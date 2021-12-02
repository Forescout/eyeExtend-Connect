from base64 import b64encode
import requests
import logging
import json


# CONFIGURATION
logging.info('===> Starting pfsense Poll Script')

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



def extract_endpoints(respons):
    #initialize response
    response = {}
    response['endpoints'] = []

    #extract data
    lease_polled= json.loads(respons.content)
    lease_polled = lease_polled.get('data', '')

    # Transform to endpoints list
    for lease in lease_polled:
        lp = {}

        ip= lease.get('ip', '')
        mac = lease.get('mac', '')
        if ip =='' and mac=='':
            continue
        if ip!='':
            lp['ip'] = ip
        if mac!='':
            lp['mac'] = ''.join(mac.split(':'))

        lp['properties'] = {}
        lp['properties']['connect_pfsense_hostname'] = str(lease.get('hostname', ''))
        lp['properties']['online'] = lease.get('online', '')

        response['endpoints'].append(lp)

    return response

try:

    resp = requests.request("GET", url, headers=headers,  verify=False)

    if resp is None:
        response['error'] = 'Error empty response from Poll Get request to connect_pfsense Service.'

    elif resp.status_code == 200:
        response = extract_endpoints(resp)

    else:
        response['error'] = f'Error {resp.status_code} Received.'

except requests.exceptions.RequestException as e:
    response['error'] = f'Error Exception happend while requesting Poll Get from connect_pfsense Proxy Service: {e}'


# logging response for debugging purposes - you might disable this option later.
logging.debug(f'Poll Response: {response}')

logging.info('===>Ending connect_pfsense Poll Script')

