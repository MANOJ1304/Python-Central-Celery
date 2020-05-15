from tasks.celery_queue_tasks import BaseChartTask
from wildfire.wildfire_api import WildfireApi

import logging
import json
import copy

import time

log = logging.getLogger(__name__)

CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}

class EventsTask(BaseChartTask):
    name = 'Event Task'
    description = '''Fatches evetns for venue.'''
    public = True
    autoinclude = True

    def __init__(self):
        pass

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])
        events = self.__get_events(**kwargs["creds"], **kwargs["data_params"])
        return events

    def __get_events(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict,
        date_range:list, agg_type:str, exclude_params:list):
        log.debug("{} {}".format(username, password))
        events = cfg['events']
        search_dict = {
            'type': events['type'],
            "start_time": {
                "$gte": events['gt'],
                "$lte": events['lt'],
            }
        }
        # w = None
        # del w
        w =  WildfireApi(username, password, cfg)
        d = (w.venues()
        .get(venue_id)
        .events()
        .lists(search=search_dict, pagination=True, sort_fields='start_time'))
        events_data = {}

        for item in d['_items']:
            try:
                start_time = item['start_time'].split(' ')
                end_time = item['end_time'].split(' ')
                data = {'name': item['name'][0]['text'], 'start_time': start_time[1], 'end_time': end_time[1]}
                if events_data.get(start_time[0], None) is not None:
                    events_data[start_time[0]].append(data)
                else:
                    events_data[start_time[0]] = [data]
            except Exception as _:
                continue
        # print('events_data ', '*' * 100)
        # print(json.dumps(d, indent=4))
        # print( len(d['_items']))
        return events_data
