"""start weather data post."""
import json
import os
import datetime
import warnings
import logging
import logging.config
import requests
import pytz
from tasks.celery_queue_tasks import ZZQLowTask

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
        self.cnt = 0
        self.config_json = ''

    def run(self, *args, **kwargs):
        """ start celery process from here. """
        # self.start_process(args[0], args[1])
        print("hello,,,,,,weather....")
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

    def time_to_utc(self, input_date, post_tzone):
        """ convert time to utc."""
        local = pytz.timezone(post_tzone)
        local_dt = local.localize(input_date, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt

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
                exit(1)

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
                exit()

            for city in city_name_list['cities']:
                if len(city.strip()):
                    if self.run_day == 'tommorrow':
                        tommorrow_date = datetime.datetime.strftime(
                            datetime.date.today()+datetime.timedelta(days=1), '%Y-%m-%d')
                    elif self.run_day == 'today':
                        tommorrow_date = datetime.datetime.strftime(
                            datetime.date.today(), '%Y-%m-%d')

                    weather_url = forecast_posturl.format(forecast_key, city, tommorrow_date)
                    response = requests.get(weather_url)
                    response_data = response.json()

                    response_data['location']['localtime'] = response_data[
                        'location']['localtime'].strip()+':00'

                    response_data['location']['localtime_utc'] = self.time_to_utc(
                        datetime.datetime.strptime(
                            response_data['location']['localtime'],
                            "%Y-%m-%d %H:%M:%S"
                            ),
                        response_data['location']['tz_id']).strftime("%Y-%m-%d %H:%M:%S")

                    response_data['current']['last_updated'] = response_data[
                        'current']['last_updated'].strip()+':00'

                    response_data['current']['last_updated_utc'] = self.time_to_utc(
                        datetime.datetime.strptime(
                            response_data['current']['last_updated'],
                            "%Y-%m-%d %H:%M:%S"
                            ),
                        response_data['location']['tz_id']).strftime("%Y-%m-%d %H:%M:%S")

                    # for nest_data in range(len(response_data['forecast']['forecastday'][0]['hour'])):
                    #     response_data['forecast']['forecastday'][0]['hour'][nest_data]['time'] = response_data['forecast']['forecastday'][0]['hour'][nest_data]['time'].strip()+':00'
                    #     response_data['forecast']['forecastday'][0]['hour'][nest_data]['time_utc'] = self.time_to_utc(datetime.datetime.strptime(response_data['forecast']['forecastday'][0]['hour'][nest_data]['time'], "%Y-%m-%d %H:%M:%S"), response_data['location']['tz_id']).strftime("%Y-%m-%d %H:%M:%S")

                    del response_data['forecast']['forecastday'][0]['day']['uv']

                    # for cnt in range(len(response_data['forecast']['forecastday'][0]['hour'])):
                    #     del response_data[
                    #         'forecast']['forecastday'][0]['hour'][cnt]['chance_of_rain']

                    #     del response_data[
                    #         'forecast']['forecastday'][0]['hour'][cnt]['chance_of_snow']

                    weather_api = posturl + weather_posturl
                    r = requests.post(
                        weather_api, headers=headers, json=response_data, verify=False)
                    if r.status_code == 201:
                        print(
                            "The weather of {} data posted successfully on api.{}".format(
                                city, self.cnt))
                        self.cnt += 1
                    else:
                        print("The weather data unable to get posted! Try again. {}".format(
                            r.status_code))
                        exit()
