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
redis_channel = cfg['redis']['redis_channel_events']


class IviuConnect(ZZQHighTask):
    """ testing Task. """
    name = 'Iviu Connector'
    description = """ It gets data from the host and  will send data to redis subscriber."""
    public = True
    autoinclude = True
    net = CheckNet()

    def run(self, *args, **kwargs):
        """celery initialise function from here."""
        self.task_id = self.request.id
        self.thread_each_table(args[0])
        self.temp_iviu = {
            "database":"iViu_data",
            "table":"p00390",
            "type":"insert",
            "ts":1527621106,
            "xid":1784748,
            "commit":True,
            "data": ""
        }

    try:
        if net.check_connection(cfg['other']['connection']):
            # conn = redis.StrictRedis(
            #     host=cfg['redis']['host'],
            #     port=cfg['redis']['port'],
            #     socket_keepalive=True)

            redis_conn = redis.StrictRedis(
                host=cfg['redis']['host'],
                port=cfg['redis']['port'],
                password=cfg['redis']['password'],
                socket_keepalive=True)
    except (redis.ConnectionError,redis.TimeoutError) as identifier:
        pass
        # print("cant connect to db 1", identifier)

    db = Database()
    db.bind('mysql', host=cfg['mysql']['host'], user=cfg['mysql']['user'], password=cfg['mysql']['passwd'], db=cfg['mysql']['db'])
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

    db.generate_mapping(create_tables=True)


    def post_to_redis(self,channel,post_data):
        try:
            self.redis_conn.lpush(channel,post_data)
        except Exception as ex:
            # print ('Error:', ex)
            exit('Failed to connect, terminating.')

    def myconverter(self,o):
        if isinstance(o, datetime):
            return o.__str__()

    def formatToConnector(self,iviu,table_name):
        # for i in cfg['other']['pathDict'].items():
        #     dpath.util.set(base,i[1],iviu[i[0]])
        iviu_format = dict(self.temp_iviu)
        iviu_format['data'] = iviu
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
            break
        else:
            # print('Internet connected')
            self.db.rollback()

    @db_session()
    def thread_each_table(self, i):
        # print("Attributes ---{}".format(dir(self.app.request)))
        tableName = ""
        tt = ""
        # print('table_name', i)
        if "iviuentity*" not in i[0]:
            if "." not in i[0]:
                tableName = i
            else:
                tableName = i.split('.')[1]
        rowcount = 1
        offset = 0
        limit = cfg['other']['limit']
        net = CheckNet()
        iviu_process = True
        while(iviu_process):
            whereClause = ""
            if len(tt) != 0:
                whereClause = " WHERE tt > '" + tt + "'"
            sqlQuery = "SELECT * FROM iViu_data." + tableName + whereClause + " order by tt ASC LIMIT " + str(limit)
            query=None
            try:
                query = self.IviuEntity.select_by_sql(sqlQuery)
                iviu_list = list(query)
                for f in iviu_list:
                    # print("Timestamp:{}{}".format(f.tt, tableName) )
                    tt = f.tt.__str__()
                    self.formatToConnector(f.to_dict(),tableName)
                    offset += limit

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
