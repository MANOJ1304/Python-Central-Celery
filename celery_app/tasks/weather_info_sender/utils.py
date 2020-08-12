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

    def celsius_to_fahrenheit(self,input_temp):
        return round(((input_temp * 1.8) + 32),1)

    def hourly_weather_data(self, api_hour_data,date):
        """ get hourly weather data. """
        temp_data = []
        for hour_info in api_hour_data:
            h_json = {
                "condition": {}
            }

            h_json['time'] = date + " " + str(int(int(hour_info['time'])/100)) + ":00:00"
            # h_json['time'] = hour_info['time']+":00:00"
            h_json['temp_c'] = hour_info['temperature']
            h_json['temp_f'] = self.celsius_to_fahrenheit(hour_info['temperature'])
            # h_json['is_day'] = hour_info['is_day']
            h_json['condition']['text'] = hour_info['weather_descriptions'][0]
            h_json['condition']['icon'] = hour_info['weather_icons'][0].split(':')[1]
            h_json['condition']['code'] = hour_info['weather_code']

            # h_json['wind_mph'] = hour_info['wind_mph']
            h_json['wind_kph'] = hour_info['wind_speed']
            h_json["wind_degree"] = hour_info["wind_degree"]
            h_json["wind_dir"] = hour_info["wind_dir"]
            h_json["pressure_mb"] = hour_info["pressure"]
            # h_json["pressure_in"] = hour_info["pressure_in"]
            h_json["precip_mm"] = hour_info["precip"]
            # h_json["precip_in"] = hour_info["precip_in"]
            h_json["humidity"] = hour_info["humidity"]
            h_json["cloud"] = hour_info["cloudcover"]
            h_json["feelslike_c"] = hour_info["feelslike"]
            h_json["feelslike_f"] = self.celsius_to_fahrenheit(hour_info["feelslike"])

            h_json["windchill_c"] = hour_info["windchill"]
            h_json["windchill_f"] = self.celsius_to_fahrenheit(hour_info["windchill"])
            h_json["heatindex_c"] = hour_info["heatindex"]
            h_json["heatindex_f"] = self.celsius_to_fahrenheit(hour_info["heatindex"])
            h_json["dewpoint_c"] = hour_info["dewpoint"]
            h_json["dewpoint_f"] = self.celsius_to_fahrenheit(hour_info["dewpoint"])
            h_json["will_it_rain"] = hour_info["chanceofrain"]
            h_json["will_it_snow"] = hour_info["chanceofsnow"]
            # h_json["vis_km"] = hour_info["vis_km"]
            # h_json["vis_miles"] = hour_info["vis_miles"]
            # h_json["gust_mph"] = hour_info["gust_mph"]
            # h_json["gust_kph"] = hour_info["gust_kph"]

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
        weather_schema['location']['weather_city'] = api_weather_data['location'].get('weather_city',api_weather_data['location']['name'])
        weather_schema['location']['region'] = api_weather_data['location']['region']
        weather_schema['location']['country'] = api_weather_data['location']['country']
        weather_schema['location']['lat'] = api_weather_data['location']['lat']
        weather_schema['location']['lon'] = api_weather_data['location']['lon']
        weather_schema['location']['tz_id'] = api_weather_data['location']['timezone_id']
        weather_schema['location']['localtime_epoch'] = api_weather_data['location']['localtime_epoch']
        weather_schema['location']['localtime'] = api_weather_data['location']['localtime'].strip()+':00'

        weather_schema['location']['localtime_utc'] = self.time_to_utc(datetime.datetime.strptime(weather_schema['location']['localtime'], "%Y-%m-%d %H:%M:%S"),weather_schema['location']['tz_id']).strftime("%Y-%m-%d %H:%M:%S")
        weather_schema['location']['utc_offset'] = api_weather_data['location']['utc_offset']

        # weather_schema['current']['last_updated_epoch'] = api_weather_data['current']['localtime_epoch']
        # weather_schema['current']['last_updated'] = api_weather_data['current']['localtime'].strip()+':00'
        # weather_schema['current']['temp_c'] = api_weather_data['current']['temp_c']
        # weather_schema['current']['temp_f'] = api_weather_data['current']['temp_f']
        # weather_schema['current']['is_day'] = api_weather_data['current']['is_day']
        # weather_schema['current']['condition']['text'] = api_weather_data['current']['condition']['text']
        # weather_schema['current']['condition']['icon'] = api_weather_data['current']['condition']['icon']
        # weather_schema['current']['condition']['code'] = api_weather_data['current']['condition']['code']
        # weather_schema['current']['wind_mph'] = api_weather_data['current']['wind_mph']
        # weather_schema['current']['wind_kph'] = api_weather_data['current']['wind_kph']
        # weather_schema['current']['wind_degree'] = api_weather_data['current']['wind_degree']
        # weather_schema['current']['wind_dir'] = api_weather_data['current']['wind_dir']
        # weather_schema['current']['pressure_mb'] = api_weather_data['current']['pressure_mb']
        # weather_schema['current']['pressure_in'] = api_weather_data['current']['pressure_in']
        # weather_schema['current']['precip_mm'] = api_weather_data['current']['precip_mm']
        # weather_schema['current']['precip_in'] = api_weather_data['current']['precip_in']
        # weather_schema['current']['humidity'] = api_weather_data['current']['humidity']
        # weather_schema['current']['cloud'] = api_weather_data['current']['cloud']
        # weather_schema['current']['feelslike_c'] = api_weather_data['current']['feelslike_c']
        # weather_schema['current']['feelslike_f'] = api_weather_data['current']['feelslike_f']
        # weather_schema['current']['vis_km'] = api_weather_data['current']['vis_km']
        # weather_schema['current']['vis_miles'] = api_weather_data['current']['vis_miles']
        # weather_schema['current']['last_updated_utc'] = self.time_to_utc(datetime.datetime.strptime(weather_schema['current']['last_updated'], "%Y-%m-%d %H:%M:%S"),weather_schema['location']['tz_id']).strftime("%Y-%m-%d %H:%M:%S")

        day_forecast_data = list(api_weather_data['daily'].values())[0]
        interval_24h_data = day_forecast_data['hourly'][0]

        hourly_forecast_data = list(api_weather_data['hourly'].values())[0]
        interval_1hs_data = hourly_forecast_data['hourly']

        weather_schema['forecast']["forecastday"][0]['date'] = day_forecast_data['date']
        weather_schema['forecast']["forecastday"][0]['date_epoch'] = day_forecast_data['date_epoch']
        weather_schema['forecast']["forecastday"][0]['day']['maxtemp_c'] = day_forecast_data['maxtemp']
        weather_schema['forecast']["forecastday"][0]['day']['maxtemp_f'] = self.celsius_to_fahrenheit(day_forecast_data['maxtemp'])
        weather_schema['forecast']["forecastday"][0]['day']['mintemp_c'] = day_forecast_data['mintemp']
        weather_schema['forecast']["forecastday"][0]['day']['mintemp_f'] = self.celsius_to_fahrenheit(day_forecast_data['mintemp'])
        weather_schema['forecast']["forecastday"][0]['day']['avgtemp_c'] = interval_24h_data['temperature']
        weather_schema['forecast']["forecastday"][0]['day']['avgtemp_f'] = self.celsius_to_fahrenheit(interval_24h_data['temperature'])

        # weather_schema['forecast']["forecastday"][0]['day']['maxwind_mph'] = interval_24h_data['forecast']["forecastday"][0]['day']['maxwind_mph']
        weather_schema['forecast']["forecastday"][0]['day']['maxwind_kph'] = interval_24h_data['wind_speed']

        weather_schema['forecast']["forecastday"][0]['day']['totalprecip_mm'] = interval_24h_data['precip']
        # weather_schema['forecast']["forecastday"][0]['day']['totalprecip_in'] = api_weather_data['forecast']["forecastday"][0]['day']['totalprecip_in']

        weather_schema['forecast']["forecastday"][0]['day']['avgvis_km'] = interval_24h_data['visibility']
        # weather_schema['forecast']["forecastday"][0]['day']['avgvis_miles'] = api_weather_data['forecast']["forecastday"][0]['day']['avgtemp_c']
        weather_schema['forecast']["forecastday"][0]['day']['avghumidity'] = interval_24h_data['humidity']

        weather_schema['forecast']["forecastday"][0]['day']['condition']['text'] = interval_24h_data['weather_descriptions'][0]
        weather_schema['forecast']["forecastday"][0]['day']['condition']['icon'] = interval_24h_data['weather_icons'][0].split(':')[1]
        weather_schema['forecast']["forecastday"][0]['day']['condition']['code'] = interval_24h_data['weather_code']

        # weather_schema['forecast']["forecastday"][0]['astro']['sunrise'] = api_weather_data['forecast']["forecastday"][0]['astro']['sunrise']
        # weather_schema['forecast']["forecastday"][0]['astro']['sunset'] = api_weather_data['forecast']["forecastday"][0]['astro']['sunset']

        # weather_schema['forecast']["forecastday"][0]['astro']['moonrise'] = api_weather_data['forecast']["forecastday"][0]['astro']['moonrise']
        # weather_schema['forecast']["forecastday"][0]['astro']['moonset'] = api_weather_data['forecast']["forecastday"][0]['astro']['moonset']

        # hour_data = api_weather_data['forecast']["forecastday"][0]['hour']
        weather_schema['forecast']["forecastday"][0]['hour'] = self.hourly_weather_data(interval_1hs_data, hourly_forecast_data['date'])
        weather_schema['weather_date'] = day_forecast_data['date']

        # print("\n........... MODIFIED DATA.......",weather_schema)
        # exit()
        return weather_schema
