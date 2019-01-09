""" all mongo db operations done here. """
import copy
from pymongo import MongoClient
from tasks.mail_receiver_module.utils import Utils


class MongoRead(object):
    """ read mongo db"""
    util_obj = Utils()

    def __init__(self, mongo_ip, mongo_port, auth_user, auth_pwd, db_name, collection_name):
        """intialise mongo db """
        self.mongo_ip = mongo_ip
        self.mongo_port = mongo_port
        self.db_name = db_name
        self.auth_user = auth_user
        self.auth_pwd = auth_pwd
        self.collection_name = collection_name

    def auth_mongo(self):
        """ auth mongo db for login."""
        # client = MongoClient('mongodb://usr_name:pwd@mongoip')
        client = MongoClient('mongodb://{}:{}@{}'.format(
            self.auth_user, self.auth_pwd, self.mongo_ip))
        db = client[self.db_name]
        # connection = MongoClient(self.mongo_ip, self.mongo_port)
        # print("db status is : {}\n".format(self.util_obj.check_connection(connection)))
        # db = connection[self.db_name]
        # db.authenticate(self.auth_user, self.auth_pwd)
        return db

    def insert_record(self, post_record):
        """inset record into db """
        db = self.auth_mongo()
        collection_obj = db[self.collection_name]
        posts = collection_obj.insert_one(copy.deepcopy(post_record)).inserted_id
        print("Data uploaded successfully db - {}\tpost_id ==> {}" .format(collection_obj, posts))

    def find_record(self, find_record):
        """find mongo record """
        db = self.auth_mongo()
        collection_obj = db[self.collection_name]
        find_data = collection_obj.find_one(find_record)
        if find_data is None:
            flag = False
        else:
            flag = True
        return flag

    def find_all(self, find_data):
        """get all mongo records."""
        db = self.auth_mongo()
        collection_obj = db[self.collection_name]
        cur = collection_obj.find(find_data)
        temp_list = []
        for i in cur:
            if 'user_name' in i:
                temp_list.append(i["user_name"])
            else:
                temp_list.append(i)
        # cur.count() ##__for finding length of code
        return temp_list

    def insert_many(self, data_condition, update_record):
        """insert many records."""
        db = self.auth_mongo()
        collection_obj = db[self.collection_name]
        # result_update = collection_obj.update(
        #     {'cid': 'b9140c7779a942e4a735e8cbb88af7b9'},
        #     {'$set': {'tag': "test change!"} },
        #     multi=True)
        result_update = collection_obj.update(data_condition, {'$set': update_record}, multi=True)
        return result_update

    def remove_record(self, record_id):
        """remove record from db."""
        db = self.auth_mongo()
        collection = db[self.collection_name]
        result = collection.remove({"cid": {"$eq": record_id}})
        print(result)

# # # # # # ++++++------------
# util_obj = Utils()
# mongo_obj = MongoRead(
#                     util_obj.mongo_credential['mongo_ip'],
#                     util_obj.mongo_credential['mongo_port'],
#                     util_obj.mongo_credential['auth_user'],
#                     util_obj.mongo_credential['auth_pwd'],
#                     util_obj.mongo_credential['db_name'],
#                     util_obj.mongo_credential['collection_name']
# )
# mongo_obj.insert_record({"user_name":"manmohan.s007@gmail.com","cid":"_+_123564612548615"})
# print(mongo_obj.find_record({"user_name":"ddmanmohan.s007@gmail.com","cid":"_+_123564612548615"}))
# if not (mongo_obj.find_record({"user_name":"ddmanmohan.s007@gmail.com","cid":"_+_123564612548615"})):
#     print("HAHAHAHHAHAHAHHHAHHHAHAHAHAHAA.............")
# mongo_obj.remove_record({"user_name":"manmohan.s007@gmail.com","cid":"_+_123564612548615"})

# util_obj = utils.Utils()
# mongo_obj = MongoRead(
#                     util_obj.mongo_credential['mongo_ip'],
#                     util_obj.mongo_credential['mongo_port'],
#                     util_obj.mongo_credential['auth_user'],
#                     util_obj.mongo_credential['auth_pwd'],
#                     util_obj.mongo_credential['db_name'],
#                     util_obj.mongo_credential['collection_name']
#     )
# if not (
#     self.mongo_obj.find_record(
#         {"user_name": mail_receiver_guest['user_name'],
#         "cid": self.config_json['cid']}
#         )
#     ):
#             pass
