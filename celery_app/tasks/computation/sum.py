from tasks.celery_queue_tasks import ZZQLowTask
from celery.task.control import revoke
import time
class Sum(ZZQLowTask):
    """ testing Task. """
    name = 'Sum Data'
    description = """ connet to host machine and run the script."""
    public = True
    autoinclude = True

    def run(self, *args, **kwargs):
        self.sum_eg(args[0], args[1], task_id=args[2])

    def sum_eg(self, a, b, task_id=None):
        if task_id:
            print("\n Task ID",task_id)
            print(revoke(task_id, terminate=True))
        else:
            print("\n Process started....")
            time.sleep(30)
            print('sum of a+b is: {}'.format(a+b))
            print('--:-- '*20)