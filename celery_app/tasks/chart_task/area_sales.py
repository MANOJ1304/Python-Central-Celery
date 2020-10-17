from tasks.celery_queue_tasks import BaseChartTask
from wildfire.wildfire_api import WildfireApi

import logging
import json
import copy

import time


CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}

class AreaSales(BaseChartTask):
    name = 'Area Sales Task'
    description = '''Fetches sales records for all areas'''
    public = True
    autoinclude = True

    def __init__(self):
        pass

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])
        tdata = self.__get_data(**kwargs["creds"], **kwargs["data_params"])
        return tdata

    def __get_data(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict,
        date_range:list, agg_type:str, exclude_params:list):
        w =  WildfireApi(username, password, cfg)
        d = (w.venues()
        .analytics(venue_id=venue_id)
        .sales_stats()
        .set_filter(date_range, '', elasttic_filters, exclude_params)
        .request())
        # print('res', d)

        result = []
        if len(d['analytic_data']) > 0:
            res = d['analytic_data'][0]['series'][0]
            for area_id, value in res.items():
                data = {}
                name = ' '.join( [i.title() for i in value['name'].split('_')])
                data['display'] = '{}{}'.format(value['unit'], format(int(value['value']), ',d'))
                data['name'] = name
                data['value'] = value['value']
                data['area_id'] = area_id
                data['unit'] = value['unit']
                result.append(data)
            result = sorted(result, key= lambda k: k['value'], reverse=True)
        return result