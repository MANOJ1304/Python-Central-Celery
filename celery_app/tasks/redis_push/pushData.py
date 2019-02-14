from tasks.celery_queue_tasks import ZZQHighTask
import yaml
import os
import redis

class DataPush(ZZQHighTask):
    """ testing Task. """
    name = 'Data Push'
    description = """ Get data from api and push it to Redis."""
    public = True
    autoinclude = True

    def run(self, *args, **kwargs):
        self.pushto_redis(args[0], args[1])

    def pushto_redis(self, dataKey, dataValues):
            with open(os.getcwd()+'/tasks/redis_push/parameters.yaml', 'r') as ymlfile:
                cfg = yaml.load(ymlfile)
                conn = redis.StrictRedis(host=cfg['redis']['host'], port=cfg['redis']['port'])

            if dataKey == 'DEVICES':
                dataFormat = cfg['REDIS_KEYS'][dataKey] + dataValues['voId'] + ':'+ dataValues['device_type'] +'<'+ dataValues['sensor_id'] + '>'

                print(dataFormat)
            elif dataKey == 'SENSOR':
                dataFormat = cfg['REDIS_KEYS'][dataKey] + dataValues['sensor_id']

                print(dataFormat)
            elif dataKey == 'PARAMETERS':
                dataFormat = cfg['REDIS_KEYS'][dataKey] + dataValues['veId']
                print(dataFormat)

            elif dataKey == 'AREA':
                dataFormat = cfg['REDIS_KEYS'][dataKey] + dataValues['veId']+":"+dataValues['area_id']
                print(dataFormat)

            conn.hmset(dataFormat,dataValues)
        # print('sum of a+b is: {}'.format(a+b))
        # print('--:-- '*20)
