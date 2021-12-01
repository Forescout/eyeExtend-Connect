"""
Copyright © 2021 Forescout Technologies, Inc.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import requests
import logging
import json

logging.info('===>************** Starting mistwired Test Script **************')

# Input Params 
org_id = params.get("connect_mistwired_org_id", '')
api_key = params.get("connect_mistwired_api_key", '')
base_url = params.get("connect_mistwired_url", '')

# Requests Proxy
is_proxy_enabled = params.get("connect_proxy_enable")
if is_proxy_enabled == "true":
    proxy_ip = params.get("connect_proxy_ip")
    proxy_port = params.get("connect_proxy_port")
    proxy_user = params.get("connect_proxy_username")
    proxy_pass = params.get("connect_proxy_password")
    if not proxy_user:
        proxy_url = f"https://{proxy_ip}:{proxy_port}"
        proxies = {"https" : proxy_url}
        logging.debug ("Proxy enabled / no user")
    else:
        proxy_url = f"https://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
        proxies = {"https" : proxy_url}
        logging.debug ("Proxy enabled / user")
else:
    logging.debug ("Proxy disabled")
    proxies = None


token = "token " + api_key
headers = {"Authorization": token,"content-type": "application/json"}
test_path_url = "/api/v1/self"
test_url = base_url + test_path_url
logging.debug("Mist Test URL " + test_url)

response = {}

try:
    resp = requests.request('get', test_url, headers=headers, verify=ssl_verify, proxies=proxies)
    if resp.status_code == 200: 
        test_result = json.loads(resp.text)
        response['succeeded'] = True
        response['result_msg'] = 'Successfully connected to mistwired.'
    else:
        response['succeeded'] = False
        response['result_msg'] = 'Could not connect to mistwired Service'
except: 
    response['succeeded'] = False
    response['result_msg'] = 'Testing Failed..'

logging.debug(test_result)    
logging.info(f'Test Script Returned Response: {response}')
logging.info('===>Ending mistwired Test Script')