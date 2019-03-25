from pony.orm import *
from datetime import datetime
# import dpath.util
import os
import json
import time
import logging
import redis
import yaml
import pymysql.cursors
from celery import Celery
from tasks.celery_queue_tasks import ZZQIVIU
from tasks.iviu_connector_nest.net_connection import CheckNet
from tasks.iviu_connector_nest.send_mail import MailSender
from celery.task.control import revoke
from billiard.exceptions import WorkerLostError

config_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'yml_config.yaml')

with open(config_file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
redis_channel = cfg['redis_channel_events']


class IviuConnect(ZZQIVIU):
    """ testing Task. """
    name = 'Iviu Connector'
    description = """ It gets data from the host and  will send data to redis subscriber."""
    public = True
    autoinclude = True

    db = Database()

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def run(self, *args, **kwargs):
        """celery initialise function from here."""
        self.config_json = args[1]
        self.task_id = self.request.id
        self.temp_iviu = {
            "database":self.config_json['mysql']['db'],
            "table":"p00390",
            "type":"insert",
            "ts":1527621106,
            "xid":1784748,
            "commit":True,
            "data": ""
        }
        self.redis_conn = None
        self.redis_connections = {}
        self.net = CheckNet()
        self.retry_count = 0
        self.err_flag = False
        self.email_flag =True
        self.start()
        # print("tt in run method",args[2])
        if len(args) == 3:
            self.thread_each_table(args[0],args[2])
        else:
            self.thread_each_table(args[0], "")


    def start(self):
        self.logger.info('Started iviu connector')
        """main entry point for db connection."""
        try:
            if self.net.check_connection(cfg['other']['connection']):
                redis_conf = self.config_json['redis_connection']
                for i in list(redis_conf):
                    self.redis_connections[i] = redis.StrictRedis(
                            host=redis_conf[i]['host'],
                            port=redis_conf[i]['port'],
                            password = redis_conf[i]['password'] if "password" in redis_conf[i] else "")
                            # socket_keepalive=True)
                    # print('redis_connections2 --- {}'.format(self.redis_connections))

                self.redis_conn = redis.StrictRedis(
                    host=self.config_json['redis_err']['host'],
                    port=self.config_json['redis_err']['port'],
                    password=self.config_json['redis_err']['password'] if "password" in self.config_json['redis_err'] else "")
                    # socket_keepalive=True)
        except (redis.ConnectionError,redis.TimeoutError , WorkerLostError,Exception) as identifier:
            if self.retry_count <= 2:
                self.retry_count += 1
                time.sleep(1)
                self.start()
            # print("retry_count value:",self.retry_count,identifier)
            self.err_flag = False
            while(net.check_connection(cfg['other']['connection'])):
                if self.email_flag:
                    # print("Sending mail about redis connection lost")
                    obj = MailSender()
                    obj.send_mails("Connection lost to redis due to:"+identifier)
                    self.email_flag =False
            # exit('Failed to connect, terminating.')
                # print("cant connect to db 1", identifier)

        self.db.bind(
            "mysql",
            host=self.config_json["mysql"]["host"],
            user=self.config_json["mysql"]["user"],
            password=self.config_json["mysql"]["passwd"],
            db=self.config_json["mysql"]["db"],
            )
        self.db.generate_mapping(create_tables=True)
        set_sql_debug(False)

    class IviuEntity_Zadd(db.Entity):
        # _table_ = 'p00169'
        id = PrimaryKey(int)
        dpt = Required(int)
        tag = Required(int)
        tag2 = Optional(int)
        tag3 = Optional(int)
        mob = Required(int)
        mfp = Required(str)
        dty = Required(str)
        mfg = Required(str)
        mobtyp = Optional(str)
        tt = Required(datetime)
        pos = Required(int)
        pwr = Required(int)
        inv = Required(float)
        cnt = Required(int)
        cnf = Required(float)
        tol = Required(float)
        x = Required(float)
        y = Required(float)
        z = Required(float)
        fs = Required(int)
        utcft = Required(datetime)
        it = Required(datetime)
        unix_tt = Optional(int)

    def post_to_redis(self,tt,table_name, post_data):
        try:
            # redis_conf = self.config_json['redis_connection']
            self.err_flag = False
            # print('Reconnected redis---{}'.format(self.err_flag))
            for i in list(self.redis_connections):
                channel = redis_channel+table_name
                # print("getting tt and tablename",channel)
                self.redis_connections[i].zadd(channel,{post_data: tt})
                # self.redis_connections[i].lpush(redis_channel,post_data)
        except Exception as ex:
            self.err_flag = True
            # print ('Error:', ex)

    def myconverter(self,o):
        if isinstance(o, datetime):
            return o.__str__()

    def formatToConnector(self,iviu,table_name):
        # for i in cfg['other']['pathDict'].items():
        #     dpath.util.set(base,i[1],iviu[i])
        iviu_format = dict(self.temp_iviu)

        if table_name == "p00390_TES":
            table_name = "p00390"
        iviu_format['table'] = table_name

        #Assign unix time
        # iviu['tt'] = iviu['unix_tt']

        iviu_format['data'] = iviu
        # print("hash value of each row {}------".format(iviu_format))

        self.post_to_redis(iviu['unix_tt'],table_name,json.dumps(iviu_format, default = self.myconverter))


    def handle_er(self,net,tableName,tt):
        self.logger.info('Exception while processing handle_er function in run_sql_db --{}'.format(tableName))
        data_err = { "alarm_message": "iviu_connector_error",
        "alarm_name": tableName,
        "alarm_threshold": "60",
        "cluster_id": "None",
        "timestamp": tt,
        "veId": ""
        }
        # data = [{"from":"iviu_connector"},{"Table_name": tableName},{"Timestamp": tt}]
        while(net.check_connection(cfg['other']['connection'])):
            if self.email_flag:
                # print("Sending mail about redis connection lost 2")
                self.redis_conn.publish("OP:ERR",json.dumps(data_err))
                self.redis_conn.set("OP:BACKUP:"+tableName,tt)
                self.email_flag =False
        else:
            # print('Internet connected')
            self.db.rollback()

    @db_session()
    def thread_each_table(self, i, tt=""):
        self.logger.info('Started task for table--{}'.format(i))
        tableName = i
        # rowcount = 1
        offset = 0
        limit = cfg['other']['limit']
        net = CheckNet()
        iviu_process = True

        while(iviu_process):
            whereClause = ""
            if len(tt) != 0:
                whereClause = " WHERE tt > '" + tt + "' AND inv !='0.0'"
            sqlQuery = "SELECT *,CAST( (UNIX_TIMESTAMP(tt) * 1000) AS UNSIGNED) as unix_tt FROM " + self.config_json['mysql']['db'] + "." + tableName + whereClause + " order by tt ASC LIMIT " + str(limit)

            query=None
            try:
                query = self.IviuEntity_Zadd.select_by_sql(sqlQuery)
                iviu_list = list(query)
                for f in iviu_list:
                    if not self.err_flag:
                        tt = f.tt.__str__()
                        # print("pushing")
                        # if f in iviu_list[1:2] :
                        #     print("Timestamp:{}{}".format(f.tt, tableName) )
                        self.formatToConnector(f.to_dict(),tableName)
                    else:
                        # if f in iviu_list[1:2] :
                        #     print("Timestamp:{}{}".format(f.tt, tableName) )
                        self.formatToConnector(f.to_dict(),tableName)
                    offset += limit
                # rowcount += 1
                self.db.rollback()
            except Exception as ex:
                iviu_process = False
                self.handle_er(net,tableName,tt)
                # print("exception in tread create table ",ex)
                self.logger.error('{} table -- {} raised an error'.format(tableName,ex))
        else:
            self.db.rollback()
            # revoke(self.task_id, terminate=True)
            # print("process stopped for table -- {}, task id -- {}".format(tableName, self.task_id))
            self.logger.error('{} table raised an error'.format(tableName))
            time.sleep(0.001)
