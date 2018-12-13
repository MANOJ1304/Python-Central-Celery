"""
requests, socketIO_client_nexus
"""

from time import sleep
from datetime import datetime
import requests
from socketIO_client_nexus import SocketIO, LoggingNamespace, BaseNamespace, ConnectionError
from tasks.celery_queue_tasks import ZZQHighTask
from tasks.monitoring.utils import UtilData
from tasks.monitoring.patch_record import DataPatch


class DataMonitor(ZZQHighTask):
    """ testing Task. """
    name = 'data Monitoring'
    description = """ connet to host machine and run the script."""
    public = True
    autoinclude = True

    def __init__(self):
        self.util_obj = UtilData()
        self.patch_data = DataPatch()
        self.config_json = ""
        self.jwt_token = ""

    def run(self, *args, **kwargs):
        # self.start_process(args[0], args[1])
        self.config_json = args[0]
        self.start_process()
        return True

    class MainNamespace(BaseNamespace):
        def on_aaa(self, *args):
            print('aaa')

    class LocationNamespace(BaseNamespace):
        def on_aaa_response(self, *args):
            # TODO:
            self.patch_data.patch_record(self.jwt_token, self.config_json, args)
            end_datetime = datetime.strptime(
                self.config_json['query']['end_time'],
                "%Y-%m-%d %H:%M:%S"
            )
            if end_datetime > datetime.utcnow():
                print("exiting process..")
            print('on_aaa_response', args)


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

    def get_auth_code(self):
        """ for jwt token """
        try:
            r = requests.post(
                self.util_obj.first_url+self.config_json["api_data"]["login_url"],
                json=self.util_obj.auth_code_credential)
            return r.json()['jwt']
        except requests.exceptions.RequestException as e:
            # print("Waiting for network....: {}.".format(e))
            print("Waiting for network....")
            sleep(0.1)
            self.get_auth_code()
            return True

        try:
            print(r.json()['jwt'])
        except KeyError as e:
            print("Error occured !! Response auth api => {}".format(e))
            print(r.json())
            # TODO:
            # send mail....
        except Exception as e:
            print("Unknown Error occured !! Response auth api => {}".format(e))
            self.get_auth_code()
            return True

    def start_process(self):
        self.jwt_token = self.get_auth_code()
        print("jwt token is: {}\n".format(self.jwt_token))
        params1 = self.util_obj.socket_connection['params1']
        params1["token"] = self.jwt_token

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
