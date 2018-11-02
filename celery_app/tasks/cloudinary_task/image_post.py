# import sys
# if sys.version_info[0] > 2:
#     from .tasks import ZZQHighTask
# else:
#     from tasks import ZZQHighTask

from tasks.celery_queue_tasks import ZZQHighTask
import cloudinary
import cloudinary.uploader
import cloudinary.api
# import yaml
# import os


class PostImageToCloud(ZZQHighTask):
    """ testing Task. """
    name = 'Cloudinary image post'
    description = ''' Upload images on Cloudinary.'''
    public = True

    # def __init__(self):
    #     print("\n Object crated")

    def run(self, *args, **kwargs):
        print("\nENTER IN RUN METHOD")
        self.post_image_to_cloud(args[0], args[1], args[2], args[3], args[4], args[5], args[6])
        return True

    def post_image_to_cloud(self, image, path, image_name, mime_type, cloud_name, api_key, api_secret):
        # with open(os.getcwd()+'/configs/appconfig.yaml') as yamlfile:
        #     cfg = yaml.load(yamlfile)

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        # print ("\n\nBefore Posting Image:", image, path, image_name)
        # cloudinary.uploader.upload(image, folder=path, public_id=image_name)
        # cloudinary.Uploader.upload("data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==")
        cloudinary.uploader.upload(
            "data:{};base64,{}".format(mime_type, image),
            folder=path,
            public_id=image_name
            )
        print("\n\nDone....")
