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
import json
import requests

WO_SERVER_USERNAME= params.get("connect_workspaceone_user")
WO_SERVER_PASSWORD = params.get("connect_workspaceone_password")
WO_SERVER_ADDRESS = params.get("connect_workspaceone_server_url")
WO_API_KEY = params.get("connect_workspaceone_api_key")
WO_DEVICE_MAC_ADDRESS = params.get("mac")
WO_AUTH_MODE = params.get("connect_workspaceone_auth_mode")
WO_TOKEN_URL = params.get("connect_workspaceone_token_url")

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

wo_to_ct_props_map = {
	"DataProtectionEnabled": "connect_workspaceone_data_protection",
	"BlockLevelEncryption": "connect_workspaceone_block_level_encryption",
	"FileLevelEncryption": "connect_workspaceone_file_level_encryption",
	"IsPasscodePresent" : "connect_workspaceone_passcode_present",
	"IsPasscodeCompliant": "connect_workspaceone_passcode_compliance"
}

# construct 'sec attributes' response to CounterACT
response = {}

device_id = params.get("connect_workspaceone_deviceID")
if device_id:

	sec_attr_url = "https://" + WO_SERVER_ADDRESS + "/api/mdm/devices/" + device_id + "/security"

	logging.debug("WO Security attributes Resolve URL " + sec_attr_url)

	if WO_AUTH_MODE == "oauth":
		access_token = params.get("connect_authorization_token")
		if not access_token:
			response["succeeded"] = False
			response["error"] = "No OAuth token found. Check authorization."
		else:
			headers = workspaceone_authentication_and_epoch.get_oauth_headers(access_token, WO_API_KEY)
	else:
		headers = workspaceone_authentication_and_epoch.get_general_authentication_headers(WO_SERVER_USERNAME, WO_SERVER_PASSWORD, WO_API_KEY)

	if "succeeded" not in response:
	
		try:
			logging.debug("Starting WO sec attributes resolve...")

			prop_response_handle = requests.get(sec_attr_url, headers=headers, verify=ssl_verify, proxies=proxies)
			prop_response_handle.raise_for_status()
			prop_response = prop_response_handle.text
			prop_response_json = json.loads(prop_response)
			logging.debug("WO Sec attr Resolve response: " + str(prop_response))

			prop = prop_response_json

			properties = {}

			for prop_key, prop_val in prop.items():
				# all properties in response
				if prop_key in wo_to_ct_props_map.keys():
					prop_ct_name = wo_to_ct_props_map[prop_key]
					properties[prop_ct_name] = prop_val

				response["properties"] = properties
				logging.debug(response)

			logging.debug("Security attributes resolve completed")
		except requests.exceptions.HTTPError as e:
			response["succeeded"] = False
			response["error"] = "Could not connect to WorkspaceONE. HTTP Response code: {}".format(e.response.status_code)
		except Exception as e:
			response["succeeded"] = False
			response["error"] = "Could not connect to WorkspaceONE. {}".format(str(e))
else:
	response["succeeded"] = False
	response["error"] = "Device identifier field is empty."
