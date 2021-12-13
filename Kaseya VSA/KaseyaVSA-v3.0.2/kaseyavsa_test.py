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

import json
import requests
import logging

response = {}

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

# Values from system.conf
server = params["connect_kaseyavsa_server_ipaddress"]
port = params["connect_kaseyavsa_server_port"]
conn_type = params["connect_kaseyavsa_conn_type"]

token = params["connect_authorization_token"]

test_url = "https://{}:{}/api/v1.0/assetmgmt/assets".format(server,port)

logging.debug("Attempting to test connectivity to Kaseya VSA server with the following parameters: address={} port={} connection type={}".format(server,port,conn_type))

if token != "":

    test_header = {"Authorization": "Bearer " + token}
    test_resp = requests.request("GET", test_url, headers=test_header, verify=ssl_verify, proxies=proxies)
    test_code = test_resp.status_code
    json_resp = json.loads(test_resp.content)
    vsa_assets = json_resp["TotalRecords"]
    logging.debug("API Client Query returned code [{}] and response [{}]".format(test_code,vsa_assets))

    if test_code == 200:
            response["succeeded"] = True
            response["result_msg"] = "Connection successful. Found {} Kaseya VSA assets".format(vsa_assets)
            logging.debug(response["result_msg"])
    else:
        response["succeeded"] = False
        response["result_msg"] = "Did not get a 200 code from List Asset API query. HTTP Error: {} Please check credentials...".format(test_code)
        logging.debug(response["result_msg"])
else:    
    response["succeeded"] = False
    response["result_msg"] = "Failed to retrieve Access Token. Credentials may be wrong or the account provided is disabled."
    logging.debug(response["result_msg"])