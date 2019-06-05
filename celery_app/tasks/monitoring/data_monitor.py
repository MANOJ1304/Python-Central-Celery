"""
requests, socketIO_client_nexus
"""

from time import sleep
from datetime import datetime
import threading
import json
import requests
from celery.task.control import revoke
from socketIO_client_nexus import SocketIO, BaseNamespace  #, LoggingNamespace, ConnectionError
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
        self.task_id = self.request.id
        # self.start_process(args[0], args[1])
        self.config_json = args[0]
        # creating threads
        t1 = threading.Thread(target=self.start_process)
        t2 = threading.Thread(target=self.run_counter)
        # setting daemon
        t1.setDaemon(True)
        t2.setDaemon(True)
        # start threads
        t1.start()
        t2.start()
        # wait until threads finish their job
        t1.join()
        t2.join()
        return True

    class LocationNamespace(BaseNamespace):
        """ location name space. """
        def on_aaa_response(self, *args):
            """ location name space get server response. """
            print('inside class on_aaa_response', args)

    def on_connect(self, response):
        """ connected to server. """
        print('connect %s' % response)

    def on_disconnect(self):
        """ disconnected from server.  """
        print('disconnect')

    def on_reconnect(self):
        """ reconnected to server. """
        print('reconnect')

    def get_server_version(self, args):
        """ get server version info. """
        print("get_server_version: ", args)

    def run_counter(self):
        """ wait till given time and than kill the task."""
        while True:
            sleep(1)
            end_datetime = datetime.strptime(
                self.config_json['query']['end_time'],
                "%Y-%m-%d %H:%M:%S"
            )
            # printing counter process of the scehema... ...
            print("run counter: end time: {}\tcurrent utc time: {}\tand condn: {}".format(
                end_datetime, datetime.utcnow(), datetime.utcnow() > end_datetime)
            )
            if datetime.utcnow() > end_datetime:
                print("killing celery process..")
                revoke(self.task_id, terminate=True)

    def on_aaa_response(self, *args):
        """ received response from server.  """
        # print('start_process ..... ', args)
        self.patch_data.patch_record(self.jwt_token, self.config_json, json.loads(args[0]))
        quiz_id = self.config_json["query"]["cod_pin"]
        # TODO: slack working.
        self.util_obj.slack_alert(
            self.config_json["slack_info"]["token"],
            self.config_json["slack_info"]["channel_name"],
            self.config_json["slack_info"]["msg"].format(quiz_id),
            )

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
            # print(r.json()['jwt'])
            return r.json()['jwt']
        except KeyError as e:
            print("Error occured !! Response auth api => {}".format(e))
            print(r.json())
            # TODO: send mail....
        except Exception as e:
            print("Unknown Error occured !! Response auth api => {}".format(e))
            self.get_auth_code()
            return True

    def start_process(self):
        """main process start from here. """
        self.jwt_token = self.get_auth_code()
        # print("jwt token is: {}\n".format(self.jwt_token))
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
