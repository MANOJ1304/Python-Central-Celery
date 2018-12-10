"""
    # import sys
    # if sys.version_info[0] > 2:
    #     from .tasks import HighTask
    # else:
    #     from tasks import HighTask
"""

from time import sleep
import requests
from socketIO_client_nexus import SocketIO, LoggingNamespace, BaseNamespace, ConnectionError
from tasks.celery_queue_tasks import ZZQHighTask
from tasks.monitoring.utils import UtilData


class DataMonitor(ZZQHighTask):
    """ testing Task. """
    name = 'data Monitoring'
    description = """ connet to host machine and run the script."""
    public = True
    autoinclude = True

    def __init__(self):
        self.util_obj = UtilData()

    def run(self, *args, **kwargs):
        # self.start_process(args[0], args[1])
        self.start_process()
        return True

    class MainNamespace(BaseNamespace):
        def on_aaa(self, *args):
            print('aaa')

    class LocationNamespace(BaseNamespace):
        def on_aaa_response(self, *args):
            # TODO:
            print('on_aaa_response', args)

    # for jwt token
    def get_auth_code(self):
        requests_body = {
            "username": self.util_obj.get_auth_code["username"],
            "password": self.util_obj.get_auth_code["password"]
            }
        r = requests.post(
            self.util_obj.get_auth_code["api"],
            json=requests_body
            )
        try:
            auth_token = r.json()['jwt']
            return auth_token
        except Exception as e:
            print("Error occured !! Response auth api => {}".format(e))
            return None

    def on_connect(self, response):
        print('connect %s' % response)

    def on_disconnect(self):
        print('disconnect')

    def on_reconnect(self):
        print('reconnect')

    def on_aaa_response(self, *args):
        print('on_aaa_response', args)

    def listen_location_data(self, *args):
        print("listen_location_data args are: {}".format(args))
        while True:
            chat_namespace.emit(
                self.util_obj.chat_message['name'],
                self.util_obj.chat_message['data']
                )
            sleep(1)

    def get_server_version(self, args):
        print(args)

    def getCMSSummary(self, args):
        print(args)

    def start_process(self):
        jwt_token = self.get_auth_code()
        print("jwt token is: {}\n".format(jwt_token))
        params1 = self.util_obj.socket_connection['params1']
        params1["token"] = jwt_token

        # socketIO = SocketIO('192.168.0.60', 8080, params=params1)
        socketIO = SocketIO(
            self.util_obj.socket_connection['ip'],
            self.util_obj.socket_connection['port'],
            params=params1)

        socketIO.emit('server.version', {})
        socketIO.on('server.version', self.get_server_version)
        pLocationNamespace = socketIO.define(self.LocationNamespace, '/location')
        filterData = self.util_obj.filterData

        pLocationNamespace.emit('location:monitor:send:filter', filterData)
        pLocationNamespace.on('location:monitor:receive', self.on_aaa_response)
        try:
            socketIO.wait()
            # engineSocket.wait()
        except ConnectionError as ex:
            print("got connection error %s" % ex)
