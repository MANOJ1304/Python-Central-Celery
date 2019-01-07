""" mongo db operations. """
import copy
from pymongo import MongoClient
from tasks.mail_sender.utils import Utils


class MongoRead(object):
    """ db operations"""
    util_obj = Utils()

    def __init__(self, mongo_ip, mongo_port, auth_user, auth_pwd, db_name, collection_name):
        """ function main entry."""
        self.mongo_ip = mongo_ip
        self.mongo_port = mongo_port
        self.db_name = db_name
        self.auth_user = auth_user
        self.auth_pwd = auth_pwd
        self.collection_name = collection_name

    def auth_mongo(self):
        """ authenticate db for """
        connection = MongoClient(self.mongo_ip, self.mongo_port)
        print("db status is : {}\n".format(self.util_obj.check_connection(connection)))
        db = connection[self.db_name]
        db.authenticate(self.auth_user, self.auth_pwd)
        return db

    def insert_record(self, post_record):
        """ insert record into db"""
        db = self.auth_mongo()
        collection_obj = db[self.collection_name]
        posts = collection_obj.insert_one(copy.deepcopy(post_record)).inserted_id
        print("Data uploaded successfully db - {}\tpost_id ==> {}" .format(collection_obj, posts))

    def find_record(self, record):
        """ find record from db"""
        db = self.auth_mongo()
        collection_obj = db[self.collection_name]
        found_data = collection_obj.find_one(record)
        if found_data is None:
            flag = False
        else:
            flag = True
        return flag

    def remove_record(self, record_id):
        """ delete record from db"""
        db = self.auth_mongo()
        collection = db[self.collection_name]
        result = collection.remove({"cid": {"$eq": record_id}})
        print(result)
####

# 006+++++++------------
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
# if not (mongo_obj.find_record(
    # {"user_name":"ddmanmohan.s007@gmail.com","cid":"_+_123564612548615"})):
#     print("HAHAHAHHAHAHAHHHAHHHAHAHAHAHAA.............")
# mongo_obj.remove_record({"user_name":"manmohan.s007@gmail.com","cid":"_+_123564612548615"})
