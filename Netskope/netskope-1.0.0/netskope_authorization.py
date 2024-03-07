from base64 import b64encode
import requests
import logging
import json

logging.info('===>Starting netskope Simulated Authorization Script')
logging.debug('Params for Authorization Script:')
logging.debug(params)

url = params.get("connect_netskope_url", '')
token = params.get("connect_netskope_token", '')

proxy_ip = params.get("connect_proxy_ip", '')
proxy_port = params.get("connect_proxy_port", '')
proxy_username = params.get("connect_proxy_username", '')
proxy_password = params.get("connect_proxy_password", '')

response = {}

try: 
    
    response['token'] = 'simulated_token'

except: 
    response['token'] = '' 
    response['error'] = 'Could not connect to netskope Server.. Exception occured.'

logging.info(f'Authorization Script Returned Response: {response}')
logging.info('===>Ending netskope Simulated Authorization Script')