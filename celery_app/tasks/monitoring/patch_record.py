""" patch all data records. """
import json
import requests
from datetime import datetime
from tasks.monitoring.utils import UtilData


class DataPatch(object):
    def __init__(self):
        self.util_obj = UtilData()
        self.get_url = None
        # self.api_output = {
        #     "type": "student",
        #     "alias_id": "412312 Student_ID, staff ID",
        #     "cod_pin": "222222",
        #     "name": "Sushil Jaiswar ",
        #     "email": "",
        #     "mobile_number": "",
        #     "classification_rule": "fixed",
        #     "start_dt": "2017-12-21 11:00:27",
        #     "end_dt": "2017-12-21 11:00:27",
        #     "wifi_devices": 2,
        #     "presence_devices": 2,
        #     "status": "fully_attended",
        #     "areas_visited": [
        #         {
        #             "area": "class1",
        #             "device_id": "aa:bb:cc:dd:ee:ff",
        #             "device_status": "",
        #             "start_dt": "2017-12-21 11:00:27",
        #             "end_dt": "2017-12-21 11:00:27"
        #         }
        #     ]
        #     }

    def get_record_id(self, jwt_token, config_json, record):
        """ fetch record id from api for patching the record data."""
        try:
            self.get_url = self.util_obj.first_url + config_json['api_data']['attendees_api']
            if 'user_apps' in record['profile'].keys():
                # print(record['profile']['user_apps']['sdlm']['quiz'])
                # print(config_json['query']['cod_pin'])
                if str(record['profile']['user_apps']['sdlm']['quiz']) == str(config_json['query']['cod_pin']):
                    api_url = self.get_url + self.util_obj.get_record_url.format(
                        config_json['query']['cod_pin'],
                        record['profile']['user_id']
                        )
                    # print ("GET URL",api_url)
                    # api_url = self.util_obj.first_url + self.util_obj.get_record_url.format(
                    #     record['belongs']['owner']['spId'],
                    #     record['belongs']['owner']['voId'],
                    #     record['belongs']['owner']['veId'],
                    #     record['profile']['user_apps']['sdlm']['quiz'],
                    #     record['profile']['user_id']
                    #     )
                else:api_url = None
            else:api_url = None

        except Exception as e:
            # print("error occurred. {} ".format(e))
            api_url = None
        headers = self.util_obj.headers
        headers['Authorization'] = 'Bearer {}'.format(jwt_token)
        if api_url is not None:
            res = requests.get(api_url, headers=headers)
            return res.json()
        else:
            return {'_items':[{}]}

    def convert_to_datetime(self, data):
        """ convert api datetime to datetime object."""
        return data.replace("T", ' ').replace('t', ' ')

    def patch_record(self, jwt_token, config_json, record):
        """ patch record after getting api id from api."""
        received_api_record = self.get_record_id(jwt_token, config_json, record)['_items'][0]
        if received_api_record:
            # patch_url = self.util_obj.first_url + self.util_obj.patch_record_url.format(
            #     record['belongs']['owner']['spId'],
            #     record['belongs']['owner']['voId'],
            #     record['belongs']['owner']['veId'],
            #     received_api_record['_id']
            # )
            patch_url = self.get_url + '/' + received_api_record['_id']
            headers = self.util_obj.headers
            headers['Authorization'] = 'Bearer {}'.format(jwt_token)
            try:
                data = {}
                data['type'] = record['properties']['user_sub_type']
                data['areas_visited'] = [{}]
                data['areas_visited'][0]['device_id'] = record['device']['device_id']
                data['areas_visited'][0]['device_status'] = record['device']['status']
                data['areas_visited'][0]['start_dt'] = self.convert_to_datetime(
                    record['properties']['start_ts'])
                data['areas_visited'][0]['end_dt'] = self.convert_to_datetime(
                    record['properties']['last_ts'])
                data['areas_visited'][0]['last_seen'] = record['device']['last_seen']
                patch_data = json.dumps(data)
                # print("patch data is: {}".format(patch_data))
                res = requests.patch(patch_url, headers=headers, data=patch_data)
                print("the patch status is: {}\tthe response is: {}".format(
                    res.status_code, res.json()))
            except Exception as e:
                print("Error occured while patching record. {}".format(e))
