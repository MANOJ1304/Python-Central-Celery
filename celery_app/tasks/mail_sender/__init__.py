""" intialise file from here. Taking class names in alphabetic order """
import os
import sys
import pkgutil
from importlib import import_module
from celery_config import app_task
from ..base_tasks import BaseTasks


for (_, name, _) in pkgutil.iter_modules([os.path.dirname(__file__)]):
    # print("asd")
    imported_module = import_module('.' + name, package='tasks.mail_sender')
    # print("analytics...>>", imported_module)
    # print("dir analytics...>>", dir(imported_module))
    class_name = list(filter(lambda x: x != 'BaseTasks' and not x.startswith('__'),
                             dir(imported_module)))
    # sum_class = getattr(imported_module, class_name[len(class_name)-1])
    for c_name in class_name:
        sum_class = getattr(imported_module, c_name)
        if hasattr(sum_class, 'autoinclude') and sum_class.autoinclude:
            app_task.register_task(sum_class())
            if issubclass(sum_class, BaseTasks):
                setattr(sys.modules[__name__], name, sum_class)
