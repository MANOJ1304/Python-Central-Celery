from tasks.celery_queue_tasks import ZZQHighTask
import requests

class DeleteTaskFromScheduler(ZZQHighTask):
    """ testing Task. """
    name = 'Delete Task in to scheduler'
    description = ''' Delete task info from scheduler.'''
    public = True
    autoinclude = True

    def run(self, *args, **kwargs):
        # print("\nENTER IN RUN METHOD")
        self.delete_task_info(args[0], args[1])
        return True

    def delete_task_info(self, scheduler_url, filter_data):
        try:
            r1 = requests.get(scheduler_url + '?where={{\"job\": \"{}\"}}&projection={{\"_id\":1}}'.format(filter_data))
            sc_response = r1.json()
            if '_items' in sc_response.keys() and len(sc_response['_items']) > 0:
                delete_id = sc_response['_items'][0]['_id']
                r2 = requests.delete(scheduler_url + "/" + delete_id)
        except:
            print("error occured while deleting job from SCHEDULER...in celery")
