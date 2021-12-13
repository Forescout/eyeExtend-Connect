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

response = {}

# SSL Verification
verify = ssl_verify

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

# Additional values
vsa_agent_id = params.get("connect_kaseyavsa_agentid")

token = params["connect_authorization_token"]

kaseyavsa_property_map = {
    "LastPatchScan": "connect_kaseyavsa_last_patch_scan_date"}


logging.debug("RESOLVE PATCH SCAN DATE: Login to VSA Server [{}]".format(server))

if token != "":
    logging.debug("PARAM Agent ID is [{}]".format(vsa_agent_id))
    properties = {}
    _date_time_str = ''

    if vsa_agent_id is not None:
        logging.debug("Attempting Patch Scan Date API Query for Agent ID [{}]".format(vsa_agent_id))
        query_code, query_results = KASEYAVSA_API_LIB.KASEYAVSA_QUERY_LAST_PATCH_SCAN(server, port, token, vsa_agent_id, verify, proxies)
        patch_details = query_results['Result']
        logging.debug("***PATCH SCAN DATE STATUS...***: Query Code: {} Data: {}".format(query_code,patch_details))

        if query_code == 200:
            _date_time_str = patch_details["LastPatchScan"]
            if _date_time_str is not None:
                _date_time_obj = datetime.datetime.strptime(_date_time_str, '%Y-%m-%dT%H:%M:%S')
                properties['connect_kaseyavsa_last_patch_scan_date'] = int(datetime.datetime.timestamp(_date_time_obj))
                properties['connect_kaseyavsa_has_patch_scan_history'] = True
                response["properties"] = properties
            else:
                properties['connect_kaseyavsa_has_patch_scan_history'] = False
                response["properties"] = properties
        else:
            properties['connect_kaseyavsa_has_patch_scan_history'] = False
            response["properties"] = properties

    else:
        logging.debug("NO value found for connect_kaseyavsa_agentid property..")
        response["error"] = "No Agent ID available to query the VSA server."       
else:
    response["error"] = "API Connection Failed, check configuration."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))