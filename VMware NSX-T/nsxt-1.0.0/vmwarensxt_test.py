"""
Copyright © 2023 Forescout Technologies, Inc.

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

import logging
from multiprocessing.sharedctypes import Value
import requests
import json
import base64
import time

# Values from system.conf
server = params.get("connect_vmwarensxt_server")
port = params.get("connect_vmwarensxt_port")
username = params.get("connect_vmwarensxt_username")
password = params.get("connect_vmwarensxt_password")

# General Values
response = {}
endpoints = []

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

# URL
base_url = "https://{}:{}/api/v1".format(server,port)

## Logical Switch (aka Segments) queries
ls_base_url = base_url + "/logical-switches"

# Auth string
authString = "{}:{}".format(username,password)

b64authString = base64.b64encode(bytes('%s' % (authString), 'ascii'))
auth_header = b64authString.decode('utf-8')

# Request content
headers = {"Authorization":"Basic {}".format(auth_header)}

# Basic connectivity
try:
    resp = requests.get(ls_base_url, headers=headers, verify=ssl_verify, proxies=proxies)
    resp_code = resp.status_code
    json_resp = json.loads(resp.content)
    resp.raise_for_status()
except requests.exceptions.HTTPError as errh:
    logging.debug("***NSX - POLL*** API Client Query returned HTTP error:{}".format(errh))
except requests.exceptions.ConnectionError as errc:
    logging.debug("***NSX - POLL*** API Client Query returned Connecting error:{}".format(errc))
except requests.exceptions.Timeout as errt:
    logging.debug("***NSX - POLL*** API Client Query returned Timeout error:{}".format(errt))
except requests.exceptions.RequestException as err:
    logging.debug("***NSX - POLL*** API Client Query returned error:{}".format(err))

if resp_code == 200:
    response["succeeded"] = True
    response["result_msg"]= "Connection successful."  
else:
    response["succeeded"] = False
    response["result_msg"] = "Did not get a 200 code from API query. https Error: {} Please check permissions.".format(resp_code)
    logging.debug(response["result_msg"])