FROM redis
RUN mkdir -p /apps
RUN mkdir -p /local/etc/redis/conf
RUN mkdir -p /opt/bitnami/redis/logs
RUN chmod 0777 /opt/bitnami/redis/logs
# RUN echo never > /sys/kernel/mm/transparent_hugepage/enabled
COPY conf/redis.conf /usr/local/etc/redis/conf/redis.conf
COPY start.sh /apps/
RUN chmod +x /apps/start.sh
WORKDIR /apps
CMD [ "redis-server" ]
#CMD ["./start.sh"]
