"""redis connection and send mail. """
import os
import json
import time
import redis
from tasks.celery_queue_tasks import ZZQLowTask
from tasks.mail_sender_logs.mail_sender import send_mail
from tasks.mail_sender_logs.html_file import make_html_file


class FetchRedisRecords(ZZQLowTask):
    """ testing Task. """
    name = 'Mail Alert'
    description = """fetch records from redis and send mail. """
    public = True
    autoinclude = True

    def __init__(self):
        self.redis_obj = None

    def run(self, *args, **kwargs):
        """celery main entry function. """
        self.config_json = args[0]
        self.sub_redis_data()
        return True

    def connect_redis(self):
        """subscribe data. """
        self.redis_obj = redis.StrictRedis(
            host=self.config_json["redis_connect"]["redis_host"],
            port=self.config_json["redis_connect"]["redis_port"],
            password=self.config_json["redis_connect"]["redis_pwd"],
            db=0
            )
        # return self.redis_obj

    def sub_redis_data(self):
        """ connect redis instance and subscribe data."""
        self.connect_redis()
        pubsub = self.redis_obj.pubsub()
        pubsub.subscribe(self.config_json["redis_connect"]["redis_key"])
        cnt = 1
        email_list = os.getenv("mail_alert_list")
        if email_list is None:
            print("Alert! email list not found. entering default emails.")
            os.environ["mail_alert_list"] = (
                "[\"devops@tes.media\"]"
            )
            email_list = os.getenv("mail_alert_list")
            print('...new email_list...', email_list)
        print("email list: {} \t.. {}".format(email_list, type(email_list)))
        while True:
            message = pubsub.get_message()
            if message and message['data'] is not None and not isinstance(message['data'], int):
                print("testing message-->", message["data"])
                try:
                    try:
                        received_err_data = json.loads(message['data'].decode('utf-8'))
                    except ValueError as e:
                        received_err_data = json.loads(
                            message['data'].decode('utf-8').replace('\'', '\"'))
                    print("cnt_->>  %d %s," % (cnt, received_err_data))
                    html_info = make_html_file(received_err_data)
                    first_name_sub = self.config_json["redis_connect"]["redis_name"]
                    html_info['subject'] = str(first_name_sub)+": "+str(html_info['subject'])
                    send_mail(
                        self.config_json['smtp']['credentials']['username'],
                        self.config_json['smtp']['credentials']['password'],
                        json.loads(email_list),
                        html_info['subject'],
                        html_info['newsletter_html']
                        )
                    # for email_record in email_list:
                    #     send_mail(
                    #         html_info['newsletter_html'],
                    #         self.config_json['smtp']['outgoing_server'],
                    #         self.config_json['smtp']['port'],
                    #         self.config_json['smtp']['credentials']['username'],
                    #         self.config_json['smtp']['credentials']['password'],
                    #         email_record,
                    #         html_info['subject'],
                    #         self.config_json['smtp']['auth_required'],
                    #         self.config_json['smtp']['reply_to']
                    #     )
                except Exception as e:
                    print("Error occurred: {} \t on data: {}\tand msg data is: {}".format(
                        e,
                        self.config_json["redis_connect"]["redis_name"],
                        message['data'])
                    )
                cnt += 1
                time.sleep(0.001)
