from tasks.celery_queue_tasks import ZZQHighTask
import requests

class AddTaskToScheduler(ZZQHighTask):
    """ testing Task. """
    name = 'Add Task in to scheduler'
    description = ''' Posting new task information in to scheduler.'''
    public = True
    autoinclude = True

    def run(self, *args, **kwargs):
        # print("\nENTER IN RUN METHOD")
        self.post_task_info(args[0], args[1])
        return True

    def post_task_info(self, scheduler_url, post_data):
        try:
            # print("\n\nScheduler url", msg[0])
            r = requests.post(scheduler_url, json=post_data)
            print("\n\nScheduler post response", r.json())
        except:
            print("error occured while posting job to SCHEDULER...in celery")

