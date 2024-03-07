from base64 import b64encode
import requests
import logging
import json

logging.info('===>*************** Starting netskope Simulated IOC Poll Script *********************')
logging.debug('Params for ioc poll Script:')
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
    
    iocs =    [
                {
                "date": 1621975392000,
                "name": "IOC Poll Test 1",
                "hash": "852d67a27e454bd389fa7f02a8cbe23f",
                "hash_type": "md5",
                "platform": "none",
                "file_name": "test_file_1.exe",
                "file_size": 10,
                "severity": "medium"
                },
               {  "date": 1621975392000,
                  "name": "IOC Poll Test 2",
                  "hash_type": "md5",
                  "hash": "2e8d4a6fedf90e265d2370a543b4fd2a",
                  "severity": "low",
                  "platform": "none", 
                  "file_name": "cscript.exe",
                  "file_size": 10,
                  "file_exists": {'file_name': 'cscript.exe', 'file_path': 'c:\\windows\\system32\\'},
                  "cnc": ["8.8.8.8", "9.9.9.9"]
               }
              ]
               
    response['ioc'] = iocs
        
except:
    response['error'] = 'Error Exception happend while requesting ioc poll from netskope'

logging.info(f'Poll Response: {response}')
logging.info('===>Ending netskope simulated IOC poll Script')

# Link to Response details: 
# https://docs.forescout.com/bundle/connect-1-6-h/page/connect-1-6-h.Format-Data-to-_22ioc_22-Response-in-Resolve--IOC-Po.html 