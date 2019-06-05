"""redis connection and send mail. """
import os
import json
import logging
import logging.config
import time
from datetime import datetime
import yaml
import redis
from tasks.celery_queue_tasks import ZZQLowTask
from tasks.mail_alert_celery.mail_sender import send_mail
from tasks.mail_alert_celery.html_file import make_html_file
logger = logging.getLogger(__name__)


class FetchRedisRecords(ZZQLowTask):
    """ testing Task. """
    name = 'Mail Alert'
    description = """fetch records from redis and send mail. """
    public = True
    autoinclude = True

    def __init__(self):
        self.redis_obj = None
        self.config_json = None
        self.main_html = {'newsletter_html': ''}
        self.last_seen_cnt = time.time()
        self.setup_logging(default_level=logging.DEBUG)

    def run(self, *args, **kwargs):
        """celery main entry function. """
        self.config_json = args[0]
        self.sub_redis_data()
        return True

    def setup_logging(
            self,
            default_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'config_files/logging.yaml'
            ),
            default_level=logging.INFO,
            env_key='LOG_CFG'
    ):
        """Setup logging configuration
        """
        path = default_path
        value = os.getenv(env_key, None)
        if value:
            path = value
        if os.path.exists(path):
            with open(path, 'rt') as f:
                # config = json.load(f)  # for json
                config = yaml.safe_load(f.read())  # for yaml
            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)

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
            logger.critical("Alert! email list not found. entering default emails.")

            email_list = self.config_json["mail_sender_list"]
        logger.info("email list: {} \t.. {}".format(email_list, type(email_list)))
        mail_msg_cnt = 0
        while True:
            message = pubsub.get_message()
            if message and message['data'] is not None and not isinstance(message['data'], int):
                print("received subscribed message--> {}".format(message["data"]))
                try:
                    received_err_data = json.loads(message['data'].decode('utf-8'))
                except ValueError as e:
                    try:
                        received_err_data = json.loads(
                            message['data'].decode('utf-8').replace('\'', '\"'))
                    except Exception as er:
                        logger.error("Unknown Error occurred for message:{}\n\t error is {}".format(
                            message["data"], er))
                        continue
                print("cnt_->>  %d %s," % (cnt, received_err_data))
                html_info = make_html_file(received_err_data)
                first_name_sub = self.config_json["redis_connect"]["redis_name"]
                # html_info['subject'] = str(first_name_sub)+": "+str(html_info['subject'])
                logger.info(
                    "current time: {}\t--diff time: {}\t//\\>last seen time: {}\tcon:{}".format(
                        time.asctime(),
                        time.time()-self.last_seen_cnt,
                        self.last_seen_cnt,
                        (time.time()-self.last_seen_cnt) > 60*15
                    )
                )
                # html_info['subject'] = str(first_name_sub)+": "+str(html_info['subject'])
                self.main_html['subject'] = str(first_name_sub)+": "+str(html_info['subject'])
                self.main_html['newsletter_html'] += html_info['newsletter_html']
                mail_msg_cnt += 1
            # #_ checking new msg attached and there is n
            time_diff = int(time.time()-self.last_seen_cnt)
            if time_diff > 60*15 and self.main_html.get('subject') is not None:
                mail_body = """\n<h2><font color=\"red\">
                    Total alerts received: {}</font></h2>\n""".format(mail_msg_cnt) +\
                    self.main_html['newsletter_html']
                try:
                    # redis monitoring task.
                    redis_monitoring_dict = {
                        "timestamp": str(datetime.now()),
                        "count": mail_msg_cnt
                        }
                    rec_data = self.redis_obj.get("OP:ERR:SUMMARY")
                    logger.info("redis_monitoring_dict: {}\t\t type: {}\n##".format(
                        redis_monitoring_dict, type(redis_monitoring_dict)))

                    if rec_data is None:
                        first_red_data = []
                        first_red_data.append(redis_monitoring_dict)
                        final_rec_data = json.dumps(first_red_data)
                    elif isinstance(rec_data, bytes):
                        rec_data = json.loads(rec_data.decode("utf-8"))
                        if isinstance(rec_data, list):
                            rec_data.append(redis_monitoring_dict)
                        else:
                            logger.info(
                                "redis record is not list type.. "
                                "rec_data: {}\t type is: {}").format(rec_data, type(rec_data))
                            rec_data = [json.dumps(redis_monitoring_dict)]
                        final_rec_data = json.dumps(rec_data[-10:])
                    self.redis_obj.set("OP:ERR:SUMMARY", final_rec_data)

                    logger.critical("time to send mail.....{}\n\n ".format(time.asctime()))
                    logger.info(
                        "current time: {}\t--diff time: {}\t//\\>last seen time: {}\tcon:{}".format(
                            time.asctime(),
                            time_diff,
                            self.last_seen_cnt,
                            time_diff > 60*15
                        )
                    )
                    # json.loads(email_list),
                    send_mail(
                        self.config_json['smtp']['credentials']['username'],
                        self.config_json['smtp']['credentials']['password'],
                        email_list,
                        self.main_html['subject'],
                        mail_body
                        )
                    mail_msg_cnt = 0
                    logger.info("reassigning last_seen_cnt and main_html to default values.")
                    # resetting time to current time
                    self.last_seen_cnt = time.time()
                    self.main_html = {'newsletter_html': ''}
                    cnt += 1
                    time.sleep(0.001)
                except Exception as e:
                    print("Error occurred: {} \t on data: {}\tand msg data is: {}".format(
                        e,
                        self.config_json["redis_connect"]["redis_name"],
                        message['data']
                        ))
