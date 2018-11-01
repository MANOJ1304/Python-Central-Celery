
from celery_config import app_task
from importlib import import_module
import pkgutil
import os
import sys
import tasks
from tasks.analytics.area_stats import AreaStats
          
if __name__ == '__main__':
    task_area = AreaStats()
    task_area.delay(100, 201)
