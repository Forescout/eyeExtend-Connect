import requests
import xml.etree.ElementTree as ET
import urllib3
import logging
import json
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#from unigy_testdata import *
response = {}

def str2bool(v):
    logging.debug(f"str2bool")
    return v.lower() in ("yes", "true", "t", "1")

# All server configuration fields will be available in the 'params' dictionary.


response["result_msg"] = ""
jdata = json.loads(params["connect_unigy_rest_servers"])

for server in jdata['Servers']:
    state = str(server['active']) 
    hostname = str(server['hostname'])
    token = str(server['password'])
    version = str(server['version'])
    certificate = str(server['certificate'])
    cert = str2bool(certificate)
    enablestate = str2bool(state)
    location = str(server['location'])
    logging.debug(f'location is: {location}')            
    logging.debug(f'hostname is: {hostname}')
    logging.debug(f'token is: {token}') 
    logging.debug(f'state is: {str(state)}')
    logging.debug(f'version is: {version}')
    logging.debug(f'certificate is: {str(cert)}')
    if enablestate == False:
        logging.debug(f'hostname is {hostname} is disabled so dropping the call')
        continue                          
 
    header = {'Content-Type': 'application/xml','Authorization': 'Basic '+token+'','X-IPCBWAPIVersion': version}
    xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ns1:CreateSession xmlns:ns1="http://www.ipc.com/bw"><ns1:SessionInfo><ns1:ClientType>DATA</ns1:ClientType></ns1:SessionInfo></ns1:CreateSession>"""

    r = requests.post(hostname+'/svc/bw/session', data=xml, headers=header, verify=cert)
    try:
        auth_resolve_response = requests.post(hostname+'/svc/bw/session', data=xml, headers=header, verify=cert)
    except Exception as e:
        logging.debug(f"Connection Timeout or other issue" + str(e))
        response["succeeded"] = False
        response["result_msg"] = "Could not connect to Unigy host " + hostname + " had error " + e + "."
        break
    #### Bluewave API authentication ####

    if r.status_code == 200:
        logging.debug(f"Connection Successful")
        response["succeeded"] = True
        response["result_msg"] += "Successfully connected to Unigy on " + hostname + "."
        continue
    else:
        logging.debug(f"Connection Unsuccessful" + str(r.status_code) + " from host " + hostname + ".")
        response["succeeded"] = False
        response["result_msg"] = "Bad HTTP response " + str(r.status_code) + " from host " + hostname + "."
        break
