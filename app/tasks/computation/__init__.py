from ..base_tasks import BaseTasks
from importlib import import_module
from celery_config import app
import pkgutil
import os
import sys

"""
All this is doing is: 
        from .goldfish import GoldFish as goldfish

I just added it there because I'm too lazy to add this line whenever I need to add a new fish to the family.

"""

for (_, name, _) in pkgutil.iter_modules([os.path.dirname(__file__)]):
    # print("asd")
    imported_module = import_module('.' + name, package='tasks.computation')

    class_name = list(filter(lambda x: x != 'BaseTasks' and not x.startswith('__'),
                             dir(imported_module)))

    sum_class = getattr(imported_module, class_name[0])
    # print(sum_class)
    app.register_task(sum_class())
    if issubclass(sum_class, BaseTasks):
        print(sum_class)
        setattr(sys.modules[__name__], name, sum_class)
        