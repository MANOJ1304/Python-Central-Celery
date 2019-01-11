"""fetching devices info from api and redis and patching to redis. """

import json
import requests
import redis
from tasks.celery_queue_tasks import ZZQLowTask
from tasks.blacklist_info_checker.utils import UtilData


class BlackListDevices(ZZQLowTask):
    """ fetching blacklist devices class."""
    name = 'black list device checker.'
    description = """ get black list devices info and update redis."""
    public = True
    autoinclude = True

    def __init__(self):
        self.util_obj = UtilData()
        self.config_json = None

    def run(self, *args, **kwargs):
        """celery process start from here. """
        # self.start_process(args[0], args[1])
        self.config_json = args[0]
        self.start_process()
        return True

    def get_blacklist_devices_from_api(self, filter_data):
        """fetching blacklist record from api. """
        black_list_mac_adderess = []
        user_credential = {
            "username": self.config_json['user'],
            "password": self.config_json['password']
        }
        # get aut token
        r1 = requests.post(
            self.util_obj.urls['login'],
            json=user_credential,
            headers=self.util_obj.api['default_header']
        )
        auth_token = r1.json()['jwt']
        self.util_obj.api['default_header']["Authorization"] = "Bearer"+" {}".format(auth_token)

        def get_mac_address(temp_list):
            for rec in temp_list:
                black_list_mac_adderess.append(rec['mac'])

        payload = {'where': json.dumps(filter_data), 'max_results': 50}
        r2 = requests.get(
            self.util_obj.urls['devices'],
            headers=self.util_obj.api['default_header'],
            params=payload
        )
        l_next = r2.json()['_links'].keys()
        # print("l_next...=>  ", l_next)

        if 'next' not in l_next:
            get_mac_address(r2.json()['_items'])

        page_no = 1
        while "next" in l_next:
            page_no += 1
            payload.update({'page': page_no})
            r3 = requests.get(
                self.util_obj.urls['devices'],
                headers=self.util_obj.api['default_header'],
                params=payload
            )
            get_mac_address(r3.json()['_items'])
            # print(r3.json()['_meta']['page'])
            l_next = r3.json()['_links'].keys()

        return black_list_mac_adderess

    def start_process(self):
        """ main process start """

        r = redis.Redis(
            host=self.util_obj.redis['host'],
            port=self.util_obj.redis['port']
        )
        for k, v in self.config_json['redis_set_keys_with_filter'].items():
            # fetching records from redis
            new_redis_black_list = [i.decode("utf-8") for i in r.smembers(k)]
            print("\n..\t redis black list....=> {}".format(new_redis_black_list))

            api_mac_record_list = self.get_blacklist_devices_from_api(v)
            print("\n..\t mac api record list....=> {}".format(api_mac_record_list))
            # get difference of (api - redis) for adding difference to redis.
            api_redis_diff = set(api_mac_record_list) - set(new_redis_black_list)
            print("api_redis set diff. -> {}".format(api_redis_diff))
            if api_redis_diff:
                add_record_redis = r.sadd(k, *api_redis_diff)
                print("adding record to redis: {}".format(add_record_redis))

            # get difference of (redis - api) for removing records to redis.
            redis_api_diff = set(new_redis_black_list) - set(api_mac_record_list)
            print("\n... redis and api difference is :-> {}".format(redis_api_diff))
            if redis_api_diff:
                remove_redis_val = r.srem(k, *redis_api_diff)
                print("Total removed record from redis: {}".format(remove_redis_val))
