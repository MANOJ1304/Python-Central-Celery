from tasks.celery_queue_tasks import BaseChartTask
import logging
import json

import copy
from pyecharts.faker import Faker
from pyecharts.charts import Line
from snapshot_selenium import snapshot as driver
from pyecharts.render import make_snapshot
import time
from .utils import get_date, get_week_number, get_month_name, day_of_week, get_12_hour, get_date_with_format

from weasyprint import HTML
import argparse
from jinja2 import Environment, FileSystemLoader

from helpers.mail_sender import send_mail, send_email_message
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
        print('Report created')
        self.__send_report(kwargs['report_data'], report_path)
        return True
    
    def __create_report(self, report_data, report_name):
        env = Environment(loader=FileSystemLoader('{}'.format(self.base_path)))
        cover = env.get_template("templates/scorecard.html")
        env.globals.update(day_of_week=day_of_week, get_date=get_date,
            get_12_hour=get_12_hour, get_date_with_format=get_date_with_format)

        cover_out = cover.render(report_data)
        covers = HTML(string=cover_out).render(stylesheets=["{}/css/style.css".format(self.base_path)])
        # all_pages = [p for p in covers.pages]
        # mains = HTML(filename="../templates/cover.html").render(stylesheets=["../css/style.css"])
        # mains.write_pdf('report.pdf')
        # with open('{}/{}/pdf.html'.format(self.root_path, self.report_path_pdf), 'w') as f:
        #     f.write(cover_out)
        report_path = '{}/{}/{}.pdf'.format(self.root_path, self.report_path_pdf, report_name)
        covers.write_pdf(report_path)
        return report_path


    def __send_report(self, report_data, report_path):
        mail_config = report_data['mail']
        # receipients = ','.join([ i['email_address'] for i in mail_config['recipient']])
        receipients = tuple([ Address(i['name'], i['email_address'].split('@')[0], i['email_address'].split('@')[1])  for i in mail_config['recipient']])
        mail_content = mail_config['body']
        subject = '{} Report - {}'.format(mail_config['subject']['type'], mail_config['subject']['site'])
        reply_email = mail_config['reply-to'][0]['email']
        print(' mail_content ', mail_content)
        # send_mail(receipients, report_path, mail_content, subject, report_data['root_path'], reply_email )
        send_email_message(receipients, report_path, mail_content, subject, report_data, reply_email)
        
