from base64 import b64encode
import logging
import json

logging.info('===>*********Starting netskope Simulated instance cache Script *************')
logging.debug('Params for instance cache Script:')
logging.debug(params)

url = params.get("connect_netskope_url", '')
token = params.get("connect_netskope_token", '')

proxy_ip = params.get("connect_proxy_ip", '')
proxy_port = params.get("connect_proxy_port", '')
proxy_username = params.get("connect_proxy_username", '')
proxy_password = params.get("connect_proxy_password", '')
netskope_to_ct_props_map = {
     "client_version" : "connect_netskope_client_version",
     "device_id" : "connect_netskope_device_id",
     "device_make" : "connect_netskope_device_make",
     "device_model" : "connect_netskope_device_model",
     "hostname" : "connect_netskope_hostname",
     "last_hostinfo_update_timestamp" : "connect_netskope_last_hostinfo_update_timestamp",
     "managementid" : "connect_netskope_managementid",
     "migrated_revision" : "connect_netskope_migrated_revision",
     "nsdeviceuid" : "connect_netskope_nsdeviceuid",
     "os" : "connect_netskope_os",
     "os_version" : "connect_netskope_os_version",
     "serialnumber" : "connect_netskope_serialnumber",
     "npa_status" : "connect_netskope_npa_status",
     "service_name" : "connect_netskope_service_name",
     "status" : "connect_netskope_status",
     "last_event_timestamp" : "connect_netskope_last_event_timestamp",
     "users" : "connect_netskope_users",
     "macaddresses" : "connect_netskope_macaddresses",
    
}

response = {}

try: 
    content = {
                'users': ['user1', 'user2', 'user3'], 
                'timer': 5, 
                'composite': {'key1':'value1', 'key2':'value2'}, 
                'boolkey': True, 
                'strKey': 'sample value'
               }
               
    response["connect_app_instance_cache"] = json.dumps(content) # serialized dict
            
except:
    response['error'] = 'Error Exception happend while requesting instance cache for netskope.'
    response["connect_app_instance_cache"] = "{}"


logging.info(f'Returned Response: {response}')
logging.info('===>Ending netskope Simulated instance cache Script')