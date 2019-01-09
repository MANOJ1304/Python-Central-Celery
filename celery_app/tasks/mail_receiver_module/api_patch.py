""" patch newsletter api records."""
import json
import requests
from tasks.mail_receiver_module.utils import Utils


class ApiPatch():
    """patch newsletter records."""

    def __init__(self, json_data, not_delivered_mail_list, news_patch_json):
        """intialise data."""
        self.util_obj = Utils()
        self.json_data = json_data
        self.not_delivered_mail_list = not_delivered_mail_list
        self.news_patch_json = news_patch_json

    def get_auth_code(self):
        """ for jwt token"""
        requests_body = {
            "username": self.util_obj.login_username,
            "password": self.util_obj.login_password
        }
        r = requests.post(
            self.util_obj.front_rest_api+self.util_obj.login_rest_api, json=requests_body)
        try:
            auth_token = r.json()['jwt']
            return auth_token
        except Exception as e:
            print("Response auth api => {}".format(e))
            return None

    def patch_data(self):
        """patch campaign on guests api for invalid email address."""
        auth_code = self.get_auth_code()
        headers = {"Authorization": "Bearer {}"}
        headers["Authorization"] = headers["Authorization"].format(auth_code)
        headers.update(self.util_obj.main_header)
        for mail_name in self.not_delivered_mail_list:
            api_process = self.util_obj.front_rest_api+self.util_obj.end_rest_api.format(
                self.json_data['spid'],
                self.json_data['void'],
                self.json_data['veid'],
                self.util_obj.api_name,
                mail_name)
            r1 = requests.patch(
                api_process, headers=headers, data=json.dumps(self.util_obj.patch_data))
            if r1.status_code == 200:
                print("The patch successful and status code is :_> {}".format(r1.status_code))
            else:
                print("The patch failed and status code is :_> {} and json is {}".format(
                    r1.status_code, r1.json()))

    def patch_newsletter(self):
        """ patch newsletter log on guests api for invalid email address."""
        auth_code = self.get_auth_code()
        headers = {"Authorization": "Bearer {}"}
        headers["Authorization"] = headers["Authorization"].format(auth_code)
        headers.update(self.util_obj.main_header)
        cid = {"campaign_id": self.news_patch_json['campaign_id']}
        api_process = self.util_obj.front_rest_api+self.util_obj.list_end_rest_api.format(
            self.json_data['spid'],
            self.json_data['void'],
            self.json_data['veid'],
            self.util_obj.news_api_name,
            json.dumps(cid))
        try:
            get_data = requests.get(api_process, headers=headers)
            if not get_data.json()['_items']:
                patch_record = json.dumps(self.news_patch_json)
                r1 = requests.post(api_process, headers=headers, data=patch_record)
                if r1.status_code == 201:
                    print(
                        "\nThe post successful and status code is :_> {}\n".format(r1.status_code))
                else:
                    print(
                        "\nThe post failed and"
                        " status code is :_> {} and json is {}\n"
                    ).format(r1.status_code, r1.json())
            else:
                patch_id = get_data.json()['_items'][0]['_id']
                api_process = api_process.split("?where")
                r1 = requests.patch(
                    api_process[0]+'/'+patch_id,
                    headers=headers,
                    data=json.dumps(self.news_patch_json)
                )
                if r1.status_code == 200:
                    print("\nThe newsletter patch successful and status code is :_> {}\n".format(
                        r1.status_code))
                else:
                    print(
                        "\nThe newsletter log patch failed "
                        "and status code is :_> {} and json is {}\n"
                    ).format(r1.status_code, r1.json())
        except Exception as e:
            print("Error Occured:.>> {}".format(e))
