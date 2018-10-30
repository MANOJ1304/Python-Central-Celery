FROM python:3.5.4

# ADD requirements.txt /apps/requirements.txt
RUN apt-get install --yes  git
RUN export BROKER_URL='redis://redis:6379/0'
RUN export CELERY_RESULT_BACKEND='redis://redis:6379/0'

# ADD ./test_celery/ /app/
# RUN mkdir  /app/conf
# RUN chown -R root:root /app/conf
# RUN git clone  https://intelipowerbuild:ZyC4z3kVRQRR@github.com/Intelipower/python-redis-pub-sub-collector /app
COPY app /app
WORKDIR /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# COPY celeryd.conf /etc/init.d/celery-worker
# RUN chmod +x /etc/init.d/celery-worker
# COPY conf/location_log.yaml /app/config.yaml
COPY wait-for-it/wait-for-it.sh /usr/bin/wait-for-it
RUN chmod +x /usr/bin/wait-for-it
# COPY scripts/runconnector.py /app/connector.py



# ENTRYPOINT python connector.py

# ENTRYPOINT python-locationlogelasticpost yes mongo_data /app/conf/location_log.yaml
# ENTRYPOINT ['celery','-A','test_celery', 'worker', '--loglevel=info']