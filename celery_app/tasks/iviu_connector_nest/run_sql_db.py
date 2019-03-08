from pony.orm import *
from datetime import datetime
# import dpath.util
import os
import json
import time
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
                    if 'password' not in redis_conf[i]:
                        self.redis_connections[i] = redis.StrictRedis(
                                host=redis_conf[i]['host'],
                                port=redis_conf[i]['port'],
                                socket_keepalive=True)
                        # print('redis_connections1 --- {}'.format(self.redis_connections))
                    else :
                        self.redis_connections[i] = redis.StrictRedis(
                                host=redis_conf[i]['host'],
                                port=redis_conf[i]['port'],
                                password = redis_conf[i]['password'],
                                socket_keepalive=True)
                        # print('redis_connections2 --- {}'.format(self.redis_connections))

                self.redis_conn = redis.StrictRedis(
                    host=self.config_json['redis_err']['host'],
                    port=self.config_json['redis_err']['port'],
                    password=self.config_json['redis_err']['password'],
                    socket_keepalive=True)
        except (redis.ConnectionError,redis.TimeoutError) as identifier:
            pass
            # print("cant connect to db 1", identifier)

        # db.bind('mysql', host=cfg['mysql']['host'], user=cfg['mysql']['user'], password=cfg['mysql']['passwd'], db=cfg['mysql']['db'])
        self.db.bind(
            "mysql",
            host=self.config_json["mysql"]["host"],
            user=self.config_json["mysql"]["user"],
            password=self.config_json["mysql"]["passwd"],
            db=self.config_json["mysql"]["db"],
            )
        self.db.generate_mapping(create_tables=True)
        # set_sql_debug(True)

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

    def post_to_redis(self, channel, post_data):
        try:
            redis_conf = self.config_json['redis_connection']
            for i in list(redis_conf):
                self.redis_connections[i].lpush(channel,post_data)
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
        iviu_format['data'] = iviu

        if table_name == "p00390_TES":
            table_name = "p00390"
        iviu_format['table'] = table_name
        self.post_to_redis(redis_channel,json.dumps(iviu_format, default = self.myconverter))

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
        tableName = i
        print("tt in thread_each_table method",tt)
        # print('table_name', i)
        # rowcount = 1
        offset = 0
        limit = cfg['other']['limit']
        net = CheckNet()
        iviu_process = True
        while(iviu_process):
            whereClause = ""
            if len(tt) != 0:
                whereClause = " WHERE tt > '" + tt + "'"
            # sqlQuery = "SELECT * FROM iViu_data." + tableName + whereClause + " order by tt ASC LIMIT " + str(limit)
            sqlQuery = "SELECT * FROM " + self.config_json['mysql']['db'] + "." + tableName + whereClause + " order by tt ASC LIMIT " + str(limit)

            query=None
            try:
                query = self.IviuEntity.select_by_sql(sqlQuery)
                iviu_list = list(query)
                record_id = []
                for f in iviu_list:
                    # print("Timestamp:{}{}".format(f.tt, tableName) )
                    tt = f.tt.__str__()
                    record_id.append(f.id.__str__())
                    self.formatToConnector(f.to_dict(),tableName)
                    offset += limit
                # for row_id in record_id:
                    # print("row_id",row_id)
                    # self.IviuEntity.select(lambda iv: iv.id == row_id).delete(bulk=True)
                record_id = []
                # rowcount += 1
            except Exception as ex:
                iviu_process = False
                self.handle_er(net,tableName,tt)
                # print("exception in tread create table ",ex)
        else:
            self.db.rollback()
            # revoke(self.task_id, terminate=True)
            # print("process stopped for table -- {}, task id -- {}".format(tableName, self.task_id))
            time.sleep(0.001)
        self.db.rollback()
