""" common medhods will remain here.
    we are adding weather key and values data manually because weather data they are using
    added new keys.so it gives error to the weathre api while posting.
"""
import datetime
import pytz
from copy import deepcopy


class UtilData(object):
    """ constant values kept here. """

    def time_to_utc(self, input_date, post_tzone):
        """ convert time to utc."""
        local = pytz.timezone(post_tzone)
        local_dt = local.localize(input_date, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt

    def hourly_weather_data(self, api_hour_data):
        """ get hourly weather data. """
        temp_data = []
        for hour_info in api_hour_data:
            h_json = {
                "condition": {}
            }
            h_json['time_epoch'] = hour_info['time_epoch']
            h_json['time'] = hour_info['time']+":00"
            h_json['temp_c'] = hour_info['temp_c']
            h_json['temp_f'] = hour_info['temp_f']
            h_json['is_day'] = hour_info['is_day']
            h_json['condition']['text'] = hour_info['condition']['text']
            h_json['condition']['icon'] = hour_info['condition']['icon']
            h_json['condition']['code']= hour_info['condition']['code']
            h_json['wind_mph'] = hour_info['wind_mph']
            h_json['wind_kph'] = hour_info['wind_kph']
            h_json["wind_degree"] = hour_info["wind_degree"]
            h_json["wind_dir"] = hour_info["wind_dir"]
            h_json["pressure_mb"] = hour_info["pressure_mb"]
            h_json["pressure_in"] = hour_info["pressure_in"]
            h_json["precip_mm"] = hour_info["precip_mm"]
            h_json["precip_in"] = hour_info["precip_in"]
            h_json["humidity"] = hour_info["humidity"]
            h_json["cloud"] = hour_info["cloud"]
            h_json["feelslike_c"] = hour_info["feelslike_c"]
            h_json["feelslike_f"] = hour_info["feelslike_f"]
            h_json["windchill_c"] = hour_info["windchill_c"]
            h_json["windchill_f"] = hour_info["windchill_f"]
            h_json["heatindex_c"] = hour_info["heatindex_c"]
            h_json["heatindex_f"] = hour_info["heatindex_f"]
            h_json["dewpoint_c"] = hour_info["dewpoint_c"]
            h_json["dewpoint_f"] = hour_info["dewpoint_f"]
            h_json["will_it_rain"] = hour_info["will_it_rain"]
            h_json["will_it_snow"] = hour_info["will_it_snow"]
            h_json["vis_km"] = hour_info["vis_km"]
            h_json["vis_miles"] = hour_info["vis_miles"]
            h_json["gust_mph"] = hour_info["gust_mph"]
            h_json["gust_kph"] = hour_info["gust_kph"]

            temp_data.append(deepcopy(h_json))
        return temp_data

    def modify_weather_data(self, api_weather_data):
        """ modify weather response data."""
        weather_schema = {
            "location": {},
            "current": {
                "condition": {},
            },
            "forecast": {
                "forecastday": [
                    {
                        "day": {
                            "condition": {
                                "text": "Partly cloudy",
                                "icon": "//cdn.apixu.com/weather/64x64/day/116.png",
                                "code": 1003
                            }
                        },
                        "astro": {},
                        "hour": []
                    }
                ]
            }
        }

        weather_schema['location']['name'] = api_weather_data['location']['name']
        weather_schema['location']['region'] = api_weather_data['location']['region']
        weather_schema['location']['country'] = api_weather_data['location']['country']
        weather_schema['location']['lat'] = api_weather_data['location']['lat']
        weather_schema['location']['lon'] = api_weather_data['location']['lon']
        weather_schema['location']['tz_id'] = api_weather_data['location']['tz_id']
        weather_schema['location'][
            'localtime_epoch'] = api_weather_data['location']['localtime_epoch']
        weather_schema['location'][
            'localtime'] = api_weather_data['location']['localtime'].strip()+':00'

        weather_schema['location']['localtime_utc'] = self.time_to_utc(
            datetime.datetime.strptime(
                weather_schema['location']['localtime'], "%Y-%m-%d %H:%M:%S"),
            weather_schema['location']['tz_id']).strftime("%Y-%m-%d %H:%M:%S")

        weather_schema['current'][
            'last_updated_epoch'] = api_weather_data['current']['last_updated_epoch']
        weather_schema['current'][
            'last_updated'] = api_weather_data['current']['last_updated'].strip()+':00'
        weather_schema['current']['temp_c'] = api_weather_data['current']['temp_c']
        weather_schema['current']['temp_f'] = api_weather_data['current']['temp_f']
        weather_schema['current']['is_day'] = api_weather_data['current']['is_day']
        weather_schema['current']['condition']['text'] = api_weather_data['current']['condition']['text']
        weather_schema['current']['condition']['icon'] = api_weather_data['current']['condition']['icon']
        weather_schema['current']['condition']['code'] = api_weather_data['current']['condition']['code']
        weather_schema['current']['wind_mph'] = api_weather_data['current']['wind_mph']
        weather_schema['current']['wind_kph'] = api_weather_data['current']['wind_kph']
        weather_schema['current']['wind_degree'] = api_weather_data['current']['wind_degree']
        weather_schema['current']['wind_dir'] = api_weather_data['current']['wind_dir']
        weather_schema['current']['pressure_mb'] = api_weather_data['current']['pressure_mb']
        weather_schema['current']['pressure_in'] = api_weather_data['current']['pressure_in']
        weather_schema['current']['precip_mm'] = api_weather_data['current']['precip_mm']
        weather_schema['current']['precip_in'] = api_weather_data['current']['precip_in']
        weather_schema['current']['humidity'] = api_weather_data['current']['humidity']
        weather_schema['current']['cloud'] = api_weather_data['current']['cloud']
        weather_schema['current']['feelslike_c'] = api_weather_data['current']['feelslike_c']
        weather_schema['current']['feelslike_f'] = api_weather_data['current']['feelslike_f']
        weather_schema['current']['vis_km'] = api_weather_data['current']['vis_km']
        weather_schema['current']['vis_miles'] = api_weather_data['current']['vis_miles']
        weather_schema['current']['last_updated_utc'] = self.time_to_utc(
            datetime.datetime.strptime(
                weather_schema['current']['last_updated'], "%Y-%m-%d %H:%M:%S"),
            weather_schema['location']['tz_id']).strftime("%Y-%m-%d %H:%M:%S")

        weather_schema['forecast']["forecastday"][0][
            'date'] = api_weather_data['forecast']["forecastday"][0]['date']
        weather_schema['forecast']["forecastday"][0][
            'date_epoch'] = api_weather_data['forecast']["forecastday"][0]['date_epoch']
        weather_schema['forecast']["forecastday"][0]['day'][
            'maxtemp_c'] = api_weather_data['forecast']["forecastday"][0]['day']['maxtemp_c']
        weather_schema['forecast']["forecastday"][0]['day'][
            'maxtemp_f'] = api_weather_data['forecast']["forecastday"][0]['day']['maxtemp_f']
        weather_schema['forecast']["forecastday"][0]['day'][
            'mintemp_c'] = api_weather_data['forecast']["forecastday"][0]['day']['mintemp_c']
        weather_schema['forecast']["forecastday"][0]['day'][
            'mintemp_f'] = api_weather_data['forecast']["forecastday"][0]['day']['mintemp_f']
        weather_schema['forecast']["forecastday"][0]['day'][
            'avgtemp_c'] = api_weather_data['forecast']["forecastday"][0]['day']['avgtemp_c']
        weather_schema['forecast']["forecastday"][0]['day'][
            'avgtemp_f'] = api_weather_data['forecast']["forecastday"][0]['day']['avgtemp_f']
        weather_schema['forecast']["forecastday"][0]['day'][
            'maxwind_mph'] = api_weather_data['forecast']["forecastday"][0]['day']['maxwind_mph']
        weather_schema['forecast']["forecastday"][0]['day'][
            'maxwind_kph'] = api_weather_data['forecast']["forecastday"][0]['day']['maxwind_kph']
        weather_schema['forecast']["forecastday"][0]['day']['totalprecip_mm'
        ] = api_weather_data['forecast']["forecastday"][0]['day']['totalprecip_mm']
        weather_schema['forecast']["forecastday"][0]['day']['totalprecip_in'
        ] = api_weather_data['forecast']["forecastday"][0]['day']['totalprecip_in']
        weather_schema['forecast']["forecastday"][0]['day'][
            'avgvis_km'] = api_weather_data['forecast']["forecastday"][0]['day']['avgvis_km']
        weather_schema['forecast']["forecastday"][0]['day'][
            'avgvis_miles'] = api_weather_data['forecast']["forecastday"][0]['day']['avgtemp_c']
        weather_schema['forecast']["forecastday"][0]['day'][
            'avghumidity'] = api_weather_data['forecast']["forecastday"][0]['day']['avghumidity']
        weather_schema['forecast']["forecastday"][0]['day']['condition'][
            'text'] = api_weather_data['forecast']["forecastday"][0]['day']['condition']['text']
        weather_schema['forecast']["forecastday"][0]['day']['condition'][
            'icon'] = api_weather_data['forecast']["forecastday"][0]['day']['condition']['icon']
        weather_schema['forecast']["forecastday"][0]['day']['condition'][
            'code'] = api_weather_data['forecast']["forecastday"][0]['day']['condition']['code']

        weather_schema['forecast']["forecastday"][0]['astro'][
            'sunrise'] = api_weather_data['forecast']["forecastday"][0]['astro']['sunrise']
        weather_schema['forecast']["forecastday"][0]['astro'][
            'sunset'] = api_weather_data['forecast']["forecastday"][0]['astro']['sunset']
        weather_schema['forecast']["forecastday"][0]['astro'][
            'moonrise'] = api_weather_data['forecast']["forecastday"][0]['astro']['moonrise']
        weather_schema['forecast']["forecastday"][0]['astro'][
            'moonset'] = api_weather_data['forecast']["forecastday"][0]['astro']['moonset']

        hour_data = api_weather_data['forecast']["forecastday"][0]['hour']
        weather_schema['forecast']["forecastday"][0]['hour'] = self.hourly_weather_data(hour_data)
        return weather_schema
