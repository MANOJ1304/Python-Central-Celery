""" get venue name from given venue id."""
import os
import time
from datetime import datetime
import requests
from cryptography.fernet import Fernet


class ApiRequest():
    """ listen server response. """

    def __init__(self, first_url, slack_key):
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        # TODO: self.first_url = "https://api-dev.myg8way.com/api/v1"
        self.first_url = first_url
        self.login_url = "/accounts/login"
        self.venue_url = "/venueProperties/"
        self.retry_cnt = 0
        self.slack_key = slack_key

    def slack_alert(self, title, data):
        """ slack notification script run. """
        cipher_suite = Fernet(self.slack_key.encode('utf-8'))
        ciphered_text = (
            b'gAAAAABc97Z8yWJIU1_BvHe-U9Akv0E8q0CH35i5ytLh_i_N9PNTz-HpyqLoO8smX54x6JvVv_H8ysqR'
            b'JHXvetz_ssgj25Sy3YML6KirEkIDbUtTDUhdWzed5abIdhvsxA4QYFDho_jKr21lsavoLCSo8sjYmJsB1'
            b'CsWFcDggZFeTJCPB5dY4Nk='
        )
        unciphered_text = (cipher_suite.decrypt(ciphered_text))
        os.system(
            "slack-notification random \"{}\"  \"{}\" \"{}\"".format(
                title, data, unciphered_text.decode("utf-8")
            )
        )

    def get_auth_code(self):
        """step_2.1.0: for accessing jwt token. """
        # {"username":"demo_so_user@venueengage.co.za", "password":"demo9993"}

        requests_body = {
            "username": "demo_so_user@venueengage.co.za",
            "password": "demo9993"
        }
        r = requests.post(self.first_url + self.login_url, json=requests_body)
        try:
            auth_token = r.json()['jwt']
            return auth_token
        except Exception as e:
            print("Error occured !! Response auth api => {} \t retry count: {}".format(
                e, self.retry_cnt))
            time.sleep(10)
            self.retry_cnt += 1
            if self.retry_cnt == 5:
                msg = "Error, mail-alert api \tretry cnt: {} \t date: {}\t api: {}".format(
                    self.retry_cnt,
                    str(datetime.now()),
                    self.first_url + self.login_url
                )
                self.slack_alert("Error occured !!, mail sender info", msg)
                return True
            else:
                self.get_auth_code()
                return True

    def get_venue_info(self, ve_id):
        """get building id from venue. """

        venue_api = self.first_url + self.venue_url
        self.headers['Authorization'] = "Bearer " + self.get_auth_code()
        try:
            res = requests.get(venue_api, headers=self.headers)
        except Exception as e:
            msg = "Error, mail-alert venue api \t date: {}\t api: {} \t res. {}".format(
                str(datetime.now()), venue_api, res.json()+str("\n\t")+str(e))
            self.slack_alert("Error occured !!, mail sender info", msg)

        data_received = res.json()
        ve_name = data_received.get("venue_properties").get(ve_id)
        if ve_name is not None:
            ve_name = ve_name.get('NAME', None)
        print("response veneue id:: {}".format(ve_name))
        return ve_name
