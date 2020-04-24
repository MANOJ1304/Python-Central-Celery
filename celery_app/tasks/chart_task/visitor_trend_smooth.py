from tasks.celery_queue_tasks import BaseChartTask
from wildfire.wildfire_api import WildfireApi
from .widgets.chart import BarChart, LineChart, OverLap, CustomMap
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from boltons.iterutils import research, get_path
import logging
import json
import dateparser
import dpath
import copy
from pyecharts.faker import Faker
from pyecharts.charts import Line
from snapshot_selenium import snapshot as driver
from pyecharts.render import make_snapshot
import time
log = logging.getLogger(__name__)

CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}

class VisitorTrendVisual(BaseChartTask):
    name = 'Visitor Trend'
    description = '''Matches address from sources A and B and constructs
a list of Address Matches for other analysis and manual review.'''
    public = True
    autoinclude = True

    def __init__(self):
        pass

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])
        self.report_details = kwargs["report"]
        self.build_dir()
        cdata = self.__get_data(**kwargs["creds"], **kwargs["data_params"])
        self.__draw_chart(cdata, kwargs["chart_name"])
        cdata['img_url'] = '{}/{}/{}.png'.format(
            kwargs['config']['base_url'],
            self.report_path_image,
            kwargs["chart_name"]
        ) 
        events = self.__get_events(**kwargs["creds"], **kwargs["data_params"])
        # data = self.__process_data( data)
        # d = data["analytic_data"][0]
        # print(cdata)
        # self.__draw_chart(d["xAxis"], d["series"][-1], kwargs["chart_options"])
        # print(kwargs['output'])
        cdata['events'] = events
        return cdata

    def __draw_chart(self, data, chart_name):
        # print(data)
        if len(data['analytic_data']) > 0 and len(data['analytic_data'][0]['series'][3]['total_visitor']) > 0:
            # time.sleep(2)
            line = Line(init_opts=opts.InitOpts(width="400px", height='100px'))
            _ = (
                line
                .add_xaxis(Faker.choose())
                .add_yaxis("", data['analytic_data'][0]['series'][3]['total_visitor'], is_smooth=True,
                            areastyle_opts= opts.AreaStyleOpts(color='#011638', opacity=0.1),
                            linestyle_opts=opts.LineStyleOpts(width=1, color='#011638'),
                            color='rgba(0, 180, 0, 0.3)',
                            symbol='none')
                .set_global_opts(
                    xaxis_opts=opts.AxisOpts(is_show=False, boundary_gap=False),
                    yaxis_opts=opts.AxisOpts(is_show=False))
                .render("{}/{}/{}.html".format(self.root_path, self.report_path_html, chart_name))
            )
            # print(line.dump_options())
            make_snapshot(driver, "{}/{}/{}.html".format(self.root_path, self.report_path_html, chart_name),
                "{}/{}/{}.png".format(self.root_path, self.report_path_image, chart_name))
            # bar.generate(file_name="visualization/html/render.html", image_name="visualization/images/example.png")


    def __get_data(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict, date_range:list, agg_type:str, exclude_params:list, ):
        log.debug("{} {}".format(username, password))
        w =  WildfireApi(username, password, cfg)
        d = (w.venues()
        .analytics(venue_id=venue_id)
        .wifi()
        .set_filter(date_range, agg_type, elasttic_filters, exclude_params)
        
        .request())
        
        # print(json.dumps(d, indent=4))
        return d

    def __get_events(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict,
        date_range:list, agg_type:str, exclude_params:list):
        log.debug("{} {}".format(username, password))
        events = cfg['events']
        search_dict = {
            'type': events['type'],
            "start_time": {
                "$gte":events['gt'],
                "$lte":events['lt'],
            }
        }
        w =  WildfireApi(username, password, cfg)
        d = (w.venues()
        .get(venue_id)
        .events()
        .lists(search=search_dict, pagination=True, sort_fields='start_time'))
        events_data = {}
        for item in d['_items']:
            start_time = item.get('start_time', '1970-01-01 00:00:00').split(' ')
            end_time = item.get('end_time', '1970-01-01 00:00:00').split(' ')
            data = {'name': item['name'][0]['text'], 'start_time': start_time[1], 'end_time': end_time[1]}
            if events_data.get(start_time[0], None) is not None:
                events_data[start_time[0]].append(data)
            else:
                events_data[start_time[0]] = [data]

        # print(json.dumps(d, indent=4))
        return events_data