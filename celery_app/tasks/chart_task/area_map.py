from tasks.celery_queue_tasks import BaseChartTask
from wildfire.wildfire_api import WildfireApi

import logging
import json
import copy

import time


CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}

class AreaMapTask(BaseChartTask):
    name = 'Area Map Task'
    description = '''Fetches area heatmap records'''
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
        print('pois length', len(d['_items']))
        if len(d['_items']) > 0:
            for area in d['_items']:
                area_names[area['area_id']] = area['name'][0].get("text") if isinstance(area['name'], list) else 'Area'
        return area_names

    def __get_data(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict,
        date_range:list, agg_type:str, exclude_params:list):

        w =  WildfireApi(username, password, cfg)
        d = (w.venues()
        .analytics(venue_id=venue_id)
        .area_map()
        .set_filter(date_range, '', elasttic_filters, exclude_params, is_prop_vis= True)
        .request({'type':'agg'}))

        # print(json.dumps(d, indent=4))
        
                # value['area_name'] = area_names.get(key, '')
                # result[area_names.get(key, '')] = value
                # result.append(value)``
            # for key, value in result.items():
                # value['avg_change'] = str(value['avg_change'])
        # print(json.dumps(result, indent=4))
        return d