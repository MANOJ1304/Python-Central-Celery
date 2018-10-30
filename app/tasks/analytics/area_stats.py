from tasks.celery_queue_tasks import ZZQLowTask


class AreaStats(ZZQLowTask):
    """ testing Task. """
    name = 'Area Stats'
    description = """ connet to host machine and run the script."""
    public = True

    def run(self, *args, **kwargs):
        print('-hello,,,,,.....- '*20)
        self.area_eg(args[0], args[1])

    def area_eg(self, a, b):
        print('Area Stats of a*b is: {}'.format(a*b))
        print('-\/\/-:-/\/\- '*20)
