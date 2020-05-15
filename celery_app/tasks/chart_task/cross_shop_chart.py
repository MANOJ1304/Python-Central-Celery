from tasks.celery_queue_tasks import BaseChartTask
from tasks.chart_task.utils import round_number, convert_capitalize
from wildfire.wildfire_api import WildfireApi
from .widgets.chart import SankeyChart
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode

import json
import copy

from snapshot_selenium import snapshot as driver
from pyecharts.render import make_snapshot
import time


CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}

class CrossShopChart(BaseChartTask):
    name = 'Cross Shopping Sankey Task'
    description = ''' Creates Snakey chart'''
    public = True
    autoinclude = True

    def __init__(self):
        super(CrossShopChart, self).__init__()
        self.map_image = 'cross_shop_chart'
    

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])
        self.report_details = kwargs["report"]
        self.build_dir()
        if kwargs.get('chart_name', None) is None:
            kwargs['chart_name'] = self.map_image

        if not self.dev:
            cdata = self.__get_data(**kwargs["creds"], **kwargs["data_params"], area_id = kwargs['chart_options'].get('area_id', None) )
            # json_object = json.dumps(cdata, indent = 4) 
            # with open('{}.json'.format(kwargs['chart_name']), 'w') as f:
            #     f.write(json_object)
            self.__draw_chart(cdata, kwargs['chart_name'])
        kwargs['output']['img_url'] = '{}/{}/{}.png'.format(
            kwargs['config']['base_url'],
            self.report_path_image,
            kwargs['chart_name']
        )
        return kwargs['output']

    def __get_data(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict,
        date_range:list, agg_type:str, exclude_params:list, area_id:str = None):

        
        area_params = {}
        if area_id is not None:
            area_params['area_id'] = area_id
       

        w =  WildfireApi(username, password, cfg)
        d = (w.venues()
        .analytics(venue_id=venue_id)
        .map_journey()
        .set_filter(date_range, 'visitors', elasttic_filters, exclude_params, True , {'type': 'cross_shopping'})
        .request(query_string=area_params))
        # print(json.dumps(d, indent=4))
        return d

    def __draw_chart(self, data, chart_name = "csc"):
        # print(data)
        formatter = 'function(data) { return data.name ; }'
        cross_shop_res = data['analytic_data']
        if len(data['analytic_data']) > 0:
            agg_data = cross_shop_res[0]['aggregation_data']
            links = agg_data['links']
            nodes = agg_data['nodes']
            sankeyChart = SankeyChart()
            sankeyChart.chart.add(
                "",
                nodes,
                links,
                linestyle_opt=opts.LineStyleOpts(opacity=0.2, curve=0.5, color="source"),
                label_opts=opts.LabelOpts(position="right", formatter=JsCode(formatter)),
            )

            sankeyChart.generate(file_name="{}/{}/{}.html".format(self.root_path, self.report_path_html, chart_name),
            image_name="{}/{}/{}.png".format(self.root_path, self.report_path_image, chart_name))
            