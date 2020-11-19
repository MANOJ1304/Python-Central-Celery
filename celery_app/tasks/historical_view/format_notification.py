# from redis_operations import redis_publish
import time
from tasks.historical_view.redis_operations import RedisOp
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

class DataFormator(object):
    
    def __init__(self):
        pass

    def format_notification(self,data_list,publish_channel,config,area_classification):
        seq_number = 0
        notification_obj = {}
        notification_monitor_obj = {}
        notification_monitor_device_obj = {}
        notification_monitor_distance_obj = {}
        notification_monitor_location_obj = {}
        
        ##main root obj 
        notification_obj['message_type'] = "notification_v0.1"
        for es_message in data_list:
            # print(es_message['@timestamp'])
            notification_obj['seq_number'] = seq_number
            notification_obj['historical'] = True
            notification_obj['error'] = False
            seq_number = seq_number + 1
        
            ##notification/monitor obj
            notification_monitor_obj['area_classification'] = es_message.get('area_aacn')
            notification_monitor_obj['channel'] = '#CHANNEL#'
            
            ##notification/monitor/device obj
            notification_monitor_device_obj['device_band'] = es_message.get('device_band')
            # notification_monitor_device_obj['button_state'] = 'pushed'
            notification_monitor_device_obj['button_state'] = es_message.get('device_button_status')
            notification_monitor_device_obj['classification'] = es_message.get('properties_classification')
            notification_monitor_device_obj['device_id'] = es_message.get('device_device_id')
            notification_monitor_device_obj['engine'] = 'omni-presence'
            notification_monitor_device_obj['journey_status'] = es_message.get('properties_journey_status')
            notification_monitor_device_obj['last_seen'] = es_message.get('device_last_seen')
            notification_monitor_device_obj['manufacturer'] = es_message.get('profile_device_manuf')
            notification_monitor_device_obj['mode_entry_status'] = True ##check
            notification_monitor_device_obj['mode_exit_status'] = False ##check
            notification_monitor_device_obj['mode_female_status'] = False ## check
            notification_monitor_device_obj['mode_male_status'] = True ## check
            notification_monitor_device_obj['mode_passerby_status'] = True ## check
            notification_monitor_device_obj['mode_staff_status'] = False ## check
            notification_monitor_device_obj['mode_visitor_status'] = True ## check
            if es_message.get('sensors') != None:
                notification_monitor_device_obj['near_sensor_id'] = es_message.get('sensors')[0].get('id')
                notification_monitor_device_obj['partcode'] = "" ## check
                notification_monitor_device_obj['rssi'] = es_message.get('sensors')[0].get('rssi') 
            notification_monitor_device_obj['rssi_filter_type'] = '0' ## check
            notification_monitor_device_obj['rssi_fix_count'] = '3' ## check
            notification_monitor_device_obj['simple_status'] = 'connected' ## check
            notification_monitor_device_obj['source'] = es_message.get('device_source')
            notification_monitor_device_obj['status'] = es_message.get('device_status')
            notification_monitor_device_obj['track'] = False ## check
            notification_monitor_device_obj['type'] = es_message.get('device_type')
            
            # print("printing -> ",es_message.get('area_aacn',''))
            if area_classification.get('enable') == True and es_message.get('area_aacn') != None:
                notification_monitor_device_obj['user_info'] = {}
                # print(area_classification.get('mapping').get(es_message.get('area_aacn',''),'').get('color'))
                # print(es_message.get('area_aacn'))
                if area_classification.get('mapping').get(str(es_message.get('area_aacn'))) != None:
                    # print(area_classification.get('mapping').get(str(es_message.get('area_aacn'))))
                    notification_monitor_device_obj['user_info']['color'] = area_classification.get('mapping').get(str(es_message.get('area_aacn'))).get('color')
                    notification_monitor_device_obj['user_info']['icon'] = 'account-star' 
                    notification_monitor_device_obj['user_info']['label'] = 'Unknown' 
                    notification_monitor_device_obj['user_info']['sub_type'] = area_classification.get('mapping').get(str(es_message.get('area_aacn'))).get('name')
                    notification_monitor_device_obj['user_info']['type'] = 'visitor' 
                    notification_monitor_device_obj['user_info']['update_rate'] = 10 
                else:
                    notification_monitor_device_obj['user_info'] = {}
                    notification_monitor_device_obj['user_info']['color'] = '#00FF00' 
                    notification_monitor_device_obj['user_info']['icon'] = 'account-star' 
                    notification_monitor_device_obj['user_info']['label'] = 'Unknown' 
                    notification_monitor_device_obj['user_info']['sub_type'] = 'unknown'
                    notification_monitor_device_obj['user_info']['type'] = 'visitor' 
                    notification_monitor_device_obj['user_info']['update_rate'] = 10 ## chec
            else:
                notification_monitor_device_obj['user_info'] = {}
                notification_monitor_device_obj['user_info']['color'] = '#00FF00' 
                notification_monitor_device_obj['user_info']['icon'] = 'account-star' 
                notification_monitor_device_obj['user_info']['label'] = 'Unknown'
                notification_monitor_device_obj['user_info']['sub_type'] = 'unknown'
                notification_monitor_device_obj['user_info']['type'] = 'visitor'
                notification_monitor_device_obj['user_info']['update_rate'] = 10
            
            notification_monitor_obj['device'] = notification_monitor_device_obj
                
            ##notification/monitor/distance obj
            notification_monitor_distance_obj['action'] = 'unknown'
            notification_monitor_distance_obj['moved'] = es_message.get('properties_moved')
            notification_monitor_distance_obj['proximity'] = es_message.get('properties_proximity')
            notification_monitor_distance_obj['unit'] = es_message.get('properties_unit')
            
            notification_monitor_obj['distance'] = notification_monitor_distance_obj
            
            ##notification/monitor/location obj
            notification_monitor_location_obj['geometry'] = {}
            notification_monitor_location_obj['geometry']['coordinates'] = es_message.get('location_geometry_coordinates')
            notification_monitor_location_obj['geometry']['type'] = es_message.get('location_geometry_type')
            notification_monitor_location_obj['properties'] = {}
            if es_message.get('area_ids'):
                notification_monitor_location_obj['properties']['areas'] = [i.get('id') for i in es_message.get('area_ids')]
            notification_monitor_location_obj['properties']['dwell'] = es_message.get('properties_dwell')
            notification_monitor_location_obj['properties']['dwell_ms'] = es_message.get('properties_dwell_ms')
            notification_monitor_location_obj['properties']['filter_level'] = 1 ## check
            notification_monitor_location_obj['properties']['filters'] = es_message.get('location_filters')
            notification_monitor_location_obj['properties']['loc_algo'] = es_message.get('properties_loc_algo')
            notification_monitor_location_obj['properties']['site_index'] = '' ## check
            notification_monitor_location_obj['properties']['unit'] = es_message.get('properties_unit')
            notification_monitor_location_obj['type'] = es_message.get('location_type')
            
            notification_monitor_obj['location'] = notification_monitor_location_obj
            
            ##merge into root obj  
            notification_obj['monitor'] = notification_monitor_obj
            # print(notification_obj)
            redis_obj = RedisOp(config)
            redis_obj.redis_publish(notification_obj,publish_channel)
            time.sleep(1/10) # to decrease the speed of messages published so user can view data properly
            
        # exit()
        
    def send_error_message(self,publish_channel,config):
        message = "No data present for selected date range."
        error_obj = {}
        error_obj['error'] = True
        error_obj['message'] = message
        # print(error_obj)
        redis_obj = RedisOp(config)
        redis_obj.redis_publish(error_obj,publish_channel)
