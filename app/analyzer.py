import os
import sys
import tasks
import pkgutil
from importlib import import_module
# from tasks.computation.sum import Sum
from celery_config import app


def my_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def register_tasks():
    # print(os.path.dirname(__file__))
    for (_, name, _) in pkgutil.iter_modules(['tasks']):
        # print('.' + name)
        # print(sys.modules[__name__])
        if name != 'dynamicimport':
            # print('Hello',name)
            imported_module = import_module('.' + name, package='tasks')
            class_name = list(filter(lambda x: x != 'dynamicimport' and not x.startswith('__'),
                             dir(imported_module)))
            imported_module = import_module('.' + name, package='tasks')
            # print("--.>>-> {}".format(class_name))


register_tasks()
# if __name__ == '__main__':
#     task_b = Sum()
#     task_b.delay(1, 20)
