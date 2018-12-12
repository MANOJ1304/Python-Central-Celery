""" patch all data records. """
import json
import requests
from tasks.monitoring.utils import UtilData


class DataPatch(object):
    def __init__(self):
        self.util_obj = UtilData()
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

    def get_record_id(self, jwt_token, record):
        """ fetch record id from api for patching the record data."""
        try:
            api_url = self.util_obj.first_url + self.util_obj.get_record_url.format(
                record['belongs']['owner']['spId'],
                record['belongs']['owner']['voId'],
                record['belongs']['owner']['veId'],
                record['profile']['user_apps']['sdlm']['quiz'],
                record['profile']['user_id']
                )
        except Exception as e:
            print("error occurred. {} ".format(e))
            api_url = None
        headers = self.util_obj.headers
        headers['Authorization'] = 'Bearer {}'.format(jwt_token)
        if api_url is not None:
            res = requests.get(api_url, headers=headers)
            return res.json()
        else:
            return None

    def patch_record(self, jwt_token, record):
        """ patch record after getting api id from api."""
        received_api_record = self.get_record_id(jwt_token, record)
        print(received_api_record)
        if received_api_record is not None:
            patch_url = self.util_obj.first_url + self.util_obj.patch_record_url.format(
                record['belongs']['owner']['spId'],
                record['belongs']['owner']['voId'],
                record['belongs']['owner']['veId'],
                received_api_record['_id']
            )
            headers = self.util_obj.headers
            headers['Authorization'] = 'Bearer {}'.format(jwt_token)
            try:
                data = {}
                data['type'] = record['properties']['user_sub_type']
                data['areas_visited'] = received_api_record['areas_visited']
                temp_json = {}
                temp_json['device_id'] = record['device']['device_id']
                temp_json['device_status'] = record['device']['status']
                data['areas_visited'].append = temp_json
                patch_data = json.dumps(data)
                res = requests.patch(patch_url, headers=headers, data=patch_data)
                print("the patch status is: {}\tthe response is: {}".format(
                    res.status_code, res.json()))
            except Exception as e:
                print("Error occured while patching record. {}".format(e))
