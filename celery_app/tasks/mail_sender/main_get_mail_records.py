""" modify html object and send record to sender."""
import datetime
import json
import re
import random
import string
from copy import deepcopy
import requests
from tasks.celery_queue_tasks import ZZQHighTask
from tasks.mail_sender.utils import Utils
from tasks.mail_sender.db_operations import MongoRead
from tasks.mail_sender.mail_process import send_mail


class FetchRecords(ZZQHighTask):
    """ main entry for module for mail sender """
    name = 'Mail sender'
    description = """ send mail to users."""
    public = True
    autoinclude = True

    def __init__(self):
        """ class initialise pgm here."""
        self.config_json = ""
        self.util_obj = Utils()
        self.mongo_obj = MongoRead(
            self.util_obj.mongo_credential['mongo_ip'],
            self.util_obj.mongo_credential['mongo_port'],
            self.util_obj.mongo_credential['auth_user'],
            self.util_obj.mongo_credential['auth_pwd'],
            self.util_obj.mongo_credential['db_name'],
            self.util_obj.mongo_credential['collection_name']
        )

    def run(self, *args, **kwargs):
        """ run pgm here."""
        self.config_json = args[0]
        self.start_process()
        return True

    def process_data(self, guest_email_list):
        """ modifying html content for mail sender."""
        # print ("\n\nGuest records found in Response",len(api_data['_items']))
        for data in guest_email_list:
            mail_id = data['user_name']
            try:
                if not (self.mongo_obj.find_record({
                    "user_name": mail_id,
                    "cid": self.config_json['cid']
                })):
                    match = re.match(
                        '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,8})$',
                        mail_id)
                    if match is None:
                        print("Bad Syntax! {}".format(
                            mail_id))
                        raise ValueError('Bad Syntax')
                    modify_template = ""
                    modify_template = self.util_obj.log_image_newsletter.format(
                        self.util_obj.front_rest_api,
                        self.config_json['spid'],
                        self.config_json['void'],
                        self.config_json['veid'],
                        self.config_json['cid'])+self.config_json['newsletter_html']
                    replace_data = self.util_obj.browser_view_link.format(
                        self.config_json['cid'])
                    modify_template = modify_template.replace(
                        "browser-view\"",
                        "browser-view\""+replace_data
                    )
                    unsubscribe_link = " href=\"" + self.util_obj.front_rest_api
                    unsubscribe_link = unsubscribe_link + self.util_obj.unsubscribe_link.format(
                        self.config_json['spid'],
                        self.config_json['void'],
                        self.config_json['veid'],
                        self.config_json['cid'],
                        mail_id
                    )
                    modify_template = modify_template.replace(
                        "unsubscribe-mail\"",
                        "unsubscribe-mail\""+unsubscribe_link
                    )
                    print("Html template file after merging log image :=> {}\n".format(
                        modify_template))
                    # TODO:
                    send_mail(modify_template, mail_id, self.config_json)

                    # for log record
                    self.util_obj.app_log_json['data']['cid'] = self.config_json['cid']
                    requset_json = deepcopy(self.util_obj.app_log_json)
                    requset_json['data'] = json.dumps(requset_json['data'])
                    requests_body = requset_json
                    event_header = deepcopy(self.util_obj.main_header)
                    event_header["Authorization"] = "Bearer " + \
                        self.config_json['public_key']
                    print("DATA FOR LOGS", requests_body)
                    res_event_log = requests.post(
                        self.util_obj.api_appEventLogs, headers=event_header, json=requests_body)
                    if res_event_log.status_code == 201:
                        print("The app event log in is successful & status is : {}".format(
                            res_event_log.status_code))
                    else:
                        print(
                            "The app event log in is not posted & status is"
                            " : {}\tjson response :=> {}\n").format(
                            res_event_log.status_code, res_event_log.json())

                    # insert record into db
                    self.mongo_obj.insert_record(
                        {"user_name": mail_id, "cid": self.config_json['cid']}
                        )

                    # try:
                    #     self.mongo_obj.insert_record({
                    #         "user_name": mail_id,
                    #         "cid": self.config_json['cid'],
                    #         # "tag": self.config_json['filter_for_guest']["tag"]["$elemMatch"]["$eq"],
                    #         "read": 0,
                    #         "date": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    #     }
                    #     )
                    # except Exception as e:
                    #     self.mongo_obj.insert_record({
                    #         "user_name": mail_id,
                    #         "cid": self.config_json['cid'],
                    #         "read": 0,
                    #         #"tag": self.config_json['filter_for_guest'],
                    #         "date": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    #     }
                    #     )
                    # if self.cnt in self.sleep_list_cnt:
                    #     time.sleep(1800)
                    # self.cnt += 1
            except Exception as e:
                print("Error occured => {} .".format(e))

                try:
                    self.mongo_obj.insert_record(
                        {
                            "user_name": mail_id,
                            "cid": self.config_json['cid'],
                            "read": 0,
                            # "tag": self.config_json['filter_for_guest']["tag"]["$elemMatch"]["$eq"],
                            "mail_status": "Invalid email",
                            "date": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        }
                    )
                except Exception as e:
                    self.mongo_obj.insert_record(
                        {
                            "user_name": mail_id,
                            "cid": self.config_json['cid'],
                            "read": 0,
                            # "tag": self.config_json['filter_for_guest'],
                            "mail_status": "Invalid email",
                            "date": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        }
                    )

    def start_process(self):
        """ run process from here."""
        before_mail_sent_time = datetime.datetime.now()
        self.process_data(self.config_json['guests_mail_list'])
        print("__\t\trequests completes\t\t__")

        # sch_patch_data = json.dumps(self.config_json)
        scheduler_info = self.util_obj.scheduler_patch_data
        after_mail_sent_time = datetime.datetime.now()
        diff_time = after_mail_sent_time - before_mail_sent_time
        time_spliting = str(diff_time).split(":")
        h = int(time_spliting[0])
        m = int(time_spliting[1])
        utc_publish_date = datetime.datetime.strptime(
            self.config_json['utc_publish_date'].split('+')[0], "%Y-%m-%d %H:%M:%S")
        utc_time = utc_publish_date + \
            datetime.timedelta(hours=h, minutes=m) + \
            datetime.timedelta(minutes=5)
        # print(
        #     "befor_mail: {}\nAfter mail: {}\n"
        #     "diff_time: {}\n utc_time:{}\n\n").format(
        #         before_mail_sent_time,
        #         after_mail_sent_time,
        #         diff_time, utc_time
        #     )
        # d1 = datetime.datetime.now() + datetime.timedelta(hours=1,minutes=15)
        # # __   scheduler
        scheduler_info['schedule'].update({
            "year": str(utc_time.year),
            "month": str(utc_time.month),
            "day": str(utc_time.day),
            "hour": str(utc_time.hour),
            "minute": str(utc_time.minute)
        })
        # temp_ar = []
        # temp_ar.append(self.config_json)
        # temp_ar.append("config_json")
        # scheduler_info['config'] = json.dumps(temp_ar)
        scheduler_info['config'] = json.dumps(self.config_json)
        scheduler_info["job"] = self.config_json['cid']+"_newslog_tasks_" + \
            ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        # r12 = requests.post(self.util_obj.scheduler_login_api,
        #                     headers=self.util_obj.main_header, json=scheduler_info)
        # if (r12.status_code) == 201:
        #     print("Successfull posted on scheduler =>\t{}".format(r12.status_code))
        # else:
        #     print("Data Not posted on scheduler status code is=>\t{}\n\t json is :-: {}".format(
        #         r12.status_code, r12.json()))
    # __== e  ===
        print("\n\nDATA TO BE POST IN SCHEDULER:", scheduler_info)
