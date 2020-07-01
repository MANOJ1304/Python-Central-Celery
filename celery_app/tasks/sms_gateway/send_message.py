from tasks.celery_queue_tasks import ZZQLowTask
from celery.task.control import revoke
import clicksend_client
from clicksend_client import SmsMessage
from clicksend_client.rest import ApiException
import json
import datetime
import time
import redis



class SendMessage(ZZQLowTask):
    """ testing Task. """
    name = "Send SMS"
    description = ''' Sending SMS to user.'''
    public = True
    autoinclude = True

    def run(self, *args, **kwargs):
        # print("\nENTER IN RUN METHOD")
        # self.post_messages(args[0])
        self.post_messages(args[0])
        return True

    def get_template(self, api_instance):
        page = 1 # int | Page number (optional) (default to 1)
        limit = 100 # int | Number of records per page (optional) (default to 10)
        try:
            # Get lists of all sms templates
            api_response = api_instance.sms_templates_get(page=page, limit=limit)
            return api_response.replace("None","0")
        except ApiException as e:
            print("Exception when calling SMSApi->sms_templates_get: %s\n" % e)
            
        

    def epoch_to_string(self,dt_field):
        dt = datetime.datetime.fromtimestamp(dt_field)
        return datetime.datetime.strftime(dt,"%Y-%m-%dT%H:%M:%S")


    def push_to_redis(self,api_respo,redis_config,owner):
        api_respo.update({"belongs":owner})
        api_respo.update({"message_id" : api_respo["data"]["messages"][0]["message_id"] , 
                        "date" : self.epoch_to_string(api_respo["data"]["messages"][0]["date"])})
        
        redis_obj = redis.StrictRedis(
            host=redis_config['host'], port=redis_config['port'], password=redis_config['password'], db=1)


        # print(api_respo)
        print(redis_obj.lpush(
                        "OP:COMPUTE:sms", json.dumps(api_respo)))
        
            
    def post_messages(self,venue_info):
        # Configure HTTP basic authorization: BasicAuth
        
        configuration = clicksend_client.Configuration()
        configuration.username = venue_info["credential"]["username"]
        configuration.password = venue_info["credential"]["password"]
        # venue_info.update({"redis_config": {
        #     "host": "localhost",
        #     "port": 6379,
        #     "password": ""
        # }})
        # create an instance of the API class
        api_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
        
        # template_str = self.get_template(api_instance)
        # template_dict =  json.loads(template_str.replace("\'","\""))

        # template_m = [i for i in template_dict["data"]["data"] if i["template_id"] ==venue_info["message_type"]][0]
        template_m = venue_info["message_template"]
        # print(venue_info)
        if venue_info["message_type"] == 1:
            template_m = template_m.format(venue_owner_alias = venue_info["message_info"]["venue_owner_alias"] , 
                            site_alias = venue_info["message_info"]["site_alias"], 
                            zone_alias = venue_info["message_info"]["zone_alias"],
                            open_time= venue_info["message_info"]["open_time"])
        elif venue_info["message_type"] == 2:
            template_m = template_m.format(venue_owner_alias = venue_info["message_info"]["venue_owner_alias"] , 
                            site_alias = venue_info["message_info"]["site_alias"], 
                            zone_alias = venue_info["message_info"]["zone_alias"],
                            close_time = venue_info["message_info"]["close_time"])
        elif venue_info["message_type"] == 3:
            template_m = template_m.format(venue_owner_alias = venue_info["message_info"]["venue_owner_alias"] , 
                            site_alias = venue_info["message_info"]["site_alias"], 
                            zone_alias = venue_info["message_info"]["zone_alias"],
                            occupancy_count = venue_info["message_info"]["occupancy_count"],
                            occupancy_threshold = venue_info["message_info"]["occupancy_threshold"])
        elif venue_info["message_type"] == 4:
            template_m = template_m.format(venue_owner_alias = venue_info["message_info"]["venue_owner_alias"] , 
                            site_alias = venue_info["message_info"]["site_alias"], 
                            zone_alias = venue_info["message_info"]["zone_alias"],
                            area_alias= venue_info["message_info"]["area_alias"],
                            device_type= venue_info["message_info"]["device_type"],
                            status= venue_info["message_info"]["status"])
        
        
        # If you want to explictly set from, add the key _from to the message.
        sms_message = SmsMessage(source= venue_info["source"],
                                body= template_m,
                                to= venue_info["to"])

        sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])

        try:
            # Send sms message(s)
            api_responser = api_instance.sms_send_post(sms_messages)
            api_response = (api_responser.replace("None","0"))
            data_to_push = json.loads(api_response.replace("\'","\""))
            if data_to_push["http_code"] == 200:
                # print(data_to_push)
                # pass
                self.push_to_redis(data_to_push,venue_info["redis_config"],venue_info["message_info"]["belongs"])
            else:
                time.sleep(10)
                self.post_messages(venue_info)
        except ApiException as e:
            print("Exception when calling SMSApi->sms_send_post: %s\n" % e)
            time.sleep(10)
            self.post_messages(venue_info)

    

    
    
