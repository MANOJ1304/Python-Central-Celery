"""start weather data post."""
# import json
import os
import datetime
import warnings
import logging
import logging.config
import requests
from cryptography.fernet import Fernet
from tasks.celery_queue_tasks import ZZQLowTask
from tasks.weather_info_sender.utils import UtilData

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")


class WeatherData(ZZQLowTask):
    """weather data post class."""
    name = 'weather info sender.'
    description = """ send weather data to the api."""
    public = True
    autoinclude = True

    def __init__(self):
        """ initialise process start from here. """
        self.run_day = 'today'
        self.util_obj = UtilData()
        self.cnt = 0
        self.config_json = ''
        self.slack_key = ''

    def run(self, *args, **kwargs):
        """ start celery process from here. """
        # self.start_process(args[0], args[1])
        self.config_json = args[0]

        cipher_suite = Fernet(self.config_json["slack_key"].encode('utf-8'))
        ciphered_text = (
            b'gAAAAABc97Z8yWJIU1_BvHe-U9Akv0E8q0CH35i5ytLh_i_N9PNTz-HpyqLoO8smX54x6JvVv_H8ysqR'
            b'JHXvetz_ssgj25Sy3YML6KirEkIDbUtTDUhdWzed5abIdhvsxA4QYFDho_jKr21lsavoLCSo8sjYmJsB1'
            b'CsWFcDggZFeTJCPB5dY4Nk='
        )
        unciphered_text = (cipher_suite.decrypt(ciphered_text))
        self.slack_key = unciphered_text.decode("utf-8")
        # run main process
        self.start_process()
        return True

    # def setup_logging(
    #         self,
    #         default_path=os.path.join(
    #             os.path.dirname(os.path.abspath(__file__)),
    #             'config_files/logger_config.json'),
    #         default_level=logging.DEBUG,
    #         env_key='LOG_CFG'
    # ):
    #     """Setup logging configuration
    #     """
    #     path = default_path
    #     value = os.getenv(env_key, None)
    #     if value:
    #         path = value
    #     if os.path.exists(path):
    #         with open(path, 'rt') as f:
    #             config = json.load(f)
    #         logging.config.dictConfig(config)
    #     else:
    #         logging.basicConfig(level=default_level)
    def slack_alert(self, title, data):
        """ slack notification script run. """
        os.system(
            "slack-notification random \"{}\"  \"{}\" \"{}\"".format(title, data, self.slack_key))

    def start_process(self):
        """ main process start from here."""
        # self.setup_logging()
        auth_json = self.config_json['weather_api']['auth_json']
        login_api = self.config_json['weather_api']['login_api']
        new_posturl = self.config_json['weather_api']['posturl']
        post_header = self.config_json['weather_api']['post_header']
        weather_city_name_posturl = self.config_json['weather_api']['weather_city_name_posturl']
        weather_posturl = self.config_json['weather_api']['weather_posturl']
        forecast_posturl = self.config_json['weather_server']['forecast_posturl']
        forecast_key = self.config_json['weather_server']['forecast_key']

        for data_cnt, posturl in enumerate(new_posturl):
            access_token_url = posturl+login_api
            r = requests.post(access_token_url, json=auth_json, verify=False)
            if r.status_code == 200:
                auth_token = r.json()['jwt']
                print(
                    'The login status is successfull  and status code is --> {}'.format(
                        r.status_code))
            else:
                msg = "The login api is not working."
                print("\33[31m"+msg+"\33[0m")
                self.slack_alert("Error, weather Login api", msg)
                break

            headers = post_header
            headers['Authorization'] = 'Bearer ' + auth_token
            get_city_names = posturl + weather_city_name_posturl[data_cnt]
            r = requests.get(get_city_names, headers=headers, verify=False)
            try:
                city_name_list = r.json()['cities']
            except Exception as e:
                msg = (
                    "city name url: {}\t "
                    "Error is: {} \tand response.: {}").format(get_city_names, e, r.json())
                print("\33[31m"+msg+"\33[0m")
                self.slack_alert("Error, weather getting city names", msg)
                break

            city_name_list = {i.lower() for i in city_name_list}
            print("\n\n\t\t->>city name is: {}".format(city_name_list))

            post_ar = []
            for city in city_name_list:
                if city.strip():
                    if self.run_day == 'tommorrow':
                        weather_post_date = datetime.datetime.strftime(
                            datetime.date.today()+datetime.timedelta(days=1), '%Y-%m-%d')
                    elif self.run_day == 'today':
                        weather_post_date = datetime.datetime.strftime(
                            datetime.date.today(), '%Y-%m-%d')

                    try:
                        weather_url = forecast_posturl.format(forecast_key, city, weather_post_date)
                        response = requests.get(weather_url)
                        response_data = response.json()
                    except Exception as e:
                        msg = (
                            "Error is: {} \t"
                            "weather url: {} \t "
                            "city: {} ").format(e, weather_url, city)
                        print("\33[31m"+msg+"\33[0m")
                        self.slack_alert("Error, weather getting forecast api info", msg)
                        break

                    try:
                        response_data = self.util_obj.modify_weather_data(response_data)
                        post_ar.append(response_data)
                    except Exception as e:
                        msg = (
                            "Error is: {} \t"
                            "weather url: {} \t "
                            "city: {} ").format(e, weather_url, city)
                        print("\33[31m"+msg+"\33[0m")
                        self.slack_alert("Error, weather getting city name forecast api info", msg)
                        continue

            weather_api = posturl + weather_posturl
            try:
                r = requests.post(
                    weather_api, headers=headers, json=post_ar)
                # print("on cnt:{}\t data.... {}".format(self.cnt, response_data))
                # print(" weather response data\n\t\t=>   {}".format(r.json()))
            except Exception as e:
                msg = (
                    "Error info: {} \t"
                    "weather url: {} \t"
                    "api response: {} \t"
                    "city: {}").format(e, weather_api, r.json(), city_name_list)
                print("\33[31m"+msg+"\33[0m")
                self.slack_alert("Error, weather posting weather info", msg)
                break

            if r.status_code == 201:
                print(""" \33[32m Success, weather data \33[34m city=> {}, status: {}
                        cnt: {} \33[34m date: {}\33[0m""".format(
                            city_name_list, r.status_code, self.cnt, weather_post_date))
                msg = (
                    "Success, weather data city=> {} \t status: {} \t"
                    "cnt: {} \t date: {}\t api: {}").format(
                            city_name_list, r.status_code, self.cnt, weather_post_date, weather_api)
                self.slack_alert("Success, weather data post successfully", msg)
                self.cnt += 1
            else:
                msg = (
                    "The weather data unable to get posted! "
                    "Try again. json is: {} \t status code: {}\t weather_api: {}").format(
                        r.json(), r.status_code, weather_api)
                print("\33[31m"+msg+"\33[0m")
                self.slack_alert("Error, weather data unable to get posted", msg)
