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
import time

logging.info('===>Starting mistwired  Assign Role Action Script')
logging.debug('Params for Action Script:')
logging.debug(params)

org_id = params.get("connect_mistwired_org_id")
api_key = params.get("connect_mistwired_api_key")
base_url = params.get("connect_mistwired_url")
is_bounce_enabled = params.get("connect_mistwired_bounce_port")
bounce_time = params.get("connect_mistwired_bounce_delay")
  
role = params.get("connect_mistwired_role")

switch_ip = params.get("sw_ip")
switch_port = params.get("sw_port_desc")

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

response = {}

# check parameters
if org_id is None:
    response["succeeded"] = False
    response["troubleshooting"] = "No Org ID set"
    
if api_key is None:
    response["succeeded"] = False
    response["troubleshooting"] = "No API key"

if role is None:
    response["succeeded"] = False
    response["troubleshooting"] = "No Role is set"

if switch_ip is None:
    response["succeeded"] = False
    response["troubleshooting"] = "No Switch IP dependancy"

if switch_port is None:
    response["succeeded"] = False
    response["troubleshooting"] = "No Switch port dependancy"

# 1. Get Switch MAC
if 'succeeded' not in response: 
    token = "token " + api_key
    headers = {"Authorization": token,"content-type": "application/json"}
    switch_mac_url = f"{base_url}/api/v1/orgs/{org_id}/devices/search?type=switch&ip={switch_ip}"
    logging.debug ("mistwired Switch MAC URL " + switch_mac_url)
    try:
        switch_mac_resp = requests.get(switch_mac_url, headers=headers, verify=ssl_verify, proxies=proxies)
        switch_mac_resp.raise_for_status()
        switch_mac_result = json.loads(switch_mac_resp.text)
        logging.debug (f"mistwired Switch MAC Result: {switch_mac_result}")
        try:
            switch_mac = switch_mac_result["results"][0]["mac"]
            site_id = switch_mac_result["results"][0]["site_id"]
            logging.info (f"MistWired found switch MAC: {switch_mac}")
            logging.info (f"MistWired found site ID: {site_id}")
        except IndexError:
            response["succeeded"] = False
            response["troubleshooting"] = "Failed to find Switch Mac Address / Site ID"

    except requests.exceptions.HTTPError as errh:
        response["succeeded"] = False
        response["troubleshooting"] = "Could not connect to Mist API. HTTP Error: {}".format(errh)
    except requests.exceptions.RequestException as err:
        response["succeeded"] = False
        response["troubleshooting"] = "{}".format(str(err))

# 2. Get port config
if 'succeeded' not in response:
    switch_id = "00000000-0000-0000-1000-" + switch_mac
    port_conf_url = f"{base_url}/api/v1/sites/{site_id}/devices/{switch_id}"
    logging.debug ("Mist Switch Config URL " + port_conf_url)
    try:
        switch_conf_resp = requests.get(port_conf_url, headers=headers, verify=ssl_verify, proxies=proxies)
        switch_conf_resp.raise_for_status()
        switch_conf_result = json.loads(switch_conf_resp.text)
        logging.debug (switch_conf_result)
        if "port_config" in switch_conf_result:
            port_conf = switch_conf_result["port_config"]
            logging.debug ("Switch port_conf:", port_conf) 
        else:
            port_conf = {}
            logging.debug ("no Switch port_conf")
    
    except requests.exceptions.HTTPError as errh:
        response["succeeded"] = False
        response["troubleshooting"] = "Could not connect to Mist API - Switch ID. HTTP Error: {}", format(errh)
    except requests.exceptions.RequestException as err:
        response["succeeded"] = False
        response["troubleshooting"] = "{}".format(str(err))

# 3. Port config settings
if 'succeeded' not in response:
    port_add = {switch_port: {"usage": role,"dynamic_usage": False, "description": "Set by Forescout"}}
    if switch_port in port_conf:
        orig_role = port_conf[switch_port]
        port_update = {"usage": role,"dynamic_usage": False, "description": "Set by Forescout"}
        port_conf[switch_port] = port_update
    else:
        port_conf.update(port_add)
        orig_role = None

    push_port = {"port_config":port_conf}

    # Push port configuration of Switch
    try:
        put_conf_request = requests.put(port_conf_url, data=json.dumps(push_port), headers=headers, verify=ssl_verify,  proxies=proxies)
        logging.debug (f'mistwired Put Conf Request: {put_conf_request}')
        if put_conf_request.status_code == 200: 
            response["succeeded"] = True
            
            # Mandatory Cookie added to enable undo action afterwards.
            response["cookie"] = json.dumps(orig_role)

        else:
            response["succeeded"] = False
            response["troubleshooting"] = "Failed to assign Role : {}".format(str(put_conf_request))

    except requests.exceptions.HTTPError as errh:
        response["succeeded"] = False
        response["troubleshooting"] = "Could not connect to Mist API - push conf. HTTP Error: {}", format(errh)

    except requests.exceptions.RequestException as err:
        response["succeeded"] = False
        response["troubleshooting"] = "{}".format(str(err))

# 4. Bounce Port (optional)
if response["succeeded"] == True:
    if is_bounce_enabled == "true":
        bounce_url = port_conf_url + "/bounce_port"
        bounce_port = {"ports":[switch_port]}
        time.sleep(int(bounce_time))
        try:
            switch_port_bounce = requests.post(bounce_url, data=json.dumps(bounce_port), headers=headers, verify=ssl_verify,  proxies=proxies)
            logging.debug (f'mistwired Port Bounce Request: {switch_port_bounce}')
            if switch_port_bounce == 200:
                logging.info (f'Port Bounced')
            else:
                logging.info (f'Port Bounce failed')
        except requests.exceptions.HTTPError as errh:
            logging.info (f'Could not connect to Mist API - Port Bounce. HTTP Error: {errh}')
        except requests.exceptions.RequestException as err:
            logging.info (f'{err}')

logging.info(f'Response: {response}')
logging.info('===>Ending mistwired Assign Role Action Script')