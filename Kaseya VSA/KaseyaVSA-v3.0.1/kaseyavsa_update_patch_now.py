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

# Additional values
vsa_agent_id = params.get("connect_kaseyavsa_agentid")
vsa_patch_ids = params["connect_kaseyavsa_missing_patchids"]

token = params["connect_authorization_token"]

logging.debug("**ACTION** Login to Kaseya VSA server [{}] Patch IDs [{}]".format(server,vsa_patch_ids))

if token != "":
    patch_action_code, patch_action_results = KASEYAVSA_API_LIB.KASEYAVSA_PATCH_UPDATE_NOW(server, port, token, vsa_agent_id, vsa_patch_ids, proxies)
    logging.debug("**ACTION** API Trigger Patch Now Query returned code [{}] and response [{}]".format(patch_action_code,patch_action_results))

    if patch_action_code == 200 or patch_action_code == 204:
        response["succeeded"] = True
    else:
        response["succeeded"] = False
        response["result_msg"] = "Received {} code from API query.".format(patch_action_code)
        logging.debug(response["result_msg"])
else:
    response["succeeded"] = False
    response["troubleshooting"] = "Did not get a 200 code from API connection."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))