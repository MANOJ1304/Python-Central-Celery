
import datetime
# from .read_config import get_config
from tasks.historical_view.fetch_es_data import ESDataFetch
from tasks.historical_view.format_notification import DataFormator
from tasks.historical_view.redis_operations import RedisOp
import json
from tasks.celery_queue_tasks import ZZQLowTask
import logging
import time

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

class HistoricalView(ZZQLowTask):
    """."""
    name = 'Historical View'
    description = """ Historical View point generator. """
    public = True
    autoinclude = True

    def __init__(self):
        """ initialise process start from here. """
        pass

    def run(self, *args, **kwargs):
        """ start celery process from here. """
        self.config_json = args[0]

        self.main_process(self.config_json)
        return True


    def main_process(self,config_json):
        if type(config_json) == str:
            config = json.loads(config_json)
        else:
            config = config_json
        
        gte = config['timestamp']['start']
        lte = config['timestamp']['end']
        veId = config['venue_id']
        floor_id = config['floor_id']
        e_map = config['emap_config']
        es_index = config['index']
        cfg = {
            "es": {
            "host": config['es_config']['host'],
            "port": config['es_config']['port'],
            "username": config['es_config']['username'],
            "password": config['es_config']['password'],
            "search_query": {
                "slice": {
                    "id": 0,
                    "max": 10
                },
                    "query": {
                        "bool": {
                        "must": [
                            {
                            "range": {
                                "@timestamp": {
                                "gte": gte,
                                "lte": lte,
                                "format": "epoch_millis"
                                }
                            }
                            }
                        ],
                        "filter": [
                            {
                            "bool": {
                                "filter": [
                                {
                                    "bool": {
                                    "should": [
                                        {
                                        "match_phrase": {
                                            "belongs.owner.veId": veId
                                        }
                                        }
                                    ],
                                    "minimum_should_match": 1
                                    }
                                },
                                {
                                    "bool": {
                                    "filter": [
                                        {
                                        "bool": {
                                            "should": [
                                            {
                                                "match_phrase": {
                                                "properties.floor_id": floor_id
                                                }
                                            }
                                            ],
                                            "minimum_should_match": 1
                                        }
                                        },
                                        {
                                            "bool": {
                                            "should": [
                                                {
                                                "match": {
                                                    "veon": True
                                                }
                                                }
                                            ],
                                            "minimum_should_match": 1
                                            }
                                        }
                                    ]
                                    }
                                }
                                ]
                            }
                            }
                        ]
                        }
                    },
                    "size":0
                },
                "index": es_index   
                }
        }
        
        start = time.time()
        
        fetchdata = ESDataFetch(cfg)
        es_raw_data_list = fetchdata.get_plain_data() ## list of records retreived from ES
        # print(len(es_raw_data_list)) 
        logging.info("Data set size: {}".format(len(es_raw_data_list)))
        
        redis_obj = RedisOp(config['redis_config'],e_map) #initialise redis class
        
        # sort the es data list in ascending order
        es_raw_data_list_ordered = sorted(es_raw_data_list,key = lambda i: datetime.datetime.strptime(i['@timestamp'],"%Y-%m-%dT%H:%M:%S.%fZ")) #.datetime.datetime.strptime("%Y-%m-%dT%H:%M:%S")
        
        # get the channel from redis which created from frontend when user clicks on live view button. we publish messages on this channel.
        publish_channel = redis_obj.get_channel() 
        logging.info("Publishing data on channel: {}".format(str(publish_channel)))
        
        logging.info(f'Time: {time.time() - start}')
        
        # send the raw data to extract needed info, create new object for notification and publish them on the retreived channel
        df_obj = DataFormator()
        if len(es_raw_data_list) != 0:
            df_obj.format_notification(es_raw_data_list_ordered,publish_channel,config['redis_config'],config['category'])
        else:
            df_obj.send_error_message(publish_channel,config['redis_config'])
        logging.info("Processing completed.")
