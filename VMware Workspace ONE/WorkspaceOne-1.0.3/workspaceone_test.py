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

import json
import logging
import requests

WO_SERVER_USERNAME= params.get("connect_workspaceone_user")
WO_SERVER_PASSWORD = params.get("connect_workspaceone_password")
WO_SERVER_ADDRESS = params.get("connect_workspaceone_server_url")
WO_API_KEY = params.get("connect_workspaceone_api_key")
WO_DEVICE_MAC_ADDRESS = params.get("connect_workspaceone_testmac")
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

if not WO_DEVICE_MAC_ADDRESS:
	# resolve without test mac for system info
	test_url = "https://" + WO_SERVER_ADDRESS + "/api/system/info"
	logging.debug("Test MAC not provided")
else:
	# resolve properties for MAC address
	test_url = "https://" + WO_SERVER_ADDRESS + "/api/mdm/devices?searchby=macaddress&id=" + WO_DEVICE_MAC_ADDRESS
	logging.debug("Resolving for Test MAC address")
logging.debug("WO Test URL " + test_url)

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
		test_response_handle = requests.get(test_url, headers=headers, verify=ssl_verify, proxies=proxies)
		test_response_handle.raise_for_status()
		test_response = test_response_handle.text
		logging.debug("WO Test response: " + test_response)

		test_response_json = json.loads(test_response)
		
		if not WO_DEVICE_MAC_ADDRESS:
			test_response_start = "\nTest device MAC address Not Found.\nSuccessfully established connection to the Workspace ONE Server.\n\nSystem info:\n"
			test_response_str = "ProductName: \"{}\",\n  ProductVersion: \"{}\"".format(test_response_json["ProductName"], test_response_json["ProductVersion"])
		else:
			test_response_start = ""
			test_response_str = ",\n  ".join(
			{ "\""+str(p)+"\"" + ": " + "\""+str(v)+"\"" for p,v in test_response_json.items() if type(test_response_json[p]) != dict } )
		test_response_final = test_response_start + "\n{\n  " + test_response_str + "\n}"
		logging.debug("WO Test FINAL response: " + test_response_final)

		response["succeeded"] = True
		response["result_msg"] = str(test_response_final) 
	except requests.exceptions.HTTPError as e:
		response["succeeded"] = False
		response["error"] = "Could not connect to WorkspaceOne. HTTP Response code: {}".format(e.response.status_code)
	except Exception as e:
		response["succeeded"] = False
		response["error"] = "{}".format(str(e))
