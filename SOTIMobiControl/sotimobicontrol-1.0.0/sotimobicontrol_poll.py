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

import ipaddress
import logging
from multiprocessing.sharedctypes import Value
import requests
import json

# Values from system.conf
server = params.get("connect_sotimobicontrol_server")
port = params.get("connect_sotimobicontrol_port")
no_ip = params.get("connect_sotimobicontrol_noip")

# General Values
response = {}
endpoints = []
token = params.get("connect_authorization_token")

# SOTI MobiControl to Forescout property map
sotimobicontrol_props_map = {
    "DeviceId":"connect_sotimobicontrol_deviceid"
}

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

# Query Base URL
url = "https://{}:{}/MobiControl/api/devices".format(server,port)

# Request content
payload = {}
headers = {"Authorization":"Bearer {}".format(token)}

logging.debug("***POLL*** Querying SOTI MobiControl API at {}".format(server))

if token != "":

    total_count = 0
    query_num = 1
    req_count = 1000

    while req_count > 0:

        req_url = url + "?skip={}&take=1000".format(total_count)

        resp = requests.request("GET", req_url, headers=headers, data=payload, verify=ssl_verify, proxies=proxies)
        resp_code = resp.status_code
        json_resp = json.loads(resp.content)
        
        logging.debug("***POLL*** API Query number {} to [{}] returned code [{}]".format(query_num,req_url,resp_code))

        if resp_code == 200:

            req_count = len(json_resp)
            total_count += len(json_resp)

            logging.debug("***POLL*** Adding hosts without IP? [{}]".format(no_ip))

            if no_ip == "true":

                for endpoint_data in json_resp:

                    endpoint = {}
                    endpoint["mac"] = endpoint_data["MACAddress"]
                    properties = {}
                    
                    for key, value in endpoint_data.items():
                    
                        if key in sotimobicontrol_props_map:
                                
                            properties[sotimobicontrol_props_map[key]] = value
                    
                    endpoint["properties"] = properties
                    endpoints.append(endpoint)

            else:

                for endpoint_data in json_resp:
                
                    soti_ip = endpoint_data["HostName"]
                    try:
                        ip = ipaddress.ip_address(soti_ip)
                        ip_exists = True
                        logging.debug("***POLL*** IP Address [{}] is valid, proceeding...".format(soti_ip))

                    except ValueError:
                        ip_exists = False
                        logging.debug("***POLL*** IP Address [{}] not valid, moving on to next entry...".format(soti_ip))

                    if ip_exists:

                        endpoint = {}
                        endpoint["mac"] = endpoint_data["MACAddress"]
                        endpoint["ip"] = soti_ip
                        properties = {}
                        
                        for key, value in endpoint_data.items():
                        
                            if key in sotimobicontrol_props_map:
                                    
                                properties[sotimobicontrol_props_map[key]] = value
                        
                        endpoint["properties"] = properties
                        endpoints.append(endpoint)

            response["endpoints"] = endpoints
            
            logging.debug("***POLL*** Completed query number {}, sending response: [{}]".format(query_num,response["endpoints"]))

            query_num += 1

        else:
            response["error"] = "Did not get a 200 code from API query. HTTP Error: {} Please check permissions.".format(resp_code)
            logging.debug(response["error"])
            break

else:
    response["error"] = "Failed to retrieve Token. Credentials or permissions may be wrong or disabled."
    logging.debug(response["error"])

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))