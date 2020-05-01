import os
import sys
import tasks
import pkgutil
from importlib import import_module
# from tasks.computation.sum import Sum
from celery_config import app_task


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

# from celery.task.control import revoke
# import time
# if __name__ == '__main__':
#     task_b = Sum()
#     task_id=str(task_b.delay(3, 20, None))
#     print("\n Task ID",task_id)
#     print(type(task_id))
#     time.sleep(5)
#     # print(revoke(task_id, terminate=True))
#     # print(task_b.delay(0, 0, task_id))
