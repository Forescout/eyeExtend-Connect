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

     "hostname" : "connect_pfsense_hostname",
     "aliases": "connect_pfsense_aliases"

}



url = f"https://{ip_address}/api/v1/firewall/alias/entry"

headers = {
  'Authorization': f'Bearer {token}'
}


# data input ip 
ip = params.get("ip", '')
#mac = params.get("mac", '')
# Actions Parameters
alias = params.get("connect_pfsense_alias", "")

# Grab Existing List of Aliases
orig_aliases = params.get("connect_pfsense_aliases", "")
if orig_aliases == "":
    aliases = []
else: 
    aliases = orig_aliases.split(',')



body = {'name': alias, 'address': ip, 'detail':'Added by Forescout'}


body_str = json.dumps(body)

#initialize response 
response = {}

try: 
    
    # Make the API Call
    resp = requests.request('post', url, data = body_str, headers=headers, verify=False)
    
    if resp: 
        content = json.loads(resp.content)
        if resp.status_code == 200: 
            response['succeeded'] = True
            response['cookie'] = f'tag endpoint {ip}_{alias}' 
            aliases.append(alias)
            response['ip'] = ip
            aliases.sort()
            str_aliases = ','.join(aliases)
            response['properties'] = {"connect_pfsense_aliases": str_aliases}
        else:
            response['succeeded'] = False 
            response['troubleshooting'] = f'Error code {resp.status_code} received from Action API..'
            
    else:
        response['succeeded'] = False 
        response['troubleshooting'] = f'Error empty response from Action request.'

except requests.exceptions.RequestException as e:
    response['succeeded'] = False 
    response['troubleshooting'] = f'Error Exception happend while taking Action: {e}'

# logging response for debugging purposes - you might disable this option later.
logging.debug(f'Response: {response}')

logging.info('===>Ending pfsense Action Script')