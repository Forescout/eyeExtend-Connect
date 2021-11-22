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

token = params["connect_authorization_token"]

kaseyavsa_property_map = {
    "AgentId": "connect_kaseyavsa_agentid",
    "MachineGroup": "connect_kaseyavsa_machine_group"
}

logging.debug("RESOLVE: Login to VSA Server [{}]".format(server))

if token != "":
    properties = []
    if "ip" in params:
        _ipadd = params["ip"]
        logging.debug("Attempting API Query for IP Address [{}]".format(_ipadd))
        query_code, query_results = KASEYAVSA_API_LIB.KASEYAVSA_QUERY_AGENT(server, port, token, _ipadd, proxies)

        if not query_results["TotalRecords"] == 0:
            
            logging.debug("API Query returned code [{}] and response [{}]".format(query_code,query_results))

            ctr = 0
            for entry in query_results['Result']:
                if query_results["Result"][ctr]["Online"] in [1,2,11,12]:
                    host_details = query_results["Result"][ctr]
                    properties = {}
                    for key, value in host_details.items():
                        if key in kaseyavsa_property_map:
                            if key != "LastSeenDate":
                                if value != "":
                                    properties[kaseyavsa_property_map[key]] = str(value)
                                else:
                                    properties[kaseyavsa_property_map[key]] = "None"
                            else:
                                _date_time_obj = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
                                properties[kaseyavsa_property_map[key]] = int(datetime.datetime.timestamp(_date_time_obj))
                                
                    response["properties"] = properties
                ctr += 1

        else:
            response["error"] = "Could not find this endpoint in the Kaseya VSA Server."
    else:
        response["error"] = "No IP address to query the endpoint."
else:
    response["error"] = "API Connection Failed, check configuration."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))