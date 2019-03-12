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
from tasks.celery_queue_tasks import ZZQHighTask
from tasks.iviu_connector_nest.net_connection import CheckNet
from celery.task.control import revoke

config_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'yml_config.yaml')

with open(config_file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
redis_channel = cfg['redis_channel_events']

class IviuConnect(ZZQHighTask):
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
        self.start()
        # print("tt in run method",args[2])
        if len(args) == 3:
            self.thread_each_table(args[0],args[2])
        else:
            self.thread_each_table(args[0], "")


    def start(self):
        """main entry point for db connection."""
        try:
            if self.net.check_connection(cfg['other']['connection']):
                redis_conf = self.config_json['redis_connection']
                for i in list(redis_conf):
                    self.redis_connections[i] = redis.StrictRedis(
                            host=redis_conf[i]['host'],
                            port=redis_conf[i]['port'],
                            password = redis_conf[i]['password'] if "password" in redis_conf[i] else "",
                            socket_keepalive=True)
                    # print('redis_connections2 --- {}'.format(self.redis_connections))

                self.redis_conn = redis.StrictRedis(
                    host=self.config_json['redis_err']['host'],
                    port=self.config_json['redis_err']['port'],
                    password=self.config_json['redis_err']['password'] if "password" in self.config_json['redis_err'] else "",
                    socket_keepalive=True)
        except (redis.ConnectionError,redis.TimeoutError) as identifier:
            pass
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

    class IviuEntity(db.Entity):
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
        # unix_tt = Optional(int)

    def post_to_redis(self,tt,table_name, post_data):
        try:
            redis_conf = self.config_json['redis_connection']
            for i in list(redis_conf):
                # print("getting tt and tablename",redis_channel,self.redis_connections[i],type(post_data))
                # channel = redis_channel+table_name
                # self.redis_connections[i].zadd(channel,{post_data: tt})
                self.redis_connections[i].lpush(redis_channel,post_data)
        except Exception as ex:
            # print ('Error:', ex)
            exit('Failed to connect, terminating.')

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

        self.post_to_redis(iviu['tt'],table_name,json.dumps(iviu_format, default = self.myconverter))

    def handle_er(self,net,tableName,tt):
        data_err = { "alarm_message": "iviu_connector_error",
        "alarm_name": tableName,
        "alarm_threshold": "60",
        "cluster_id": "None",
        "timestamp": tt,
        "veId": ""
        }
        # data = [{"from":"iviu_connector"},{"Table_name": tableName},{"Timestamp": tt}]
        while(net.check_connection(cfg['other']['connection'])):
            self.redis_conn.publish("OP:ERR",json.dumps(data_err))
            self.redis_conn.set("OP:BACKUP:"+tableName,tt)
            break
        else:
            # print('Internet connected')
            self.db.rollback()

    @db_session()
    def thread_each_table(self, i, tt=""):
        # print("Attributes ---{}".format(dir(self.app.request)))
        self.logger.info('Start reading database')
        tableName = i
        # print("tt in thread_each_table method",tt)
        # print('table_name', i)
        # rowcount = 1
        offset = 0
        limit = cfg['other']['limit']
        net = CheckNet()
        iviu_process = True
        while(iviu_process):
            whereClause = ""
            if len(tt) != 0:
                whereClause = " WHERE tt > '" + tt + "' AND inv !='0.0'"
            sqlQuery = "SELECT * FROM " + self.config_json['mysql']['db'] + "." + tableName + whereClause + " order by tt ASC LIMIT " + str(limit)
            # sqlQuery = "SELECT *,CAST( (UNIX_TIMESTAMP(tt) * 1000) AS UNSIGNED) as unix_tt FROM " + self.config_json['mysql']['db'] + "." + tableName + whereClause + " order by tt ASC LIMIT " + str(limit)

            query=None
            try:
                query = self.IviuEntity.select_by_sql(sqlQuery)
                iviu_list = list(query)
                # record_id = []
                for f in iviu_list:
                    # print("Timestamp:{}{}".format(f.tt, tableName) )
                    tt = f.tt.__str__()
                    # record_id.append(f.id.__str__())
                    self.formatToConnector(f.to_dict(),tableName)
                    offset += limit
                # for row_id in record_id:
                    # print("row_id",row_id)
                    # self.IviuEntity.select(lambda iv: iv.id == row_id).delete(bulk=True)
                # record_id = []
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
        self.db.rollback()
