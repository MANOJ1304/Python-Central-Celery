# python-tool-central-celery-process

Running instructions:
    $ run central celery module.

# Usage:

    step 1. Go to python-central-celery-docker and install requirements.
    step 2. Activate virtual environment:
                $ source ~/virtenv/t_venv3.6/bin/activate
    step 3. Run redis server:
                $ redis-server --protected-mode no --daemonize yes
    step 4. go to directory:
                $ cd python-central-celery-docker/celery_app
    step 5. starated celery process in diffrent terminals:
                $ celery worker -A analyzer -Q priority_high -l INFO
                $ celery worker -A analyzer -Q default -l INFO
                $ celery worker -A analyzer -Q iviu_queue -l INFO
