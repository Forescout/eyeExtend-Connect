"""
Copyright © 2026 Forescout Technologies, Inc.

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

MERAKI_API = params.get("connect_merakimx_api_key")
MERAKI_URL = params.get("connect_merakimx_url")
MERAKI_ORG = params.get("connect_merakimx_org")

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

cache = {}

base_url = "https://" + MERAKI_URL + "/api/v1"

headers = {
    "X-Cisco-Meraki-API-Key": MERAKI_API,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

org_url = base_url +"/organizations"

orgId = None

try:
	org_resp_handle = requests.get(org_url, headers=headers, verify=ssl_verify, proxies=proxies)
	org_resp_handle.raise_for_status()
	org_resp_json = org_resp_handle.json()
	logging.debug("Meraki MX Cache Org Response: {}".format(org_resp_json))

	if org_resp_handle.status_code == 200:
		for entry in org_resp_json:
			if MERAKI_ORG:
				if entry.get("name") == MERAKI_ORG:
					orgId = entry.get("id")
					logging.debug("Meraki MX Cache Org Found: {}".format(orgId))

except requests.exceptions.HTTPError as e:
	response["error"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {}".format(e.response.status_code)
	logging.debug("Meraki MX Cache: {}".format(response["error"]))
except Exception as e:
	response["error"] = "Could not connect to Meraki Dashboard API. {}".format(str(e))
	logging.debug("Meraki MX Cache: {}".format(response["error"]))

if not orgId:
	response["error"] = "Organization not found"
	logging.debug("Meraki MX Cache: {}".format(response["error"]))	
else:
	cache["orgId"] = orgId
	net_url = base_url + "/organizations/" + orgId + "/networks"
	logging.debug("Meraki MX Cache Network URL: {}".format(net_url))	
	netIdList = []
	try:
		net_resp_handle = requests.get(net_url, headers=headers, verify=ssl_verify, proxies=proxies)
		net_resp_handle.raise_for_status()
		net_resp_json = net_resp_handle.json()
		logging.debug("Meraki MX Cache Network Response: {}".format(net_resp_json))

		if net_resp_handle.status_code == 200:
			for entry in net_resp_json:
				netId = entry.get("id")
				if netId:
					netIdList.append(netId)

			logging.debug("Meraki MX Cache Networks Found: {}".format(netIdList))

	except requests.exceptions.HTTPError as e:
		response["error"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {}".format(e.response.status_code)
		logging.debug("Meraki MX Cache: {}".format(response["error"]))
	except Exception as e:
		response["error"] = "Could not connect to Meraki Dashboard API. {}".format(str(e))
		logging.debug("Meraki MX Cache: {}".format(response["error"]))
	
	if not netIdList:
		response["error"] = "Networks not found"
		logging.debug("Meraki MX Cache: {}".format(response["error"]))
	else:
		cache["networks"] = netIdList
		response["connect_app_instance_cache"] = json.dumps(cache)
		logging.debug("Meraki MX Cache: {}".format(response))