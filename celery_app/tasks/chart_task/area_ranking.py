from tasks.celery_queue_tasks import BaseChartTask
from wildfire.wildfire_api import WildfireApi

import logging
import json
import copy

import time


CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}

class AreaRankingTask(BaseChartTask):
    name = 'Area Ranking Task'
    description = '''Fetches records based'''
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
            .lists())
        area_names = {}
        if len(d['_items']) > 0:
            for area in d['_items']:
                area_names[area['area_id']] = area['name'][0].get("text") if isinstance(area['name'], list) else 'Area'
        return area_names

    def __get_data(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict,
        date_range:list, agg_type:str, exclude_params:list):

        w =  WildfireApi(username, password, cfg)
        d = (w.venues()
        .analytics(venue_id=venue_id)
        .top_area_visits()
        .set_filter(date_range, 'visitors', elasttic_filters, exclude_params)
        .request())
        result = []
        # print(json.dumps(d, indent=4))
        if len(d['analytic_data']) > 0:
            area_names = self.__get_area(username, password, cfg, venue_id)
            res = d['analytic_data'][0]['series'][0]
            for key, value in res.items():
                value['area_name'] = area_names.get(key, '')
                result.append(value)
            
            result = sorted(result, key= lambda k: k['one_done']['value'], reverse=True)

            for value in result:
                for k, v in value.items():
                    if type(value[k]) is dict:
                        value[k]['avg_change'] = str(value[k]['avg_change'])
                        if type(value[k]['value']) is int:
                            value[k]['value'] = format(value[k]['value'], ',d')
                # value['area_name'] = area_names.get(key, '')
                # result[area_names.get(key, '')] = value
                # result.append(value)
            # for key, value in result.items():
                # value['avg_change'] = str(value['avg_change'])
        # print(json.dumps(result, indent=4))
        
        return result[:10]