import redis
import json

class RedisOp(object):
    
    def __init__(self, config, e_map={}):
        self.redis_obj = redis.StrictRedis(
                            host = config['host'], 
                            port = config['port'], 
                            password = config['password'], 
                            db = config['db'],
                            decode_responses=True
                        )
        self.e_map = e_map
  
    def get_channel(self):
        ## index key OP:MON:floorindex:<sn>:<bn>:<fn>
        # smembers OP:MON:floorindex:<sn>:<bn>:<fn> 
        index_key = "OP:MON:floorindex:"+self.e_map['sn']+":"+self.e_map['bn']+":"+self.e_map['fn']
        element = self.redis_obj.smembers(index_key)
        channel = element.pop()
        return channel

    def redis_publish(self,message,publish_channel):
        redis_message = json.dumps(message)
        try:
            self.redis_obj.publish(publish_channel, redis_message)
        except Exception as e:
            # print(redis_message)
            # exit()
            pass