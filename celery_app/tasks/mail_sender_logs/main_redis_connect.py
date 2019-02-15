"""redis connection and send mail. """
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

    def redis_email_list(self):
        """get redis receipnist mail."""
        print("key exists -->> ", self.redis_obj.exists(
            self.config_json["redis_connect"]["email_receipnist_key"]))
        mail_list = self.redis_obj.lrange(
            self.config_json["redis_connect"]["email_receipnist_key"], 0, -1)
        mail_list = [x.decode('utf-8') for x in mail_list]
        # print(mail_list)
        # print("r type is: ", r.type(redis_key))
        return mail_list

    def sub_redis_data(self):
        """ connect redis instance and subscribe data."""
        self.connect_redis()
        pubsub = self.redis_obj.pubsub()
        email_list = self.redis_email_list()
        pubsub.subscribe(self.config_json["redis_connect"]["redis_key"])
        cnt = 1
        while True:
            message = pubsub.get_message()
            if message and message['data'] is not None:
                try:
                    received_err_data = json.loads(message['data'].decode('utf-8'))
                    print("cnt_->>  %d %s," % (cnt, received_err_data))
                    html_info = make_html_file(received_err_data)
                    for email_record in email_list:
                        send_mail(
                            html_info['newsletter_html'],
                            self.config_json['smtp']['outgoing_server'],
                            self.config_json['smtp']['port'],
                            self.config_json['smtp']['credentials']['username'],
                            self.config_json['smtp']['credentials']['password'],
                            email_record,
                            html_info['subject'],
                            self.config_json['smtp']['auth_required'],
                            self.config_json['smtp']['reply_to']
                        )
                except Exception as e:
                    print("error is : {} and msg data is: {}".format(e, message['data']))
                cnt += 1
                time.sleep(0.001)
