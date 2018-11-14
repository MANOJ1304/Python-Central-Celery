FROM redis
RUN mkdir -p /celery_app
RUN mkdir -p /local/etc/redis/conf
RUN mkdir -p /opt/bitnami/redis/logs
RUN chmod 0777 /opt/bitnami/redis/logs
# RUN echo never > /sys/kernel/mm/transparent_hugepage/enabled
COPY conf/redis.conf /usr/local/etc/redis/conf/redis.conf
COPY start.sh /celery_app/
RUN chmod +x /celery_app/start.sh
WORKDIR /celery_app
CMD [ "redis-server" ]
#CMD ["./start.sh"]
