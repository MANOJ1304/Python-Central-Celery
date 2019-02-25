""" redis://:password@hostname:port/db_number """
import yaml
import os
from celery import Celery
from kombu import Queue

with open(os.getcwd()+'/configs/config.yaml') as yamlfile:
    cfg = yaml.load(yamlfile)


# CELERY_BROKER_URL = 'redis://192.168.0.80:6379/0'
# CELERY_RESULT_BACKEND = 'redis://192.168.0.80:6379/0'

CELERY_BROKER_URL = 'redis://:{}@{}:{}/0'.format(cfg['redis']['password'],cfg['redis']['host'],cfg['redis']['port'])
CELERY_RESULT_BACKEND = 'redis://:{}@{}:{}/0'.format(cfg['redis']['password'],cfg['redis']['host'],cfg['redis']['port'])

CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default'),
    Queue('priority_high'),
)

# celery.py
# coding: utf-8
"""Configuracao inicial do Celery"""

app_task = Celery('analyzer', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
