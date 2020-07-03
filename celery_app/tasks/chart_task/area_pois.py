from tasks.celery_queue_tasks import BaseChartTask
from wildfire.wildfire_api import WildfireApi

import logging
import json
import copy

import time


CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}

class AreaPoisTask(BaseChartTask):
    name = 'Area Pois Task'
    description = '''Fetches area pois records'''
    public = True
    autoinclude = True

    def __init__(self):
        pass

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])
        tdata = self.__get_data(**kwargs["creds"], **kwargs["data_params"])
        return tdata
    
    def __get_area(self, username, password, cfg:dict, venue_id:str):
        w =  WildfireApi(username, password, cfg)
        d = (w.venues() 
            .get(venue_id)
            .pois()
            .lists(pagination=True))
        area_names = {}
        # print('pois length', len(d['_items']))
        if len(d['_items']) > 0:
            for area in d['_items']:
                area_names[area['area_id']] = area['name'][0].get("text") if isinstance(area['name'], list) else 'Area'
        return area_names

    def __get_data(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict,
        date_range:list, agg_type:str, exclude_params:list):
        area_names = self.__get_area(username, password, cfg, venue_id)
        return area_names