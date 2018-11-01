from tasks.celery_queue_tasks import ZZQHighTask


class Journey(ZZQHighTask):
    """ testing Task. """
    name = 'Guest Journey'
    description = """ connet to host machine and run the script."""
    public = True

    def run(self, *args, **kwargs):
        self.sum_eg(args[0], args[1])

    def sum_eg(self, a, b):
        print('journey of a/b is: {}'.format(a/b))
        print('\\\\:// '*20)
