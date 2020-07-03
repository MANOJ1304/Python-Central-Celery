from tasks.celery_queue_tasks import BaseChartTask
from wildfire.wildfire_api import WildfireApi
from .widgets.chart import BarChart, LineChart, OverLap
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Line
from boltons.iterutils import research, get_path
import logging
import json
import dateparser
import dpath
import os
import pathlib

from .utils import is_weekend

log = logging.getLogger(__name__)


CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}
class VisitorGraph(BaseChartTask):
    name = 'Visitor Graph'
    description = '''Matches address from sources A and B and constructs
a list of Address Matches for other analysis and manual review.'''
    public = True
    autoinclude = True

    def __init__(self):
        super(VisitorGraph, self).__init__()
        self.map_image = "visitors_graph"
        

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])
        print('Is dev ', self.dev)
        self.report_details = kwargs["report"]
        self.build_dir()
        if kwargs.get('chart_name', None) is None:
            kwargs['chart_name'] = self.map_image

        if not self.dev:
            interval = kwargs.get('api_filter', {}).get('interval', None)
            data = self.__get_data(**kwargs["creds"], **kwargs["data_params"], area_id = kwargs['chart_options'].get('area_id', None),
                visitor_filter = interval )
            data = self.__process_data( data)
            d = data["analytic_data"][0]
            # print(d)
            self.__draw_chart(d["xAxis"], d["series"][-1], kwargs["chart_options"], kwargs['chart_name'])
            if interval is not None:
                kwargs['output']['title'] += ' Week'
            else:
                kwargs['output']['title'] += ' Day' 
            
        kwargs['output']['img_url'] = '{}/{}/{}.png'.format(kwargs['config']['base_url'], self.report_path_image, kwargs['chart_name']) 
        return kwargs['output']

    def __draw_chart(self, xaxis, data_storage, chart_options:dict= {}, chart_name = "vis"):

        lc = LineChart("dsad")
        line = Line(init_opts=opts.InitOpts(animation_opts=opts.AnimationOpts(animation=False),
            width='1200px', height='300px'))
        line.add_xaxis(xaxis)
        # bar.xaxis(xaxis,)
        total = [ sum([x,y]) for x, y in list(zip(data_storage.get("new") , data_storage.get("repeat")))]
        markline_formatter = """
            function (data) {
                return Number(Math.round(data.value)).toLocaleString('US-en');
            }
        """
        date_format = '%d %b, %Y'
        final_data = []
        for i in range(len(total)):
            td = {}
            if (is_weekend(xaxis[i], date_format)):
                td['itemStyle'] = {'color':'#183058'}
                td['symbolSize'] = 0
                # td['symbol'] = 'circle'
            # else:
                # td['itemStyle'] = {'color': '#eee', 'borderWidth': 1, 'borderColor': '#183059'}
            td['value'] = total[i]
            final_data.append(td)

        line.add_yaxis('', final_data, symbol_size=0, color="#666", xaxis_index=0, itemstyle_opts=lc.line_colors.pop(),
            label_opts= opts.LabelOpts(is_show=False),
            markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")],
                label_opts=opts.LabelOpts(is_show=True, formatter=JsCode(markline_formatter), position='middle'),
                linestyle_opts=opts.LineStyleOpts( type_='dashed'),
                symbol_size=5))

        line.set_global_opts(xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=8, rotate=-15)))
        lc.chart = line
        
        lc.generate(file_name="{}/{}/{}.html".format(self.root_path, self.report_path_html, chart_name),
            image_name="{}/{}/{}.png".format(self.root_path, self.report_path_image, chart_name))


    def __get_data(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict,
        date_range:list, agg_type:str, exclude_params:list, area_id:str = None, visitor_filter = None):
        log.debug("{} {}".format(username, password))

        is_area_compute = False
        area_info = {}
        if area_id is not None:
            is_area_compute = True
            area_info = self.get_area_info(username, password, cfg, venue_id, area_id)

        qparams = {}
        if visitor_filter is not None:
            qparams['interval'] = visitor_filter
        w =  WildfireApi(username, password, cfg)
        d = (w.venues()
        .analytics(venue_id=venue_id)
        .wifi()
        .set_filter(date_range, 'visitors', elasttic_filters, exclude_params, is_area_compute = is_area_compute, area_filter = area_info)
        .request(query_string=qparams))
        # print(json.dumps(d, indent=4))
        return d

    def __process_data(self, data:dict):
        # print("Data ===========", data)
        r = research(data,  lambda p, k, v:  k in ["date", "xAxis"]) 
        for i in r: 
            i = list(i) 
            if isinstance(i[1], list):
                i[1] = [ dateparser.parse(item).strftime("%-d %b, %Y") for item in i[1]] 
                dpath.util.set(data, "/".join([ str(item)  for item in i[0]]) ,[ dateparser.parse(item).strftime("%-d %b, %Y") for item in i[1]] ) 
            elif isinstance(i[1], str): 
                dpath.util.set(data, "/".join([ str(item)  for item in i[0]]) ,dateparser.parse(i[1]).strftime("%-d %b, %Y"))
        return data

    def get_area_info(self, username, password, cfg:dict, venue_id:str, area_id:str):
        # w =  WildfireApi(username, password, cfg)
        # d = (w.venues() 
        #     .get(venue_id)
        #     .pois()
        #     .lists(search={"type": "area", "area_id": area_id}, ))
        area_data = {}
        # area_data['area.zeid'] = d['_items'][0]['zone_id']
        # area_data['properties.floor_id'] = d['_items'][0]['floor_id']
        area_data['area_ids.id'] = area_id
        # area_data['venue_id'] = venue_id
        area_data['gt'] = 0
        area_data['lt'] = 6
        # print(d)
        return area_data
        