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
from pyecharts.charts import Bar
from snapshot_selenium import snapshot as driver
from pyecharts.render import make_snapshot
import time
from  .utils import get_ts, get_12_hour
import pandas as pd

from datetime import timedelta, datetime

log = logging.getLogger(__name__)

CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}


class VisitorHourChart(BaseChartTask):
    name = 'Visitior Hourly Chart'
    description = '''Matches address from sources A and B and constructs
a list of Address Matches for other analysis and manual review.'''
    public = True
    autoinclude = True

    def __init__(self):
        super(VisitorHourChart, self).__init__()
        self.current_week = {'x_axis': [], 'visitors': []}
        self.last_week = {'x_axis': [], 'visitors': []}
        self.map_image = 'visitors_hour'
        pass

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])
        self.report_details = kwargs["report"]
        self.build_dir()
        if not self.dev:
            self.__get_data(**kwargs["creds"], **kwargs["data_params"])
            
            self.__draw_chart(kwargs["chart_options"])
        
        kwargs['output']['img_url'] = '{}/{}/{}.png'.format(kwargs['config']['base_url'], self.report_path_image, self.map_image) 
        # print(kwargs['output'])

        return kwargs['output']

    def __draw_chart(self, chart_options):
        # Current week operations
        # print('Current week ', self.current_week)

        # print('LAst week ', self.last_week)

        df = pd.DataFrame(self.current_week)
        df['x_axis'] = df['x_axis'].apply(lambda x:  x[:23])
        df['x_axis'] = pd.to_datetime(df['x_axis'])
        df['hour'] = df['x_axis'].dt.hour
        df = df[(df['hour'] >= 10) & (df['hour'] <= 21)]
        grp = df.groupby('hour').sum().reset_index()

        # Last week operations
        df = pd.DataFrame(self.last_week)
        df['x_axis'] = df['x_axis'].apply(lambda x:  x[:23])
        df['x_axis'] = pd.to_datetime(df['x_axis'])
        df['hour'] = df['x_axis'].dt.hour
        df = df[(df['hour'] >= 10) & (df['hour'] <= 21)]
        prev_grp = df.groupby('hour').sum().reset_index()

        x_axis = list(set(list(grp['hour'].values) + list(prev_grp['hour'].values)))
        x_axis = [str(i) for i in x_axis]

        cw = list(grp['visitors'].values)
        pw = list(prev_grp['visitors'].values)
        cw = [int(i) for i in cw]
        pw = [int(i) for i in pw]
        l_cw = len(cw)
        l_pw = len(pw)
        if l_cw > l_pw:
            for i in range(l_cw - l_pw):
                pw.append(0)
        elif l_pw > l_cw:
            for i in range(l_pw - l_cw):
                cw.append(0)

       
        bar = BarChart(bar_title=self.map_image)
        
        # for i in x_axis:
        #     hr = get_12_hour('{}:00:00'.format(i))
        #     hr = hr.split(' ')
        #     hr = '{} {}'.format(hr[0], '.'.join(list(hr[1])) )   
        #     x_axis_label.append(hr)
        x_axis_label = []
        x_axis_label = [get_12_hour('{}:00:00'.format(i)).lstrip('0') for i in x_axis ]
        bar.xaxis(x_axis_label)
        # bar.ydata("Current Week", cw , options={"gap":"0%", "label_opts":bar.label_style['x_data']})
        # bar.ydata("Previous week", pw , options={"gap":"10%", "label_opts":bar.label_style['x_data']})
        # add_yaxis(title, data, category_gap="60%", itemstyle_opts=self.bar_colors.pop(),  **options )
        bar.get_chart_instance().add_yaxis("Current Week", cw, gap="0%", label_opts=bar.label_style['x_data'],
            category_gap="30%", itemstyle_opts=bar.bar_colors.pop())
        bar.get_chart_instance().add_yaxis("Previous Week", pw, gap="10%", label_opts=bar.label_style['x_data'],
            category_gap="30%", itemstyle_opts=bar.bar_colors.pop())
        bar.get_chart_instance().set_global_opts(xaxis_opts=opts.AxisOpts(name='Hours',
            position='bottom', axislabel_opts=opts.LabelOpts(font_size=8, rotate=-15)),)
        # print(bar.get_chart_instance().dump_options())
        bar.generate(file_name="{}/{}/{}.html".format(self.root_path, self.report_path_html, self.map_image),
            image_name="{}/{}/{}.png".format(self.root_path, self.report_path_image, self.map_image))
        # Reset data
        self.__reset_data()
# 
        
        # c = (
        #     Bar()
        #     .add_xaxis(x_axis)
        #     .add_yaxis("Current Week", cw, gap="0%", label_opts=)
        #     .add_yaxis("Prev week", pw, gap="30%")
        #     .set_global_opts(xaxis_opts=opts.AxisOpts(name='Hour', position='bottom', name_location='center', name_gap=40))
        #     .render("{}/{}.html".format(self.report_path_html, self.map_image))
        # )
        # c.render(path="bar1.png")

        # make_snapshot(driver, "{}/{}.html".format(self.report_path_html, self.map_image),
        #     "{}/{}.png".format(self.report_path_image, self.map_image))
        # print(data)
        # make_snapshot(driver, "{}/{}.html".format(self.report_path_html, chart_name),
        #     "{}/{}.png".format(self.report_path_image, chart_name))
        # bar.generate(file_name="visualization/html/render.html", image_name="visualization/images/example.png")

    def __get_data(self, username, password, cfg: dict,
                   venue_id: str, elasttic_filters: dict, date_range: list, agg_type: str, exclude_params: list, last_week_range: list, ):
        log.debug("{} {}".format(username, password))
        
        # current week data gathering
        current_week_range = [ datetime.fromtimestamp(i/1000)  for i in date_range]
        last_week_date_range = [ datetime.fromtimestamp(i/1000)  for i in last_week_range]
        start_date = current_week_range[0]
        while start_date <=  current_week_range[1]:
            # print( )
            w = WildfireApi(username, password, cfg)
            local_date_range = [get_ts(start_date), get_ts(start_date + timedelta(days=1, seconds=-1))]
            elasttic_filters['gte'] = local_date_range[0]
            elasttic_filters['lte'] = local_date_range[1]
            d = (w.venues()
                .analytics(venue_id=venue_id)
                .wifi()
                .set_filter(local_date_range, 'general', elasttic_filters, exclude_params)
                .request())

            start_date = start_date + timedelta(days=1)
            # print('d ', d)
            if len(d['analytic_data'] ) > 0:
                self.current_week['x_axis'] = self.current_week['x_axis'] + d['analytic_data'][0]['xAxis']
                self.current_week['visitors'] = self.current_week['visitors'] + d['analytic_data'][0]['series'][3]['total_visitor']

        # Last week data gathering
        start_date = last_week_date_range[0]
        while start_date <= last_week_date_range[1]:
            # print( )
            w = WildfireApi(username, password, cfg)
            local_date_range = [get_ts(start_date), get_ts(start_date + timedelta(days=1, seconds=-1))]
            elasttic_filters['gte'] = local_date_range[0]
            elasttic_filters['lte'] = local_date_range[1]
            d = (w.venues()
                .analytics(venue_id=venue_id)
                .wifi()
                .set_filter(local_date_range, agg_type, elasttic_filters, exclude_params)
                .request())

            start_date = start_date + timedelta(days=1)
            if len(d['analytic_data']) > 0:
                self.last_week['x_axis'] = self.last_week['x_axis'] + d['analytic_data'][0]['xAxis']
                self.last_week['visitors'] = self.last_week['visitors'] + d['analytic_data'][0]['series'][3]['total_visitor']
        # print(json.dumps(d, indent=4))
        # return d

    def __reset_data(self):
        self.current_week = {'x_axis': [], 'visitors': []}
        self.last_week = {'x_axis': [], 'visitors': []}