"""
    data post on oracle db.
    Module req.- pony, requests, cx_Oracle
"""

from time import sleep
from math import ceil
import requests
from pony import orm
from tasks.celery_queue_tasks import ZZQHighTask
from tasks.db_data_post.utils import UtilData


class DataConnector(ZZQHighTask):
    """connect to db and post on api."""
    name = 'Data connector'
    description = """ connet to host machine and run the script."""
    public = True
    autoinclude = True
    db = orm.Database()

    def __init__(self):
        self.util_obj = UtilData()
        self.config_json = ""
        orm.set_sql_debug(False)


    def run(self, *args, **kwargs):
        """ initialize db connction"""
        self.config_json = args[0]


        # # __ connected to oracle db.
        # self.db.bind(
        #     provider='oracle',
        #     user=self.config_json["oracle_info"]["db_user_name"],
        #     password=self.config_json["oracle_info"]["db_password"],
        #     dsn=self.config_json["oracle_info"]["db_service_name"])

        # # __ connected to mysql db.
        self.db.bind(
            provider='mysql',
            host=self.config_json["sql_info"]["db_host"],
            user=self.config_json["sql_info"]["db_user_name"],
            passwd=self.config_json["sql_info"]["db_password"],
            db=self.config_json["sql_info"]["db"])

        self.db.generate_mapping(create_tables=False)
        self.start_process()
        return True

    class UB_ril_presenze(db.Entity):
        """assigning data to oracle db."""
        user_id = orm.PrimaryKey(str, auto=True, column="UserId")
        s_name = orm.Required(str, column="Surname")
        name = orm.Required(str, column="Name")
        cod_pin = orm.Required(str, column="CodPin")

    def start_process(self):
        """connecting from oracle server and post data"""

        with orm.db_session:
            query_cod_pin = self.config_json["query"]["cod_pin"]
            orm.select(u for u in self.UB_ril_presenze if u.cod_pin == query_cod_pin).show()
            batch_records = orm.select(
                u for u in self.UB_ril_presenze if u.cod_pin == query_cod_pin).count()
            print("total count is: {}.......\n".format(batch_records))

            offset_limit = self.util_obj.offset_limit
            for i in range(ceil(batch_records/self.util_obj.per_batch_record)):
                batch_records = orm.select(
                    u for u in self.UB_ril_presenze if u.cod_pin == query_cod_pin).limit(
                        10, offset=offset_limit)
                for record in batch_records:
                    self.post_data(record.to_dict())
                offset_limit += self.util_obj.per_batch_record
        self.db.disconnect()

    def post_data(self, record):
        """ post data in api."""
        data_schema = {
            "alias_id": record["user_id"],
            "name": record["name"] + ' ' + record["s_name"],
            "cod_pin": record["cod_pin"],
            "status": "scheduled",
            "type": "student",
        }
        print(data_schema)
        # print('** **\f'*2)
        auth_token = self.get_auth_code()
        # post_header = self.config_json["api_data"]["post_header"]
        post_header = {"Accept": "application/json", "Content-Type": "application/json"}
        post_header = {"Authorization": "Bearer"+" "+auth_token}
        try:
                
            r_report = requests.post(
                self.util_obj.first_url+self.config_json["api_data"]["post_api"],
                data=data_schema,
                headers=post_header)

            print("post status is: {}".format(r_report.status_code))
            # print("post reponse is \n", r_report.json())
        except Exception as e:
            print("error occurred. {}".format(e))

    def get_auth_code(self):
        """ for jwt token """
        try:
            r = requests.post(
                self.util_obj.first_url+self.config_json["api_data"]["login_url"],
                json=self.config_json["api_credential"])
        except requests.exceptions.RequestException as e:
            # print("Waiting for network....: {}.".format(e))
            print("Waiting for network....")
            sleep(0.1)
            self.get_auth_code()
            return True
        try:
            print(r.json()['jwt'])
            return r.json()['jwt']
        except KeyError as e:
            print("Error occured !! Response auth api => {}".format(e))
            print(r.json())
            # TODO:
            # send mail....
        except Exception as e:
            print("Unknown Error occured !! Response auth api => {}".format(e))
            self.get_auth_code()
            return True
