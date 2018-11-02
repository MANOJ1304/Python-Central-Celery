
from celery_config import app_task
from importlib import import_module
import pkgutil
import os
import sys
import tasks
from tasks.computation.sum import Sum


if __name__ == '__main__':
    task_b = Sum()
    task_b.delay(1, 201.0)
