from tasks.celery_queue_tasks import BaseChartTask
import logging
import json

import copy
from pyecharts.faker import Faker
from pyecharts.charts import Line
from snapshot_selenium import snapshot as driver
from pyecharts.render import make_snapshot
import time
from .utils import get_date, get_week_number, get_month_name, day_of_week

from weasyprint import HTML
import argparse
from jinja2 import Environment, FileSystemLoader

from helpers.mail_sender import send_mail
from email.headerregistry import Address

log = logging.getLogger(__name__)

CELERY_ROUTES = {
    'BaseTask': {'queue': 'priority_high'}
}
class GenerateReport(BaseChartTask):
    name = 'Generate Report'
    description = ''
    public = True
    autoinclude = True

    def __init__(self):
        self.base_path = ''
        pass

    def run(self, kwargs):
        # print('Task Started', args[0], args[1])
        # report_data = self.__prepare_data(kwargs["report_data"])
        self.report_details = kwargs["report"]
        self.build_dir()
        self.base_path = kwargs['report']['root_path']
        report_path = self.__create_report(kwargs['report_data'], kwargs['report_name'], )
        self.__send_report(kwargs['report_data'], report_path)
        return True
    
    def __create_report(self, report_data, report_name):
        env = Environment(loader=FileSystemLoader('{}'.format(self.base_path)))
        cover = env.get_template("templates/scorecard.html")
        env.globals.update(day_of_week=day_of_week, get_date=get_date)

        cover_out = cover.render(report_data)
        covers = HTML(string=cover_out).render(stylesheets=["{}/css/style.css".format(self.base_path)])
        # all_pages = [p for p in covers.pages]
        # mains = HTML(filename="../templates/cover.html").render(stylesheets=["../css/style.css"])
        # mains.write_pdf('report.pdf')
        report_path = '{}/{}/{}.pdf'.format(self.root_path, self.report_path_pdf, report_name)
        covers.write_pdf(report_path)
        return report_path


    def __send_report(self, report_data, report_path):
        mail_config = report_data['mail']
        receipients = ','.join([ i['email_address'] for i in mail_config['recipient']])
        mail_content = mail_config['body']
        subject = '{} Report - {}'.format(mail_config['subject']['type'], mail_config['subject']['site'])
        reply_email = mail_config['reply-to'][0]['email']
        print(' mail_content ', mail_content)
        send_mail(receipients, report_path, mail_content, subject, reply_email)
        

    def __prepare_data(self, visitors):

        if len(visitors) > 0:
            
            current_week= visitors[0]
            print(current_week)

            report_data = {}
            report_data['header_info'] = {}
            report_data['visitors_count'] = []
            report_data['header_info']['logo'] = "http://localhost:8000/wildfire.png"
            report_data['header_info']['report_title'] = 'Wildfire'
            report_data['header_info']['venue_name'] = 'Seaport village'
            
            # current_date = get_date(current_week['analytic_data'][0]['xAxis'][0])
            # report_data['header_info']['week_number'] = get_week_number(current_date)
            # report_data['header_info']['month'] = get_month_name(current_date)
            # report_data['header_info']['year'] = current_date.year

            # visitors_trend_title = ["Visitor this week", "Visitor last week", "This week last month", "This week last year"]
            # chart_names = ['current_week', 'last_week', 'last_month', 'last_year']

            report_data['visitors_info'] = []
            # for i, visitor_data in enumerate(visitors):
            #     if len(visitor_data['analytic_data']) > 0:
            #         if i == 0:
            #             report_data['visitors_count'] = [format(i, ',d') for i in visitor_data['analytic_data'][0]['series'][3]['total_visitor']]
            #         visitor_info = {}
            #         visitor_info['title'] = visitors_trend_title[i]
            #         visitor_info['count'] = format(visitor_data['analytic_data'][0]['series'][2]['value'], ',d')
            #         visitor_info['avg_change'] = str(visitor_data['analytic_data'][0]['series'][2]['avg_change']) + '%'
            #         visitor_info['img_url'] = 'http://localhost:8000/{}.png'.format(chart_names[i])
            #         report_data['visitors_info'].append(visitor_info)
            # report_data["weather_info"] = current_week['analytic_data'][0]['series'][3]['weather']
            # print('report_data ', report_data)
            return report_data
