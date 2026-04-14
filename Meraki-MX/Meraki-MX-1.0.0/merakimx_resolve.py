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

def normalise_mac(mac):
    if not mac:
        return None
    mac_clean = mac.replace(":", "").replace("-", "").replace(".", "").lower()
    return ":".join(mac_clean[i:i+2] for i in range(0, 12, 2))

MERAKI_API = params.get("connect_merakimx_api_key")
MERAKI_URL = params.get("connect_merakimx_url")
MERAKI_ORG = params.get("connect_merakimx_org")
cache = params.get("connect_app_instance_cache")

if isinstance(cache, str):
	cache = json.loads(cache)
	
logging.debug("Meraki MX Resolve Cache: {}".format(cache))

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
properties = {}

base_url = "https://" + MERAKI_URL + "/api/v1"

headers = {
    "X-Cisco-Meraki-API-Key": MERAKI_API,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

if not cache:
	response["error"] = "Cache not available"
	logging.debug("Meraki MX Resolve: {}".format(response["error"]))
else:
	if "mac" in params:
		mac = params.get("mac")
		mac = normalise_mac(mac)
		logging.debug("Meraki MX Resolve MAC: {}".format(mac))		
		netIdList = cache["networks"]
		logging.debug("Meraki MX Resolve Networks Found: {}".format(netIdList))

		confNetId = None
		mxSerial = None
		mxName = None
		mxPort = None

		if not netIdList:
			response["error"] = "Network ID not Found"
			logging.debug("Meraki MX Resolve: {}".format(response["error"]))
		else:
			for netId in netIdList:
				client_url = base_url + "/networks/" + netId + "/clients?mac=" + mac
				logging.debug("Meraki MX Resolve Client URL: {}".format(client_url))
				try:
					client_resp_handle = requests.get(client_url, headers=headers, verify=ssl_verify, proxies=proxies)
					client_resp_handle.raise_for_status()
					client_resp_json = client_resp_handle.json()
					logging.debug("Meraki MX Resolve Client Query Response: {}".format(client_resp_json))

					if client_resp_handle.status_code == 200:
						if client_resp_json:
							for entry in client_resp_json:
								mxSerial = entry.get("recentDeviceSerial")
								mxName = entry.get("recentDeviceName")
								confNetId = netId

							logging.debug("Meraki MX Resolve Network Found: {}".format(confNetId))

				except requests.exceptions.HTTPError as e:
					response["error"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {}".format(e.response.status_code)
					logging.debug("Meraki MX Resolve: {}".format(response["error"]))
				except Exception as e:
					response["error"] = "Could not connect to Meraki Dashboard API. {}".format(str(e))
					logging.debug("Meraki MX Resolve: {}".format(response["error"]))

			if not confNetId:
				response["error"] = "Client MAC not Found"
				logging.debug("Meraki MX Resolve: {}".format(response["error"]))
			else:
				if not mxSerial:
					response["error"] = "MX Device not Found"
					logging.debug("Meraki MX Resolve: {}".format(response["error"]))
				else:
					lldp_url = base_url + "/devices/" + mxSerial + "/lldpCdp"
					logging.debug("Meraki MX Resolve LLDP/CDP URL: {}".format(lldp_url))
					try:
						lldp_resp_handle = requests.get(lldp_url, headers=headers, verify=ssl_verify, proxies=proxies)
						lldp_resp_handle.raise_for_status()
						lldp_resp_json = lldp_resp_handle.json()
						logging.debug("Meraki MX Resolve LLDP/CDP Response: {}".format(lldp_resp_handle.text))

						if lldp_resp_handle.status_code == 200:
							for port_name, port_data in lldp_resp_json.get("ports", {}).items():
								# Check deviceMac
								device_mac = port_data.get("deviceMac", "").lower()
								if device_mac == mac.lower():
									mxPort = port_name
									logging.debug("Meraki MX Resolve Port matched via deviceMac on port: {}".format(mxPort))
								else:
									# Check lldp.portId as fallback
									lldp = port_data.get("lldp", {})
									lldp_port_id = lldp.get("portId", "").lower()
									if lldp_port_id == mac.lower():
										mxPort = port_name
										logging.debug("Meraki MX Resolve Port matched via lldp.portId on port: {}".format(mxPort))

							logging.debug("Meraki MX Resolve LLDP/CDP Found: {}".format(mxPort))

					except requests.exceptions.HTTPError as e:
						response["error"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {}".format(e.response.status_code)
						logging.debug("Meraki MX Resolve: {}".format(response["error"]))
					except Exception as e:
						response["error"] = "Could not connect to Meraki Dashboard API. {}".format(str(e))
						logging.debug("Meraki MX Resolve: {}".format(response["error"]))

					if not mxPort:
						response["error"] = "MX Port not Found"	
						logging.debug("Meraki MX Resolve: {}".format(response["error"]))			
					else:
						mxPortNumber = mxPort.replace("port", "")
						port_url = base_url + "/networks/" + confNetId + "/appliance/ports/" + mxPortNumber
						logging.debug("Meraki MX Resolve Port Query URL: {}".format(port_url))
						try:
							port_resp_handle = requests.get(port_url, headers=headers, verify=ssl_verify, proxies=proxies)
							port_resp_handle.raise_for_status()
							port_resp_json = port_resp_handle.json()
							logging.debug("Meraki MX Resolve Port Query Response: {}".format(port_resp_json))

							mxPortType = None
							mxVlan = None

							if port_resp_handle.status_code == 200:
								mxPortType = port_resp_json.get("type")
								if mxPortType == "access":
									mxVlan = str(port_resp_json.get("vlan"))
								elif mxPortType == "trunk":
									mxVlan = port_resp_json.get("allowedVlans")

							logging.debug("Meraki MX Resolve Port Query Found: VLAN {}, Port Type {}".format(mxVlan, mxPortType))

						except requests.exceptions.HTTPError as e:
							response["error"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {}".format(e.response.status_code)
							logging.debug("Meraki MX Resolve: {}".format(response["error"]))
						except Exception as e:
							response["error"] = "Could not connect to Meraki Dashboard API. {}".format(str(e))
							logging.debug("Meraki MX Resolve: {}".format(response["error"]))

						if not mxVlan or not mxPortType:
							response["error"] = "Port and VLAN not Found"
							logging.debug("Meraki MX Resolve: {}".format(response["error"]))
						else:
							properties["connect_merakimx_mxnetid"] = confNetId
							properties["connect_merakimx_mxname"] = mxName
							properties["connect_merakimx_mxport"] = mxPortNumber
							properties["connect_merakimx_mxporttype"] = mxPortType
							properties["connect_merakimx_mxvlan"] = mxVlan
							response["properties"] = properties
							logging.debug("Meraki MX Resolve response: {}".format(response))