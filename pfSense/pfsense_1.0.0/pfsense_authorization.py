from base64 import b64encode
import requests
import logging
import json

# CONFIGURATION
logging.info('===>Starting pfsense Authorization Script')

#disable those loggings before releasing the script
logging.debug('Params for Authorization Script:')
logging.debug(params)

# All server configuration fields will be available in the 'params' dictionary.
ip_address = params.get("connect_pfsense_ip_address", '')
login = params.get("connect_pfsense_login", '')
password = params.get("connect_pfsense_password", '')

# ***** START - AUTH API CONFIGURATION ***** #

url = f"https://{ip_address}/api/v1/access_token?client-id={login}&client-token={password}"

payload={}
headers={}

#initialize response
response = {}

# Make the API Call
try:

    # Make the API Call
    resp = requests.request("POST", url, headers=headers, data=payload, verify=False)

    # Return the 'response' dictionary, must have a 'succeded' field.
    content = json.loads(resp.content)

    if resp is None:
        response['error'] = 'No response from pfsense Service.'
        response['token'] = ''
    elif resp.status_code == 200:

        # set the token in this field
        response['token'] = content.get("data", {}).get("token")

    else:
        response['token'] = ''
        response['error'] = f'Error Code {resp.status_code} received from pfsense Service.'

except requests.exceptions.RequestException as e:
    response['token'] = ''
    response['error'] = f'Could not connect to pfsense Server.. Exception occured. {e}'

# logging response for debugging purposes - you might disable this option later.
logging.debug(f'Authorization Script Returned Response: {response}')

logging.info('===>Ending pfsense Authorization Script')

