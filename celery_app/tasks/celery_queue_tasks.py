from celery_config import app_task
from time import sleep
import pathlib

class ZZQLowTask(app_task.Task):

    ignore_result = False
    validation_class = ''
    name = ''
    description = ''
    queue = 'default'
    # def run(self, *args, **kwargs):
    #     controller_id = kwargs.pop('cid', None)
    #     next_id = kwargs.pop('nsi', None)
    #     self._load_data(controller_id, next_id)
    #     return self._run()

    # def _load_data(self, controller_id, next_id):

    #     self.controller = StateController.objects.get(id=controller_id)
    #     self.previous = self.controller.current_state
    #     self.next = State.objects.get(id=next_id)

    def _run(self):
        return True


class ZZQHighTask(app_task.Task):

    ignore_result = False
    validation_class = ''
    name = ''
    description = ''
    queue = 'priority_high'
    # def run(self, *args, **kwargs):
    #     controller_id = kwargs.pop('cid', None)
    #     next_id = kwargs.pop('nsi', None)
    #     self._load_data(controller_id, next_id)
    #     return self._run()

    # def _load_data(self, controller_id, next_id):

    #     self.controller = StateController.objects.get(id=controller_id)
    #     self.previous = self.controller.current_state
    #     self.next = State.objects.get(id=next_id)

    def _run(self):
        return True


class ZZQIVIU(app_task.Task):

    ignore_result = False
    validation_class = ''
    name = ''
    description = ''
    queue = 'iviu_queue'
    # def run(self, *args, **kwargs):
    #     controller_id = kwargs.pop('cid', None)
    #     next_id = kwargs.pop('nsi', None)
    #     self._load_data(controller_id, next_id)
    #     return self._run()

    # def _load_data(self, controller_id, next_id):

    #     self.controller = StateController.objects.get(id=controller_id)
    #     self.previous = self.controller.current_state
    #     self.next = State.objects.get(id=next_id)

    def _run(self):
        return True


class BaseChartTask(app_task.Task):

    queue = 'priority_high'
    ignore_result = False
    validation_class = ''
    name = ''
    description = ''

    def __init__(self):
        self.dev = False
        super(BaseChartTask, self).__init__()
        self.report_details ={}
    # def run(self, *args, **kwargs):
    #     controller_id = kwargs.pop('cid', None)
    #     next_id = kwargs.pop('nsi', None)
    #     self._load_data(controller_id, next_id)
    #     return self._run()

    # def _load_data(self, controller_id, next_id):

    #     self.controller = StateController.objects.get(id=controller_id)
    #     self.previous = self.controller.current_state
    #     self.next = State.objects.get(id=next_id)

    def _run(self):
        print('--Start')
        sleep(30)
        return True 

    def build_dir(self):
        self.report_path_html = "/".join([self.report_details.get("parent_path"), self.report_details.get("_id"), self.report_details.get("html")])
        self.report_path_image = "/".join([self.report_details.get("parent_path"), self.report_details.get("_id"), self.report_details.get("images")])
        self.report_path_pdf= "/".join([self.report_details.get("parent_path"), self.report_details.get("_id"), self.report_details.get("pdf")])
        self.root_path = self.report_details['root_path']
        # os.mkdir(self.report_path_html)
        # os.mkdir(self.report_path_image)
        pathlib.Path('{}/{}'.format(self.root_path, self.report_path_html)).mkdir(parents=True, exist_ok=True)
        pathlib.Path('{}/{}'.format(self.root_path, self.report_path_image)).mkdir(parents=True, exist_ok=True)
        pathlib.Path('{}/{}'.format(self.root_path, self.report_path_pdf)).mkdir(parents=True, exist_ok=True)