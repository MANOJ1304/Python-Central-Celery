"""
mail-templatesender "{\"newsletter_html\":\"<h1>welcome</h1>\",\"smtp\":{\"outgoing_server\":\"smtp.gmail.com\",\"incoming_server\":\"imap.gmail.com\",\"port\":25,\"receiver_port\":587,\"auth_required\":true,\"reply_to\":\"\",\"credentials\":{\"username\":\"dev@intelipower.co.za\",\"password\":\"DevelopMent@22\"}},\"spid\":\"5203363f47bc4c2991a7a2bf3f4a2cb4\",\"void\":\"f60365ccbe9d4324ab61c17a6ef57caf\",\"veid\":\"36e4930bf12a42e5a5b64cded1515fa9\",\"cid\":\"2f4e2b3d13e84c8c83b4088d812e6813\",\"filter_for_guest\":{\"tester_flag\":false,\"valid_email\":{\"$ne\":false},\"agree_newsletter\":{\"$ne\":false}},\"utc_publish_date\":\"2018-03-22 21:01:00+00:00\",\"subject\":\"TEST MAIl\",\"public_key\":\"\",\"guests_mail_list\":[{\"user_name\":\"manmohan.singh@tes.media\"},{\"user_name\":\"manmohans@intelipower.co.za\"}, {\"user_name\": \"joys.pereira@tes.media\"}]}"
"""

import time
import requests
import pymongo


class Utils(object):
    """ constant objects stored here."""

    def __init__(self):
        self.status = ''
        self.net_cnt = 1

    main_header = {"Content-Type": "application/json", "Accept": "application/json"}
    log_image_newsletter = (
        "<img src='{}/api/v1/serviceProviders/{}/venueOwners/{}/venues"
        "/{}/newsletterid/{}/open.jpg' style='width:1px;height:1px;'>")
    unsubscribe_link = (
        "/api/v1/serviceProviders/{}/venueOwners"
        "/{}/venues/{}/newsletterid/{}/userName/{}\"")
    app_log_json = {
        "data": {"action": "sent", "cid": ""},
        "type": "newsletterTrend"
    }

    # # __ live api.
    # api_appEventLogs = "https://api.fattiengage.com/api/v1/appEventLogs"
    # browser_view_link = " href=\"http://www.newtownjunctionmall.co.za/#!/newsletter/{}\""
    # front_rest_api = "https://api.fattiengage.com"
    # scheduler_login_api = "http://138.197.110.57/tasks"
    # mongo_credential = {
    #     "mongo_ip": "10.28.28.3",
    #     "mongo_port": 27017,
    #     "auth_user": "superuser",
    #     "auth_pwd": "12345678",
    #     "db_name": "admin",
    #     "collection_name": "sent_mail_record"
    # }

    # # __ 42-test-api
    api_appEventLogs = "http://192.168.0.42/api/v1/appEventLogs"
    browser_view_link = " href=\"http://192.168.0.50:3000/#!/newsletter/{}\""
    front_rest_api = "http://192.168.0.42"
    scheduler_login_api = "http://192.168.0.112:9000/tasks"
    mongo_credential = {
        "mongo_ip": "192.168.0.53",
        "mongo_port": 27017,
        "auth_user": "superuser",
        "auth_pwd": "12345678",
        "db_name": "admin",
        "collection_name": "sent_mail_record"
    }
    # # __
    scheduler_patch_data = {
        "schedule": {
            "week": "*",
            "hour": "16",
            "day_of_week": "*",
            "month": "11",
            "second": "10",
            "year": "2017",
            "day": "9",
            "minute": "33"
            },
        "config": "",
        "module": "mail_recevier.mail_import.Mail_read_data",
        "callable": "read_mail",
        "job": "Sample_nlewww",
        "params": [],
        "type": "class"
    }

    # # __
    def check_connection(self, url):
        """checking connection for mongo db """
        try:
            if isinstance(url, pymongo.mongo_client.MongoClient):
                url.server_info()
            # elif type(url) == aioredis.commands.Redis:
            # 	print(url, type(url))
            else:
                requests.get(url)
            self.status = 'on'
        except Exception as e:
            # print("Something went wrong:")
            self.status = 'off'
            print(e)
        finally:
            if self.status == 'off':
                self.net_cnt += 1
                print('off count.//...>> {}'.format(self.net_cnt))
                time.sleep(5)
                self.check_connection(url)
            else:
                # print('connected...   ')
                return True
        # # __ ex.
        # client = pymongo.MongoClient(str(db_ip)+":"+str(db_host))
        # check = self.util_obj.check_connection(client)
