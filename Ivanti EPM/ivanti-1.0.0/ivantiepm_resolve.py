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

import logging
import requests
import json

# Values from system.conf
server = params.get("connect_ivantiepm_server")
port = params.get("connect_ivantiepm_port")

# General Values
response = {}
endpoints = []
token = params.get("connect_authorization_token")

if "mac" in params:
    mac = params.get("mac")
    logging.debug("Retrieved Mac Address for API query [{}]".format(mac))
else:
    logging.debug("Mac Address not Found")
    exit()

# Ivanti to Forescout property map
ivanti_props_map = {
    "DeviceId":"connect_ivantiepm_deviceid",
    "Compliant":"connect_ivantiepm_compliance_status",
    "Reason":"connect_ivantiepm_compliance_reason"
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
url = "https://{}:{}/PatchApi/api/v1/Devices/Compliance?$filter=MacAddr eq '{}'".format(server,port,mac)

# Request content
payload = {}
headers = {"Authorization":"Bearer {}".format(token)}

logging.debug("***RESOLVE*** Querying Ivanti EPM API at {} for device with Mac Address '{}'".format(server,mac))

resp = requests.request("POST", url, headers=headers, data=payload, verify=ssl_verify, proxies=proxies)
resp_code = resp.status_code
json_resp = json.loads(resp.content)
logging.debug("API Query returned code [{}] and response [{}].".format(resp_code,str(json_resp)))

if token != "":

    if resp_code == 200:
            logging.debug("Response received [{}]".format(str(json_resp)))
            
            for endpoint_data in json_resp["value"]:
                properties = {}
                    
                for key, value in endpoint_data.items():
                    
                    if key in ivanti_props_map:
                    
                        properties[ivanti_props_map[key]] = value
                
                response["properties"] = properties

    else:
        response["error"] = "Did not get a 200 code from API query. HTTP Error: {} Please check permissions.".format(resp_code)
        logging.debug(response["error"])

else:
    response["error"] = "Failed to retrieve Token. Credentials or permissions may be wrong or disabled."
    logging.debug(response["error"])

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))