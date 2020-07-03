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
        st_parking_areas = ["4309834628c546f3896f7e99f30a6641", "4bf929a11e7140ceb9c973af0dc1ef95" , "6e24036d41cb4f518334482510b430a0" ,
        "9bf0aec600b042a3abd249cc441178a5", "30d063c77ebc41fe84a17b929f36655d"]
        sg_parking_areas = ["50428e8a52f343f594d55abc038129b2","68799e931b2949338bc20591e43adc6f","6893c9a23d0a441d93900b6c2a2a14c6",
        "6fa02129add644d2a0d36f2ede0631b0","b67773c62263411eae232e54e33ed863",
        "f1554d8ef8ce41b9b6e7b527e8accbbf","e11dd4a7261244d7872c2c2fd0b53405"]
        cn_p_a = ['3664e66c395e4cb291052f0d34174384', '45652c141f034b318c256797420802ba', '49cfb85ef80247b6877a3b904a4089fd', 
            '82990a159d5f442a96b2fcf5a4b2e5e0', '947f9eb47fa645679543da1f6048da38', 'd323348dacf84d0cb719177394e1e1e8', 'dc650096740b4e528b4bfb39761a72e9',
            'e0a306c066d444eca78c6fc863053de9', 'f39ea1a4fdfa4396b4170f494a35d5f1', 'b6a3ccbf605c472bb2c374d55ba55646']
        self.parking_areas = st_parking_areas + sg_parking_areas + cn_p_a
        
    

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
        .set_filter(date_range, '', elasttic_filters, exclude_params, True , {'type': 'cross_shopping'})
        .request(query_string=area_params))
        # print(json.dumps(d, indent=4))
        return d

    def __draw_chart(self, data, chart_name = "csc"):
        # print(data)
        formatter = 'function(data) { return data.name ; }'
        cross_shop_res = data['analytic_data']

        # with open('{}.json'.format(chart_name), 'w') as file:
        #     file.write(json.dumps(data, indent=4))
        
        if len(data['analytic_data']) > 0:
            agg_data = cross_shop_res[0]['aggregation_data']
            links = agg_data['links']
            nodes = agg_data['nodes']

            # links_index = []

            links = [v for v in links if v['source'] not in self.parking_areas]

            links = [v for v in links if v['target'] not in self.parking_areas]

            nodes = [v for v in nodes if 'parking' not in v['name'].lower() and (v['id'] not in self.parking_areas)]

            # for i, v in enumerate(links):
            #     if v['target'] in self.parking_areas:
            #         try:
            #             links.pop(i)
            #             # print(i, v['source'])
            #             # links_index.append(i)
            #             # del links[i]
            #         except Exception as e:
            #             pass
            # _ = [links.pop(i) for i in links_index]

            # with open('cross.json','w') as f:
            #     f.write(json.dumps(cross_shop_res, indent=4))       
            # for i, v in enumerate(nodes):
            #     if (v['id'] in st_parking_areas) or ('parking' in v['name'].lower()):
            #         # print('Parking id ', v['source'], v['target'])
            #         try:
            #             nodes.pop(i)
            #         except Exception as e:
            #             pass
            # nodes = agg_data['nodes']

            for node in nodes:
                del node['value']
            sankeyChart = SankeyChart()
            sankeyChart.chart.add(
                "",
                nodes,
                links,
                linestyle_opt=opts.LineStyleOpts(opacity=0.2, curve=0.5, color="source"),
                label_opts=opts.LabelOpts(position="right", formatter=JsCode(formatter), font_size=8),
            )

            sankeyChart.generate(file_name="{}/{}/{}.html".format(self.root_path, self.report_path_html, chart_name),
            image_name="{}/{}/{}.png".format(self.root_path, self.report_path_image, chart_name))
            