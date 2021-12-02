from base64 import b64encode
import requests
import logging
import json


# CONFIGURATION
logging.info('===>Starting pfsense Poll Script')

#disable those loggings before releasing the script
logging.debug('Params for Poll Script:')
logging.debug(params)

# All server configuration fields will be available in the 'params' dictionary.
ip_address = params.get("connect_pfsense_ip_address", '')
login = params.get("connect_pfsense_login", '')
password = params.get("connect_pfsense_password", '')

token = params.get('connect_authorization_token', '')


# Mapping between pfsense response fields to Forescout connect App properties
pfsense_to_ct_props_map = {
     "hostname" : "connect_pfsense_hostname"

}



url = f"https://{ip_address}/api/v1/services/dhcpd/lease"

headers = {
  'Authorization': f'Bearer {token}'
}


# data input ip - could be changed to mac 
ip = params.get("ip", '')
body = {"ip": ip}
body_str = json.dumps(body)

#initialize response 
response = {}

try: 

    
    # Make the API Call
    resp = requests.request('post', url, data = body_str, headers=headers, verify=False)
    
    if resp: 
        content = json.loads(resp.content)
        if resp.status_code == 200: 
            props = {}
            for item in pfsense_to_ct_props_map:
                props["connect_pfsense_hostname"] = content["hostname"]
                props["online"] = content["online"]
                
            response['properties'] = props
            # response needs to be { 'properties' : { 'prop1': 'value1', etc..} } 
            # where prop1 needs to be the internal Forescout connect App property Name. 
            # otherwise return 'error' key with the error message. 
            
        else:
            response['error'] = f'Error Code: {resp.status_code} recieved. '+content.get('message', '') 
            
    else:
        response['error'] = f'Error empty response from Resolve POST  for {body_str}'

except requests.exceptions.RequestException as e:
    response['error'] = f'Error Exception happend while requesting Resolve API: {e}'

# logging response for debugging purposes - you might disable this option later.
logging.debug(f'Response: {response}')

logging.info('===>Ending pfsense Resolve Script')