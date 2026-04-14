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
import time

def normalise_mac(mac):
    if not mac:
        return None
    mac_clean = mac.replace(":", "").replace("-", "").replace(".", "").lower()
    return ":".join(mac_clean[i:i+2] for i in range(0, 12, 2))

MERAKI_API = params.get("connect_merakimx_api_key")
MERAKI_URL = params.get("connect_merakimx_url")

mxPort = params.get("connect_merakimx_mxport")
mxPortType = params.get("connect_merakimx_mxporttype")
mxTargetVlan = params.get("cookie")
netId = params.get("connect_merakimx_mxnetid")

# Requests Proxy
is_proxy_enabled = params.get("connect_proxy_enable")
if is_proxy_enabled == "true":
	proxy_ip = params.get("connect_proxy_ip")
	proxy_port = params.get("connect_proxy_port")
	proxy_user = params.get("connect_proxy_username")
	proxy_pass = params.get("connect_proxy_password")
	if not proxy_user:
		proxy_url = f"https://{proxy_ip}:{proxy_port}"
		proxies = {"https": proxy_url}
	else:
		proxy_url = f"https://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
		proxies = {"https": proxy_url}
else:
	proxies = None

response = {}
properties = {}
action_status = {}

base_url = "https://" + MERAKI_URL + "/api/v1"

headers = {
	"X-Cisco-Meraki-API-Key": MERAKI_API,
	"Content-Type": "application/json",
	"Accept": "application/json",
}

if not mxTargetVlan:
	response["succeeded"] = False
	response["troubleshooting"] = "Previous VLAN not found"
	action_status["status"] = response["troubleshooting"]
	action_status["time"] = int(time.time())
	logging.debug("Meraki MX Revert VLAN: {}".format(response["troubleshooting"]))

elif not mxPort:
	response["succeeded"] = False
	response["troubleshooting"] = "Host MX port property not resolved — run resolve first"
	action_status["status"] = response["troubleshooting"]
	action_status["time"] = int(time.time())
	logging.debug("Meraki MX Revert VLAN: {}".format(response["troubleshooting"]))

elif not mxPortType:
	response["succeeded"] = False
	response["troubleshooting"] = "Host MX port type property not resolved — run resolve first"
	action_status["status"] = response["troubleshooting"]
	action_status["time"] = int(time.time())
	logging.debug("Meraki MX Revert VLAN: {}".format(response["troubleshooting"]))

elif not netId:
	response["succeeded"] = False
	response["troubleshooting"] = "Host MX Network ID property not resolved — run resolve first"
	action_status["status"] = response["troubleshooting"]
	action_status["time"] = int(time.time())
	logging.debug("Meraki MX Revert VLAN: {}".format(response["troubleshooting"]))

else:
	if "mac" in params:
		mac = params.get("mac")
		mac = normalise_mac(mac)
		logging.debug("Meraki MX Revert VLAN MAC: {}".format(mac))

		client_url = base_url + "/networks/" + netId + "/clients?mac=" + mac
		try:
			client_resp_handle = requests.get(client_url, headers=headers, verify=ssl_verify, proxies=proxies)
			client_resp_handle.raise_for_status()
			client_resp_json = client_resp_handle.json()
			logging.debug("Meraki MX Revert VLAN Client Response: {}".format(client_resp_json))

			if client_resp_handle.status_code == 200:
				if mxPortType == "access":
					payload = {
						"type": "access",
						"vlan": int(mxTargetVlan)
					}
				elif mxPortType == "trunk":
					response["succeeded"] = False
					response["troubleshooting"] = "Meraki MX port type is Trunk. Cannot assign VLAN on Trunk port."
					action_status["status"] = response["troubleshooting"]
					action_status["time"] = int(time.time())
					logging.debug("Meraki MX Revert VLAN: {}".format(response["troubleshooting"]))
					payload = None
				else:
					response["succeeded"] = False
					response["troubleshooting"] = "Unknown port type: {}".format(mxPortType)
					action_status["status"] = response["troubleshooting"]
					action_status["time"] = int(time.time())
					logging.debug("Meraki MX Revert VLAN: {}".format(response["troubleshooting"]))
					payload = None

				if payload:
					port_url = base_url + "/networks/" + netId + "/appliance/ports/" + mxPort
					try:
						put_resp_handle = requests.put(port_url, headers=headers, verify=ssl_verify, proxies=proxies, data=json.dumps(payload))
						put_resp_handle.raise_for_status()
						put_resp_json = put_resp_handle.json()
						logging.debug("Meraki MX Revert VLAN PUT Response: {}".format(put_resp_json))

						if put_resp_handle.status_code == 200:
							properties["connect_merakimx_mxvlan"] = mxTargetVlan
							response["succeeded"] = True
							response["properties"] = properties
							action_status["status"] = "Succeeded"
							action_status["time"] = int(time.time())
							logging.debug("Meraki MX Revert VLAN Assignment succeeded. Port: {} VLAN Reverted: {}".format(mxPort, mxTargetVlan))

					except requests.exceptions.HTTPError as e:
						if e.response.status_code == 400:
							response["succeeded"] = False
							response["troubleshooting"] = "VLAN change rejected by Meraki — VLAN {} may not exist on this MX. HTTP 400".format(mxTargetVlan)
							action_status["status"] = response["troubleshooting"]
							action_status["time"] = int(time.time())						
						else:
							response["succeeded"] = False
							response["troubleshooting"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {}".format(e.response.status_code)
							action_status["status"] = response["troubleshooting"]
							action_status["time"] = int(time.time())
							logging.debug("Meraki MX Revert VLAN: {}".format(response["troubleshooting"]))
					except Exception as e:
						response["succeeded"] = False
						response["troubleshooting"] = "Could not connect to Meraki Dashboard API. {}".format(str(e))
						action_status["status"] = response["troubleshooting"]
						action_status["time"] = int(time.time())
						logging.debug("Meraki MX Revert VLAN: {}".format(response["troubleshooting"]))
			else:
				response["succeeded"] = False
				response["troubleshooting"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {} Response: {}".format(client_resp_handle.status_code, client_resp_handle.text)
				action_status["status"] = response["troubleshooting"]
				action_status["time"] = int(time.time())
				logging.debug("Meraki MX Revert VLAN: {}".format(response["troubleshooting"]))

		except requests.exceptions.HTTPError as e:
			response["succeeded"] = False
			response["troubleshooting"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {}".format(e.response.status_code)
			action_status["status"] = response["troubleshooting"]
			action_status["time"] = int(time.time())
			logging.debug("Meraki MX Revert VLAN: {}".format(response["troubleshooting"]))
		except Exception as e:
			response["succeeded"] = False
			response["troubleshooting"] = "Could not connect to Meraki Dashboard API. {}".format(str(e))
			action_status["status"] = response["troubleshooting"]
			action_status["time"] = int(time.time())
			logging.debug("Meraki MX Revert VLAN: {}".format(response["troubleshooting"]))
