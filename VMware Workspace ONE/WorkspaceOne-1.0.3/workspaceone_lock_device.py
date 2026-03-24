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

response = {}

if WO_AUTH_MODE == "oauth":
	access_token = params.get("connect_authorization_token")
	if not access_token:
		response["succeeded"] = False
		response["error"] = "No OAuth token found. Check authorization."
	else:
		headers = workspaceone_authentication_and_epoch.get_oauth_headers(access_token, WO_API_KEY)
else:
	headers = workspaceone_authentication_and_epoch.get_general_authentication_headers(WO_SERVER_USERNAME, WO_SERVER_PASSWORD, WO_API_KEY)

# construct 'check-in action' response to CounterACT

if "succeeded" not in response:
	action_url = None

	device_id = params.get("connect_workspaceone_deviceID")
	if device_id:
		action_url = "https://" + WO_SERVER_ADDRESS + "/api/mdm/devices/" + device_id + "/commands?command=lock"

	elif WO_DEVICE_MAC_ADDRESS:
		action_url = "https://" + WO_SERVER_ADDRESS + "/api/mdm/devices/commands?command=lock&searchby=macaddress&id=" + WO_DEVICE_MAC_ADDRESS

	if action_url:
		logging.debug("WO Action URL " + action_url)

		try:
			logging.debug("Starting Request Lock device action...")

			action_response = requests.request("POST", action_url, headers=headers, verify=ssl_verify, proxies=proxies)
			action_response.raise_for_status()
			logging.debug("WO Lock device response: " + str(action_response.text) )

			if action_response.status_code == 210:
				device_lock_response = action_response.json()
				response["succeeded"] = False
				response["error"] = "Lock device Action Failed for Device ID= {}. {}".format(device_id, device_lock_response.get("message") )
			else:
				response["succeeded"] = True
				logging.debug("Lock device action completed")

		except requests.exceptions.HTTPError as e:
			response["succeeded"] = False
			response["error"] = "Lock device failed. HTTP Response code: {}".format(e.response.status_code)
		except Exception as e:
			response["succeeded"] = False
			response["error"] = "Lock device failed. {}".format(str(e))

	else:
		response["succeeded"] = False
		response["error"] = "Device identifier field is empty."