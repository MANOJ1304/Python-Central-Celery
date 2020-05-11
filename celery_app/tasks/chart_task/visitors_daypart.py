from tasks.celery_queue_tasks import BaseChartTask
from tasks.chart_task.utils import round_number, convert_capitalize
from wildfire.wildfire_api import WildfireApi
from .widgets.chart import PieChart
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from boltons.iterutils import research, get_path
import logging
import json
import dateparser
import copy

from snapshot_selenium import snapshot as driver
from pyecharts.render import make_snapshot
import time
log = logging.getLogger(__name__)

CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'},
}

class VisitorsDayPart(BaseChartTask):
    name = 'Visitors Day Part Task'
    description = ''' Draws data for weekday and weekend with day part segregation'''
    public = True
    autoinclude = True

    def __init__(self):
        super(VisitorsDayPart, self).__init__()
        self.map_image = 'visitors_daypart'
        pass

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])
        self.report_details = kwargs["report"]
        self.build_dir()
        if not self.dev:
            cdata = self.__get_data(**kwargs["creds"], **kwargs["data_params"])
            self.__draw_chart(cdata)
        kwargs['output']['img_url'] = '{}/{}/{}.png'.format(
            kwargs['config']['base_url'],
            self.report_path_image,
            self.map_image
        )
        return kwargs['output']
        

    def __draw_chart(self, data):
        # print(data)
        if len(data['analytic_data']) > 0:
            wdata = data
            pie_data = {'labels': [], 'data': []}
            weekend_data = copy.deepcopy(pie_data)
            weekday_data = copy.deepcopy(pie_data)

            weekend_res_data = wdata['analytic_data'][0]['series'][0]['weekend']
            weekday_res_data = wdata['analytic_data'][0]['series'][0]['weekday']

            weekend_data['labels'] = [convert_capitalize(item[1]) for item in research(weekend_res_data, query=lambda p, k, v: k == 'name' )]
            weekend_data['data'] = [item[1] for item in research(weekend_res_data, query=lambda p, k, v: k == 'value' )]

            weekday_data['labels'] = [convert_capitalize(item[1]) for item in research(weekday_res_data, query=lambda p, k, v: k == 'name' )]
            weekday_data['data'] = [item[1] for item in research(weekday_res_data, query=lambda p, k, v: k == 'value' )]

            weekend_total = sum(weekend_data['data'])
            weekday_total = sum(weekday_data['data'])

            weekday_percent = [round_number((i/weekday_total) * 100) for i in weekday_data['data']]
            weekend_percent = [round_number((i/weekend_total) * 100) for i in weekend_data['data']]

            pchart = PieChart("")
            pchart.chart.add(
                "",
                [list(z) for z in zip(weekday_data['labels'], weekday_data['data'], weekday_percent)],
                center=["30%", "40%"],
                radius=pchart.doughnut_radius,
                label_opts=opts.LabelOpts(
                    formatter=JsCode(" function(params) { return params.value + '\\n' + params.percent + '%';} "),
                    is_show=True 
                )
            )
            pchart.chart.add(
                "",
                [list(z) for z in zip(weekend_data['labels'],  weekend_data['data'], weekend_percent)],
                center=["75%", "40%"],
                radius=pchart.doughnut_radius,
                label_opts=opts.LabelOpts(
                    formatter=JsCode(" function(params) { return params.value + '\\n' + params.percent + '%';} "),
                    is_show=True 
                )
            )
            pchart.chart.set_global_opts(
                legend_opts=opts.LegendOpts(
                    type_="scroll",pos_bottom='10%', orient="horizontal", pos_left='15%')
                
            )
            pchart.chart.set_colors(pchart.colors)
            # pchart.chart.render("{}/{}/{}.html".format(self.root_path, self.report_path_html, self.map_image))
            pchart.generate(file_name="{}/{}/{}.html".format(self.root_path, self.report_path_html, self.map_image),
                image_name="{}/{}/{}.png".format(self.root_path, self.report_path_image, self.map_image))
            # pchart.get_chart_instance()
            
            # make_snapshot(driver, "{}/{}/{}.html".format(self.root_path, self.report_path_html, self.map_image),
            #     "{}/{}/{}.png".format(self.root_path, self.report_path_image, self.map_image))
            # bar.generate(file_name="visualization/html/render.html", image_name="visualization/images/example.png")


    def __get_data(self, username, password, cfg:dict, venue_id:str, elasttic_filters: dict, date_range:list, agg_type:str, exclude_params:list, ):
        # log.debug("{} {}".format(username, password))
        w =  WildfireApi(username, password, cfg)
        d = (w.venues()
        .analytics(venue_id=venue_id)
        .day_part_visitors()
        .set_filter(date_range, "", elasttic_filters, exclude_params, pre_compute=True, pre_compute_filter={"type": "daywise_visitor"})
        .request())
        # print(json.dumps(d, indent=4))
        # print(d)
        return d
