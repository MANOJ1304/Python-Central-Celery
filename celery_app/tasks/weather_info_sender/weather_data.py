"""start weather data post."""
# import json
# import os
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
            try:
                city_name_list = r.json()['cities']
            except Exception as e:
                print("Error occured while getting cities name: {} \tand resp.: {}".format(
                    e, city_name_list))
                # TODO: send alert!
                print("get city name url: {}".format(get_city_names))

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
                        print(
                            """\33[31m Error occurred during getting weather info: {}
                            weather url: {} \n api response: {}\n city: {}
                            \33[0m """.format(e, weather_url, response, city))
                        # TODO: send alert!

                    response_data = self.util_obj.modify_weather_data(response_data)
                    post_ar.append(response_data)

            weather_api = posturl + weather_posturl
            try:
                r = requests.post(
                    weather_api, headers=headers, json=post_ar, verify=False)
                # print("on cnt:{}\t data.... {}".format(self.cnt, response_data))
                # print(" weather response data\n\t\t=>   {}".format(r.json()))
            except Exception as e:
                print(
                    """\33[31m Error occurred while posting weather info: {}
                        \n weather url: {}
                        \n api response: {}
                    \n city: {} \33[0m """.format(e, weather_api, post_ar, city_name_list))
                # TODO: send alert!

            if r.status_code == 201:
                print(""" \33[32m Success, weather data \33[34m city=> {}, status: {}
                        cnt: {} \33[34m date: {}\33[0m""".format(
                            city_name_list, r.status_code, self.cnt, weather_post_date))
                self.cnt += 1
            else:
                print("""\33[31m The weather data unable to get posted!
                    Try again. json: {} {} \33[0m """.format(
                        r.json(), r.status_code))
                # TODO: send alert!
