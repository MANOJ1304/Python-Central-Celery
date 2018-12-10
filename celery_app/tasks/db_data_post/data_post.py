"""
    data post on oracle db.
    Module req.- pony, requests, cx_Oracle
"""
from math import ceil
import requests
from pony import orm
from tasks.celery_queue_tasks import ZZQHighTask
from tasks.db_data_post.utils import UtilData

# db = orm.Database()


# class UB_ril_presenze(db.Entity):
#     user_id = orm.PrimaryKey(str, auto=True, column="UserId")
#     s_name = orm.Required(str, column="Surname")
#     name = orm.Required(str, column="Name")
#     cod_pin = orm.Required(str, column="CodPin")


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
        self.config_json = args[0]
        self.start_process()
        return True

    class UB_ril_presenze(db.Entity):
        user_id = orm.PrimaryKey(str, auto=True, column="UserId")
        s_name = orm.Required(str, column="Surname")
        name = orm.Required(str, column="Name")
        cod_pin = orm.Required(str, column="CodPin")

    def start_process(self):
        """connecting from oracle server and post data"""
        self.db.bind(
            provider='oracle',
            user=self.util_obj.db_user_name,
            password=self.util_obj.db_password,
            dsn=self.util_obj.db_service_name)
        self.db.generate_mapping(create_tables=False)

        with orm.db_session:
            query_cod_pin = self.config_json["query"]["CodPin"]
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

    def post_data(self, record):
        """ post data in api."""
        data_schema = {
            "alias_id": record["user_id"],
            "name": record["name"] + ' ' + record["s_name"],
            "code_pin": record["cod_pin"],
            "status": "scheduled",
            "type": "student",
        }
        print(data_schema)
        # print('** **\f'*2)
        auth_token = self.login_api()
        # post_header = self.config_json["api_data"]["post_header"]
        post_header = {"Accept": "application/json", "Content-Type": "application/json"}
        post_header = {"Authorization": "Bearer"+" "+auth_token}
        r_report = requests.post(
            self.util_obj.first_url+self.config_json["api_data"]["post_api"],
            data=data_schema,
            headers=post_header)

        print("post status is: {}".format(r_report.status_code))
        # print("post reponse is \n", r_report.json())

    def login_api(self):
        r = requests.post(
            self.util_obj.first_url+self.config_json["api_data"]["login_url"],
            json=self.util_obj.api_credential)
        return r.json()['jwt']
