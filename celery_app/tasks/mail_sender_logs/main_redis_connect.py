"""redis connection and send mail. """
import os
import json
import logging
import logging.config
import time
import yaml
import redis
from tasks.celery_queue_tasks import ZZQLowTask
from tasks.mail_sender_logs.mail_sender import send_mail
from tasks.mail_sender_logs.html_file import make_html_file
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
            os.environ["mail_alert_list"] = (
                "[\"devops@tes.media\", \"manmohan.singh@tes.media\", \"sushil.jaiswar@tes.media\"]"
                # "[\"devops@tes.media\"]"
            )
            email_list = os.getenv("mail_alert_list")
        logger.info("email list: {} \t.. {}".format(email_list, type(email_list)))
        while True:
            message = pubsub.get_message()
            if message and message['data'] is not None and not isinstance(message['data'], int):
                print("testing message-->", message["data"])
                try:
                    received_err_data = json.loads(message['data'].decode('utf-8'))
                except ValueError as e:
                    received_err_data = json.loads(
                        message['data'].decode('utf-8').replace('\'', '\"'))
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

            # #_ checking new msg attached and there is n
            time_diff = int(time.time()-self.last_seen_cnt)
            if time_diff > 60*15 and self.main_html.get('subject') is not None:
                try:
                    logger.critical("time to send mail.....{}\n\n ".format(time.asctime()))
                    logger.info(
                        "current time: {}\t--diff time: {}\t//\\>last seen time: {}\tcon:{}".format(
                            time.asctime(),
                            time_diff,
                            self.last_seen_cnt,
                            time_diff > 60*15
                        )
                    )
                    send_mail(
                        self.config_json['smtp']['credentials']['username'],
                        self.config_json['smtp']['credentials']['password'],
                        json.loads(email_list),
                        self.main_html['subject'],
                        self.main_html['newsletter_html']
                        )
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
