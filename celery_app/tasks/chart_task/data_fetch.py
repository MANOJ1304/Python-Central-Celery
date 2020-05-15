from tasks.celery_queue_tasks import BaseChartTask
from wildfire.wildfire_api import WildfireApi
from .widgets.chart import BarChart, LineChart, OverLap
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from boltons.iterutils import research, get_path
import logging
import json
import dateparser
import dpath
import os
import pathlib

log = logging.getLogger(__name__)


CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}
class DataFetch(BaseChartTask):
    name = 'Data Fetch'
    description = '''Matches address from sources A and B and constructs
a list of Address Matches for other analysis and manual review.'''
    public = True
    autoinclude = True

    def __init__(self):
        super(DataFetch, self).__init__()
        self.map_image = "visitors"
        

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])
        print('Is dev ', self.dev)
        self.report_details = kwargs["report"]
        self.build_dir()
        if kwargs.get('chart_name', None) is None:
            kwargs['chart_name'] = self.map_image

        if not self.dev:
            data = self.__get_data(**kwargs["creds"], **kwargs["data_params"], area_id = kwargs['chart_options'].get('area_id', None))
            data = self.__process_data( data)
            d = data["analytic_data"][0]
            # print(d)
            self.__draw_chart(d["xAxis"], d["series"][-1], kwargs["chart_options"], kwargs['chart_name'])
        kwargs['output']['img_url'] = '{}/{}/{}.png'.format(kwargs['config']['base_url'], self.report_path_image, kwargs['chart_name']) 
        return kwargs['output']

    def __draw_chart(self, xaxis, data_storage, chart_options:dict= {}, chart_name = "vis"):

        bar = BarChart("dsad")
        line = LineChart("sad")
        
        bar.xaxis(xaxis,)
        line.xaxis(xaxis,)
        # print(list(zip(data_storage.get("new") , data_storage.get("repeat"))))
        total = [ sum([x,y]) for x, y in list(zip(data_storage.get("new") , data_storage.get("repeat")))]
        # print(total)
        if "stack" in list(chart_options["series"].keys()):
            stack = chart_options["series"]["stack"]
            
        for legend, data in data_storage.items():
            if legend in ["new", "repeat"]: 
                # print("Values", title, data_storage.get(title), total)
                nr_data= [  {"value": n, "percent": n / t} for n, t in list(zip(data_storage.get(legend) , total))]
                bar.ydata(legend.replace("_"," ").title(), nr_data , options=chart_options["series"])

        # chart_options["label_opts"] = self.label_style[chart_options["label_opts"]] 
        for legend, data in data_storage.items():
            if legend in ["total_visitor"]: 
                line.ydata(legend.replace("_"," ").title(), data)
        # bar.set_option(chart_options)
        
        bar.set_option(chart_options["series"], {}, chart_options["global"]['yaxis_opts'])
        line.label_style['single_value'].update(color= '#000')
        line.set_option({"label_opts": "single_value", "z_level":1})
        overlap = bar.get_chart_instance().overlap(line.get_chart_instance())
        # overlap.render(file_name="visualization/html/abc.html")
        grid = OverLap(width="540px", height="300px")
        grid.add(overlap, is_control_axis_index=True)

        # print(grid.get_chart_instance().dump_options())
        grid.generate(file_name="{}/{}/{}.html".format(self.root_path, self.report_path_html, chart_name),
            image_name="{}/{}/{}.png".format(self.root_path, self.report_path_image, chart_name))
        
        # bar.get_chart_instance().overlap(line.get_chart_instance())
        # bar.generate(file_name="{}/{}.html".format(self.report_path_html, self.map_image),
        # image_name="{}/{}.png".format(self.report_path_image, self.map_image))


    def __get_data(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict,
        date_range:list, agg_type:str, exclude_params:list, area_id:str = None):
        log.debug("{} {}".format(username, password))

        is_area_compute = False
        area_info = {}
        if area_id is not None:
            is_area_compute = True
            area_info = self.get_area_info(username, password, cfg, venue_id, area_id)
       
        w =  WildfireApi(username, password, cfg)
        d = (w.venues()
        .analytics(venue_id=venue_id)
        .wifi()
        .set_filter(date_range, 'visitors', elasttic_filters, exclude_params, is_area_compute = is_area_compute, area_filter = area_info)
        .request())
        # print(json.dumps(d, indent=4))
        return d

    def __process_data(self, data:dict):
        # print("Data ===========", data)
        r = research(data,  lambda p, k, v:  k in ["date", "xAxis"]) 
        for i in r: 
            i = list(i) 
            if isinstance(i[1], list):
                i[1] = [ dateparser.parse(item).strftime("%-d %b, %y") for item in i[1]] 
                dpath.util.set(data, "/".join([ str(item)  for item in i[0]]) ,[ dateparser.parse(item).strftime("%-d %b, %y") for item in i[1]] ) 
            elif isinstance(i[1], str): 
                dpath.util.set(data, "/".join([ str(item)  for item in i[0]]) ,dateparser.parse(i[1]).strftime("%-d %b, %y"))
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
        