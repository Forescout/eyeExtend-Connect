from base64 import b64encode
import requests
import logging

# CONFIGURATION
logging.info('===>Starting pfsense Test Script')

#disable those loggings before releasing the script
logging.debug('Params for Test Script:')
logging.debug(params)

# All server configuration fields will be available in the 'params' dictionary.
ip_address = params.get("connect_pfsense_ip_address", '')
login = params.get("connect_pfsense_login", '')
password = params.get("connect_pfsense_password", '')



# Mapping between pfsense response fields to Forescout connect App properties
pfsense_to_ct_props_map = {
     "hostname" : "connect_pfsense_hostname"

}

# ***** START - AUTH API CONFIGURATION ***** #
url = f"https://{ip_address}/api/v1/access_token?client-id={login}&client-token={password}"

payload={}
headers={}
response={}

# Make the API Call
try:
    resp = requests.request("POST", url, headers=headers, data=payload, verify=False)
    # resp = None

    if resp.status_code == 200:
        response['succeeded'] = True
        response['result_msg'] = 'Successfully connected to pfsense.'
    else:
        response['succeeded'] = False
        response['result_msg'] = 'Could not connect to pfsense Service'

except requests.exceptions.RequestException as e:
    response['succeeded'] = False
    response['result_msg'] = f'Could not connect to pfsense Service.. Exception occured. {e}'

# logging response for debugging purposes - you might disable this option later.
logging.debug(f'Returned Response: {response}')

logging.info('===>Ending pfsense Test Script')

