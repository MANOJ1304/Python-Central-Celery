from __future__ import absolute_import
from celery import Celery
app = Celery('test_celery',broker='redis://redis:6379',backend='rpc://',include=['python_locationlogelasticpost.tasks'])
