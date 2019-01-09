""" mail read and fetch undelivered mails and patch on newsletter api."""
import imaplib
import sys
import time
import datetime
import email
from email.parser import Parser
import json
import re
import dateparser
from tasks.celery_queue_tasks import ZZQLowTask
from tasks.mail_receiver_module.utils import Utils
from tasks.mail_receiver_module.db_operations import MongoRead
from tasks.mail_receiver_module.api_patch import ApiPatch

parser = Parser()


class MailReadData(ZZQLowTask):
    """ read undelivered mails."""
    name = 'mail receiver info.'
    description = """ read mail data to the api."""
    public = True
    autoinclude = True

    util_obj = Utils()
    not_delivered_mail_list = []
    all_guest_mail_list = []
    mail_recived_cnt = 0
    mail_not_recived_cnt = 0
    mail_not_opened_cnt = 0

    mongo_obj = MongoRead(
        util_obj.mongo_credential['mongo_ip'],
        util_obj.mongo_credential['mongo_port'],
        util_obj.mongo_credential['auth_user'],
        util_obj.mongo_credential['auth_pwd'],
        util_obj.mongo_credential['db_name'],
        util_obj.mongo_credential['collection_name']
    )
    # if not (self.mongo_obj.find_record({"user_name":mail_receiver_guest['user_name'],"cid":self.config_json['cid']})):

    def __init__(self):
        """initialize function """
        self.config_json = ""

    def run(self, *args, **kwargs):
        """ start celery process from here. """
        # self.start_process(args[0], args[1])
        self.config_json = args[0]
        self.start_process()
        return True

    def data_sort(self, data):
        """decoding data."""
        flag = None
        if isinstance(data, bytes):
            try:
                flag = data.decode('utf-8')
            except Exception:
                flag = data.decode('utf-16')
                # print("unicode error occured: {}".format(e))
                # print(data)
                flag = data
        else:
            flag = data
        return flag

    def rearrange_data_for_py3(self, main_data_array):
        """rearranging data."""
        main_ar = []
        nest_ar = []
        for i in main_data_array:
            if isinstance(i, tuple):
                for d2 in i:
                    new_data = self.data_sort(d2)
                    nest_ar.append(new_data)
                main_ar.insert(0,tuple(nest_ar))
            elif isinstance(i, bytes):
                new_data = self.data_sort(i)
                main_ar.append(new_data)
        return main_ar

    def start_process(self):
        """reading mail info."""
        try:
            self.config_json = json.loads(self.config_json)
        except Exception as e:
            print("Error occured: {}".format(e))
            exit()
        imap_server = self.config_json['smtp']['incoming_server']
        outlook_email = self.config_json['smtp']['credentials']['username']
        outlook_password = self.config_json['smtp']['credentials']['password']
        # FIXME:
        try:
            self.all_guest_mail_list = (self.mongo_obj.find_all(
                {"read": 0, "cid": self.config_json["cid"]}))
        except Exception as e:
            self.all_guest_mail_list = (self.mongo_obj.find_all(
                {"read": 0, "cid": self.config_json["cid"]}))
        self.mail_recived_cnt = len(self.all_guest_mail_list)

        print('>>>>>>>>:~\n'*5, "all guest mail names:-> \/")
        print(self.all_guest_mail_list)

        # # -- Download unread emails
        mail = imaplib.IMAP4_SSL(imap_server)
        (retcode, capabilities) = mail.login(outlook_email, outlook_password)
        mail.list()
        # mail.select('inbox')
        # #__ for unseen the mail.
        mail.select('Inbox', readonly=True)
        n = 0
        (retcode, messages) = mail.search(None, '(UNSEEN)')
        print(retcode)
        print('****'*27)
        check_messsage = messages[0].decode('utf-8').strip().replace(' ', '')
        if retcode == 'OK' and messages[0].decode('utf-8').strip():
            for emailid in reversed(messages[0].split()):
                new_data = None
                print('Processing ')
                n = n+1
                resp, data = mail.fetch(emailid, "(RFC822)")
                if (sys.version_info > (3, 0)):
                    new_data = self.rearrange_data_for_py3(data)
                else:
                    new_data = data
                email_body = new_data[0][1]
                # """PUT THE RAW TEXT OF YOUR EMAIL HERE"""
                try:
                    email_body_parser = parser.parsestr(email_body)
                except Exception as e:
                    print("Email parse error occured. {}\n\n".format(e))
                    continue
                # TODO: add greater than publish date.
                mail_date = email_body_parser.get('Date')
                mail_date = mail_date.replace(' ', '').replace(',', '_')[4:9]
                print(' ~ / ~ \f'*2)
                print("from mail:-> {}\t & to:-> {}\t& date:-> {}".format(
                    (email_body_parser.get('From')), email_body_parser.get('To'), mail_date))
                mail_sub = email_body_parser.get('Subject')
                print(' ~ / ~ \f'*2)
                config_date = dateparser.parse(self.config_json['utc_publish_date'])
                email_date = dateparser.parse(email_body_parser.get('Date').split(' (')[0])
                if email_date is None:
                    email_date = datetime.datetime.now()
                print(config_date, '\t\tconfig_date')
                print(email_date, '\t\email_date\t', email_body_parser.get('Date'))
                if email_date < config_date:
                    print(
                        "The given date is less than publish date."
                        " So, escaping all previous mails.\n\n")
                    break
                # Delivery Status Notification (Failure)
                if 'fail' in mail_sub.lower():
                    print(mail_sub)
                    m = email.message_from_string(email_body)
                    if m.get_content_maintype() != 'multipart':
                        continue
                    for part in m.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True)
                            body_text = body.decode("utf-8")
                            if body_text.strip() != '':
                                # # -- multiple email address
                                not_delivered_mail_list = re.findall(
                                    r'[\w\.-]+@[\w\.-]+', body_text)
                                print("web api not_delivered_mail_list :-) {}".format(
                                    not_delivered_mail_list))
                    if not_delivered_mail_list:
                        for del_mail in not_delivered_mail_list:
                            # print("-->\t\tnot delivered mail list::\t",del_mail)
                            cond_mail = del_mail not in self.not_delivered_mail_list
                            if del_mail in self.all_guest_mail_list and cond_mail:
                                mail.select('inbox')
                                mail.fetch(emailid, "(RFC822)")
                                print('..~..~..{} Seen current mail sub.: {} .Done!'.format(
                                    del_mail, mail_sub))
                                self.not_delivered_mail_list.append(del_mail)
                                self.mail_not_recived_cnt += 1
                                self.mail_recived_cnt -= 1
                    # ##!!!!!!!
                    # print('..~..~.. Converting to Seen mail.')
                    # mail.select('inbox')
                    # mail.fetch(emailid, "(RFC822)")
                    # print('..~..~.. Seen current mail sub.: {} .Done!'.format(mail_sub))
                    # ##!!!!!!!

        time.sleep(2)
        news_patch_json = {
                            "mail_recived": self.mail_recived_cnt,
                            "mail_not_recived": self.mail_not_recived_cnt,
                            "mail_not_opened": self.mail_recived_cnt,
                            "campaign_id": self.config_json["cid"],
                            "total_mail_sent": len(self.all_guest_mail_list)
        }
        print("\t=>\t\t{}".format(news_patch_json))
        api_patch_obj = ApiPatch(self.config_json, self.not_delivered_mail_list, news_patch_json)
        api_patch_obj.patch_data()
        api_patch_obj.patch_newsletter()
        print("\t~+~\t~+~\t patching db read data to 1 ")
        update_data = self.mongo_obj.insert_many({"cid": self.config_json["cid"]}, {"read": 1})
        print("updated read flag data on db->  {}".format(update_data))
        # self.mongo_obj.insert_many(data_condition, update_record)
        print("\t~+~\t~+~\t The data is given here and ///////////////////"*5)
