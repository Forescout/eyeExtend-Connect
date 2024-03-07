from base64 import b64encode
import requests
import logging
import json

logging.info('===>************** Starting netskope Test Script **************')
logging.debug('Params for Test Script:')
logging.debug(params)

#input Params 
url = params.get("connect_netskope_url", '').strip()
if url.endswith('/'):
    Base_URL = f'{url}api/v1/clients'
else: 
    Base_URL = f'{url}/api/v1/clients'
    
token = params.get("connect_netskope_token", '')
query = "host_info"

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

    
}

    
response = {}
try: 
    # Construct the query parameters
    params = {'token': token, 'query': query}

    # Make a GET request to the API endpoint, passing the query parameters
    result = requests.get(Base_URL, params=params)
    if result.status_code == 200: 
        result = result.json()
        if result.get('status', 'fail') == 'success':
            #output response
            response['succeeded'] = True 
            response['result_msg'] = 'Successfully connected!'
        else: 
            response['succeeded'] = False 
            response['result_msg'] = 'Failed Status is not showing success!'
    else: 
            response['succeeded'] = False 
            response['result_msg'] = f'error {result.status_code} - {result.content}'
            
except Exception as e: 
    response['succeeded'] = False
    response['result_msg'] = f'Testing Failed.. {e}'
    
logging.info(f' Test Script Returned Response: {response}')
logging.info('===>Ending netskope Test Script')
