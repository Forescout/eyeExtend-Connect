from base64 import b64encode
import logging
import json

# syslog script runs when a syslog message is recieved from the defined source
response = {}
properties = {}
ioc_info_dict = {}

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

keys = [k for k in netskope_to_ct_props_map.keys()]
values = [v for v in netskope_to_ct_props_map.values()]

logging.info('===>*********Starting netskope Simulated SYSLOG Script*************')

if params.get("connect_syslog_message"):
    syslog_message = params.get("connect_syslog_message", '')
    logging.debug(f"Syslog message is: {syslog_message}")
    try:
        syslog_obj = json.loads(syslog_message[4:])
        if 'target_ip' in syslog_obj:
            response['ip'] = syslog_obj.get('target_ip')
        if 'message' in syslog_obj: 
            properties[ values[0] ] = syslog_obj.get('message', '')
            response['properties'] = properties
        if 'ioc' in syslog_obj:
            response["ioc"] = syslog_obj.get('ioc', {})
    except: 
        response["error"] = "Syslog parsing failed!"
        
else:
    response["error"] = "Syslog Message Missing..."

# logging response for debugging purposes - you might disable this option later.
logging.info(f'Returned Response: {response}')

logging.info('===>Ending netskope Simulated SYSLOG Script')