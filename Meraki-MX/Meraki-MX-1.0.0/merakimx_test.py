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

def normalise_mac(mac):
    if not mac:
        return None
    mac_clean = mac.replace(":", "").replace("-", "").replace(".", "").lower()
    return ":".join(mac_clean[i:i+2] for i in range(0, 12, 2))

MERAKI_API = params.get("connect_merakimx_api_key")
MERAKI_URL = params.get("connect_merakimx_url")
MERAKI_ORG = params.get("connect_merakimx_org")
MERAKI_TEST_MAC = params.get("connect_merakimx_testmac")
MERAKI_TEST_MAC = normalise_mac(MERAKI_TEST_MAC)
logging.debug("Meraki MX Test MAC: {}".format(MERAKI_TEST_MAC))

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
	logging.debug("Meraki MX Test Org Response: {}".format(org_resp_json))

	if org_resp_handle.status_code == 200:
		for entry in org_resp_json:
			if MERAKI_ORG:
				if entry.get("name") == MERAKI_ORG:
					orgId = entry.get("id")
					logging.debug("Meraki MX Test Org Found: {}".format(orgId))

	if not orgId:
		response["succeeded"] = False
		response["error"] = "Organization not found"
		logging.debug("Meraki MX Test: {}".format(response["error"]))
	else:
		net_url = base_url + "/organizations/" + orgId + "/networks"
		logging.debug("Meraki MX Test Network URL: {}".format(net_url))
		netIdList = []
		try:
			net_resp_handle = requests.get(net_url, headers=headers, verify=ssl_verify, proxies=proxies)
			net_resp_handle.raise_for_status()
			net_resp_json = net_resp_handle.json()
			logging.debug("Meraki MX Test Network Response: {}".format(net_resp_json))

			if net_resp_handle.status_code == 200:
				for entry in net_resp_json:
					netId = entry.get("id")
					if netId:
						netIdList.append(netId)

				logging.debug("Meraki MX Test Networks Found: {}".format(netIdList))

		except requests.exceptions.HTTPError as e:
			response["succeeded"] = False
			response["error"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {}".format(e.response.status_code)
			logging.debug("Meraki MX Test: {}".format(response["error"]))
		except Exception as e:
			response["succeeded"] = False
			response["error"] = "Could not connect to Meraki Dashboard API. {}".format(str(e))
			logging.debug("Meraki MX Test: {}".format(response["error"]))

		confNetId = None
		mxSerial = None
		mxName = None
		mxPort = None

		if not netIdList:
			response["succeeded"] = False
			response["error"] = "Network ID not Found"
			logging.debug("Meraki MX Test: {}".format(response["error"]))
		else:
			for netId in netIdList:
				client_url = base_url + "/networks/" + netId + "/clients?mac=" + MERAKI_TEST_MAC
				logging.debug("Meraki MX Test Client URL: {}".format(client_url))
				try:
					client_resp_handle = requests.get(client_url, headers=headers, verify=ssl_verify, proxies=proxies)
					client_resp_handle.raise_for_status()
					client_resp_json = client_resp_handle.json()
					logging.debug("Meraki MX Test Client Query Response: {}".format(client_resp_json))

					if client_resp_handle.status_code == 200:
						if client_resp_json:
							for entry in client_resp_json:
								mxSerial = entry.get("recentDeviceSerial")
								mxName = entry.get("recentDeviceName")						
								confNetId = netId
							
							logging.debug("Meraki MX Test Network Found: {}".format(confNetId))

				except requests.exceptions.HTTPError as e:
					response["succeeded"] = False
					response["error"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {}".format(e.response.status_code)
					logging.debug("Meraki MX Test: {}".format(response["error"]))
				except Exception as e:
					response["succeeded"] = False
					response["error"] = "Could not connect to Meraki Dashboard API. {}".format(str(e))
					logging.debug("Meraki MX Test: {}".format(response["error"]))

			if not confNetId:
				response["succeeded"] = False
				response["error"] = "Test Client MAC not Found"
				logging.debug("Meraki MX Test: {}".format(response["error"]))
			else:
				if not mxSerial:
					response["succeeded"] = False
					response["error"] = "MX Device not Found"
					logging.debug("Meraki MX Test: {}".format(response["error"]))
				else:
					lldp_url = base_url + "/devices/" + mxSerial + "/lldpCdp"
					logging.debug("Meraki MX Test LLDP/CDP URL: {}".format(lldp_url))
					try:
						lldp_resp_handle = requests.get(lldp_url, headers=headers, verify=ssl_verify, proxies=proxies)
						lldp_resp_handle.raise_for_status()
						lldp_resp_json = lldp_resp_handle.json()
						logging.debug("Meraki MX Test LLDP/CDP Response: {}".format(lldp_resp_handle.text))

						if lldp_resp_handle.status_code == 200:
							for port_name, port_data in lldp_resp_json.get("ports", {}).items():
								# Check deviceMac
								device_mac = port_data.get("deviceMac", "").lower()
								if device_mac == MERAKI_TEST_MAC.lower():
									mxPort = port_name
									logging.debug("Meraki MX Test Port matched via deviceMac on port: {}".format(mxPort))
								else:
									# Check lldp.portId as fallback
									lldp = port_data.get("lldp", {})
									lldp_port_id = lldp.get("portId", "").lower()
									if lldp_port_id == MERAKI_TEST_MAC.lower():
										mxPort = port_name
										logging.debug("Meraki MX Test Port matched via lldp.portId on port: {}".format(mxPort))

							logging.debug("Meraki MX Test LLDP/CDP Found: {}".format(mxPort))

					except requests.exceptions.HTTPError as e:
						response["succeeded"] = False
						response["error"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {}".format(e.response.status_code)
						logging.debug("Meraki MX Test: {}".format(response["error"]))
					except Exception as e:
						response["succeeded"] = False
						response["error"] = "Could not connect to Meraki Dashboard API. {}".format(str(e))
						logging.debug("Meraki MX Test: {}".format(response["error"]))

					if not mxPort:
						response["succeeded"] = False
						response["error"] = "MX Port not Found"	
						logging.debug("Meraki MX Test: {}".format(response["error"]))			
					else:
						mxPortNumber = mxPort.replace("port", "")
						port_url = base_url + "/networks/" + confNetId + "/appliance/ports/" + mxPortNumber
						logging.debug("Meraki MX Test Port Query URL: {}".format(port_url))
						try:
							port_resp_handle = requests.get(port_url, headers=headers, verify=ssl_verify, proxies=proxies)
							port_resp_handle.raise_for_status()
							port_resp_json = port_resp_handle.json()
							logging.debug("Meraki MX Test Port Query Response: {}".format(port_resp_json))

							mxPortType = None
							mxVlan = None

							if port_resp_handle.status_code == 200:
								mxPortType = port_resp_json.get("type")
								if mxPortType == "access":
									mxVlan = port_resp_json.get("vlan")
								elif mxPortType == "trunk":
									mxVlan = port_resp_json.get("allowedVlans")

							logging.debug("Meraki MX Test Port Query Found: VLAN {}, Port Type {}".format(mxVlan, mxPortType))

						except requests.exceptions.HTTPError as e:
							response["succeeded"] = False
							response["error"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {}".format(e.response.status_code)
							logging.debug("Meraki MX Test: {}".format(response["error"]))
						except Exception as e:
							response["succeeded"] = False
							response["error"] = "Could not connect to Meraki Dashboard API. {}".format(str(e))
							logging.debug("Meraki MX Test: {}".format(response["error"]))

						if not mxVlan or not mxPortType:
							response["succeeded"] = False
							response["error"] = "Port and VLAN not Found"
							logging.debug("Meraki MX Test: {}".format(response["error"]))
						else:
							test_response_start = "Test device found.\nMAC Address: {}\nMX Appliance: {}\nMX Port: {}\n".format(MERAKI_TEST_MAC, mxName, mxPortNumber)
							if mxPortType == "access":
								test_response_end = "MX Port Type: {}\nMX VLAN: {}".format(mxPortType, mxVlan)
							elif mxPortType == "trunk":
								test_response_end = "MX Port Type: {}\nMX Trunk Allowed VLANs: {}".format(mxPortType, mxVlan)
							else:
								test_response_end = "MX Port Type: {}".format(mxPortType)
							test_response = test_response_start + test_response_end
							logging.debug("Meraki MX Test response: " + test_response)

							response["succeeded"] = True
							response["result_msg"] = str(test_response) 

except requests.exceptions.HTTPError as e:
	response["succeeded"] = False
	response["error"] = "Could not connect to Meraki Dashboard API. HTTP Response code: {}".format(e.response.status_code)
	logging.debug("Meraki MX Test: {}".format(response["error"]))
except Exception as e:
	response["succeeded"] = False
	response["error"] = "Could not connect to Meraki Dashboard API. {}".format(str(e))
	logging.debug("Meraki MX Test: {}".format(response["error"]))