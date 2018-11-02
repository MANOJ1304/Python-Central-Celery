from celery import Celery
from kombu import Exchange, Queue
# settings.py
# CELERY_BROKER_URL = 'redis://192.168.0.116:6379/0'
# CELERY_RESULT_BACKEND = 'redis://192.168.0.116:6379/0'
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default'),
    Queue('priority_high'),
)

# celery.py
# coding: utf-8
"""Configuração inicial do Celery"""

app_task = Celery('analyzer', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
