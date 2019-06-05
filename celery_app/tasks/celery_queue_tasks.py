from celery_config import app_task


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
