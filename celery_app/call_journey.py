from celery_config import app_task
from importlib import import_module
import pkgutil
import os
import sys
import tasks
from tasks.analytics.journey import Journey

if __name__ == '__main__':
    task_area = Journey()
    task_area.delay(500, 200)
