from base64 import b64encode
import requests
import logging
import json

logging.info('===>Starting Nutanix Test Script')

prism_api_ip = params.get('connect_nutanix_prism_api_ip', '')
username = params.get('connect_nutanix_username', '')
password = params.get('connect_nutanix_password', '')
ssl_verify = params.get("connect_nutanix_ssl_verify", False)

# prepare encoded credentials based on username/password
encoded_credentials = b64encode(bytes(f'{username}:{password}',\
                                      encoding='ascii')).decode('ascii')
# prepare the headers
auth_header = f'Basic {encoded_credentials}'

headers = { 
            'Accept': 'application/json', 
            'Content-Type': 'application/json',
            'Authorization': f'{auth_header}', 
            'cache-control': 'no-cache'
          }

# base api URI
base_uri = f'https://{prism_api_ip}:9440/api/nutanix/v3'
url = f'{base_uri}/hosts/list'
data = '{"kind":"host"}'
response = {}

try: 
    resp = requests.request('post', url, data=data, headers=headers, verify=ssl_verify)

    # Return the 'response' dictionary, must have a 'succeeded' field.
    
    if resp.status_code == 200: 
        content = json.loads(resp.content)
        total_hosts = content.get('metadata', {'total_matches':0}).get('total_matches')
        
        response['succeeded'] = True
        response['result_msg'] = f'Successfully connected. Total of {total_hosts} host(s) has been discovered.'
        logging.debug(f'Test Script was successful. Total of {total_hosts} host(s) has been discovered.')
    else:
        response['succeeded'] = False
        response['result_msg'] = 'Could not connect to Nutanix Server'
        logging.info(f'Test Script was not successful - status code: {resp.status_code}')

except requests.exceptions.RequestException as e: 
    response['succeeded'] = False
    response['result_msg'] = f'Could not connect to Nutanix Server.. Exception occured: {e}'

logging.info('===>Ending Nutanix Test Script')
