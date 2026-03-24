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
from requests.exceptions import HTTPError

WO_PROTOCOL = "https"
WO_SERVER_USERNAME= params.get("connect_workspaceone_user")
WO_SERVER_PASSWORD = params.get("connect_workspaceone_password")
WO_SERVER_ADDRESS = params.get("connect_workspaceone_server_url")
WO_API_KEY = params.get("connect_workspaceone_api_key")
WO_DEVICE_MAC_ADDRESS = params.get("mac")


# Proxy support-- requests only needs proxy_dict
workspaceone_proxy_enabled = params.get("connect_proxy_enable")
workspaceone_proxy_basic_auth_ip = params.get("connect_proxy_ip")
workspaceone_proxy_port = params.get("connect_proxy_port")
workspaceone_proxy_username = params.get("connect_proxy_username")
workspaceone_proxy_password = params.get("connect_proxy_password")
if workspaceone_proxy_enabled == "true":
	proxy_dict = workspaceone_proxy_support.get_proxy_dict(workspaceone_proxy_basic_auth_ip,
															workspaceone_proxy_port,
															workspaceone_proxy_username,
															workspaceone_proxy_password)
else:
	proxy_dict = None


PUSH_MSG_TYPE = params.get("connect_workspaceone_action_push_msg_type")
PUSH_MSG_BODY = params.get("connect_workspaceone_action_push_msg_body")

# create message body to send
def xml_message_body_for_push_notification(push_msg_type=PUSH_MSG_TYPE, push_msg_body=PUSH_MSG_BODY):
	MESSAGE_BODY = "<PushMessage xmlns=\"http://www.air-watch.com/servicemodel/resources\"> <MessageBody>" +push_msg_body+ "</MessageBody> <Application>AirWatch Agent</Application> <MessageType>" +push_msg_type+ "</MessageType> </PushMessage>"
	return(MESSAGE_BODY)

message_body = xml_message_body_for_push_notification()
headers, data = workspaceone_authentication_and_epoch.get_action_authentication_headers_with_xmlmessage_encoding(WO_SERVER_USERNAME, WO_SERVER_PASSWORD, WO_API_KEY, message_body)

# construct 'send push notification action' response to CounterACT
response = {}

action_url = None

device_id = params.get("connect_workspaceone_deviceID")
if device_id:
	action_url = WO_PROTOCOL + "://" + WO_SERVER_ADDRESS + "/api/mdm/devices/" + device_id + "/messages/push"

elif WO_DEVICE_MAC_ADDRESS:
	action_url = WO_PROTOCOL + "://" + WO_SERVER_ADDRESS + "/api/mdm/devices/messages/push&searchby=macaddress&id=" + WO_DEVICE_MAC_ADDRESS

if action_url:
	logging.debug("WO Action URL " + action_url)

	try:
		logging.debug("Starting Request Send Push notification action...")

		action_response = requests.request("POST", action_url, headers=headers, data=data, verify=ssl_verify, proxies=proxy_dict)
		logging.debug("WO Send Push notification response: " + str(action_response.text) )

		if (200 <= action_response.status_code <= 210):
			response["succeeded"] = True
		else:
			device_action_response = action_response.json()
			response["succeeded"] = False
			response["error"] = "Send Push notification Action Failed for Device ID= {}. {}".format(device_id, device_action_response.get("message") )

		logging.debug("Send Push notification action completed")
	except HTTPError as e:
		response["succeeded"] = False
		response["error"] = "Send Push notification failed. HTTP Response code: {}".format(e.code)
	except Exception as e:
		response["succeeded"] = False
		response["error"] = "Send Push notification failed. {}".format(str(e))
else:
	response["succeeded"] = False
	response["error"] = "Device identifier field is empty."
