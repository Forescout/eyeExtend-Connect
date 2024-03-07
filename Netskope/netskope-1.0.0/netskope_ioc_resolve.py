from base64 import b64encode
import requests
import logging
import json

logging.info('===>******************** Starting netskope simulated IOC Resolve Script ********************')
logging.debug('Params for IOC Resolve Script:')
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

ip = params.get('ip', '')
mac = params.get('mac', '')

response = {}

try: 
    response['ip'] = ip
    response['mac'] = mac
           
    properties = {}
    properties["connect_netskope_client_version"] = "client_version"
    properties["connect_netskope_device_id"] = "device_id"
    properties["connect_netskope_device_make"] = "device_make"
    properties["connect_netskope_device_model"] = "device_model"
    properties["connect_netskope_hostname"] = "hostname"
    properties["connect_netskope_last_hostinfo_update_timestamp"] = "last_hostinfo_update_timestamp"
    properties["connect_netskope_managementid"] = "managementid"
    properties["connect_netskope_migrated_revision"] = "migrated_revision"
    properties["connect_netskope_nsdeviceuid"] = "nsdeviceuid"
    properties["connect_netskope_os"] = "os"
    properties["connect_netskope_os_version"] = "os_version"
    properties["connect_netskope_serialnumber"] = "serialnumber"
    properties["connect_netskope_npa_status"] = "npa_status"
    properties["connect_netskope_service_name"] = "service_name"
    properties["connect_netskope_status"] = "status"
    properties["connect_netskope_last_event_timestamp"] = "last_event_timestamp"
    properties["connect_netskope_users"] = {'username': 'username_sample', 'device_classification_status': 'device_classification_status_sample'}
    properties["connect_netskope_macaddresses"] = "macaddresses"
    
    
    response['properties'] = properties
    
    ioc = {
            "date": 1621975392000,
            "name": "IOC Resolve Test 1",
            "hash": "852d67a27e454bd389fa7f02a8cbe2af",
            "hash_type": "md5",
            "platform": "none",
            "file_name": "test_file_2.exe",
            "file_size": 11,
            "severity": "low"
            }
    
    response['ioc'] = ioc
except:
    response['error'] = f'Error Exception happend while requesting IOC Resolve API'

logging.info(f'Response: {response}')
logging.info('===>Ending netskope simulated IOC Resolve Script')