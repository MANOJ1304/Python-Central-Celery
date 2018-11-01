from tasks.celery_queue_tasks import ZZQLowTask


class Sum(ZZQLowTask):
    """ testing Task. """
    name = 'Sum Data'
    description = """ connet to host machine and run the script."""
    public = True

    def run(self, *args, **kwargs):
        self.sum_eg(args[0], args[1])

    def sum_eg(self, a, b):
        print('sum of a+b is: {}'.format(a+b))
        print('--:-- '*20)
