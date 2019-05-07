"""start weather data post."""
import json
import os
import time
import datetime
import warnings
import logging
import logging.config
import requests
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

    def run(self, *args, **kwargs):
        """ start celery process from here. """
        # self.start_process(args[0], args[1])
        self.config_json = args[0]
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
                print("The login api is not working.")

            headers = post_header
            headers['Authorization'] = 'Bearer ' + auth_token
            get_city_names = posturl + weather_city_name_posturl[data_cnt]
            r = requests.get(get_city_names, headers=headers, verify=False)
            city_name_list = r.json()
            print("\n\n\t\t->>city name is: {}".format(city_name_list))
            try:
                city_name_list['cities']
            except Exception as e:
                print("Error occured while getting cities name: {} \tand resp.: {}".format(
                    e,
                    city_name_list
                    ))
                print("get city name url: {}".format(get_city_names))

            for city in city_name_list['cities']:
                if len(city.strip()):
                    if self.run_day == 'tommorrow':
                        tommorrow_date = datetime.datetime.strftime(
                            datetime.date.today()+datetime.timedelta(days=1), '%Y-%m-%d')
                    elif self.run_day == 'today':
                        tommorrow_date = datetime.datetime.strftime(
                            datetime.date.today(), '%Y-%m-%d')

                    try:
                        weather_url = forecast_posturl.format(forecast_key, city, tommorrow_date)
                        response = requests.get(weather_url)
                        response_data = response.json()
                    except Exception as e:
                        print(
                            "\33[31m Error occurred during getting weather"
                            " info: {} \n weather url: {} \n api response: {}\n city: {} \33[0m"
                        ).format(e, weather_url, response, city)

                    response_data = self.util_obj.modify_weather_data(response_data)
                    weather_api = posturl + weather_posturl
                    r = requests.post(
                        weather_api, headers=headers, json=response_data, verify=False)
                    # print("on cnt:{}\t data.... {}".format(self.cnt, response_data))
                    # print(" weather response data\n\t\t=>   {}".format(r.json()))

                    if r.status_code == 201:
                        print(
                            "Success, weather data post of city: \'{}\', status: {} cnt: {}".format(
                                city, r.status_code, self.cnt))
                        self.cnt += 1
                    else:
                        print(
                            "\33[31m The weather data unable to get"
                            "posted! Try again. json: {} {} \33[0m").format(r.json(), r.status_code)
                time.sleep(2)
