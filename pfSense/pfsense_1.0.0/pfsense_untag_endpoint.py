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

proxy_ip = params.get("connect_proxy_ip", '')
proxy_port = params.get("connect_proxy_port", '')
proxy_username = params.get("connect_proxy_username", '')
proxy_password = params.get("connect_proxy_password", '')

# Mapping between pfsense response fields to Forescout connect App properties
pfsense_to_ct_props_map = {
     "hostname" : "connect_pfsense_hostname"

}

# Grab Existing List of Aliases
orig_aliases = params.get("connect_pfsense_aliases", "")
if orig_aliases == '':
    aliases = []
else: 
    aliases = orig_aliases.split(',')


url = f"https://{ip_address}/api/v1/firewall/alias/entry"

headers = {
  'Authorization': f'Bearer {token}'
}


# data input ip 
ip = params.get("ip", '')
#mac = params.get("mac", '')
# Actions Parameters
alias = params.get("connect_pfsense_alias", "")
cookie = params.get("cookie", "")



#initialize response 
response = {}

try: 
    final_resp = True
    
    for _alias in aliases: 
        body = {'name': _alias,'address': ip}
        body_str = json.dumps(body)
        
        # Make the API Call
        resp = requests.request('delete', url, data = body_str, headers=headers, verify=False)
        if resp.status_code != 200: 
            final_resp = False 
        
    if final_resp: 
        response['succeeded'] = True
        response['ip'] = ip
        response['properties'] = {"connect_pfsense_aliases": ""}
    else:
        response['succeeded'] = False 
        response['troubleshooting'] = f'Error code {resp.status_code} received from Action API..'

except requests.exceptions.RequestException as e:
    response['succeeded'] = False 
    response['troubleshooting'] = f'Error Exception happend while taking Action: {e}'

# logging response for debugging purposes - you might disable this option later.
logging.debug(f'Response: {response}')

logging.info('===>Ending pfsense Action')