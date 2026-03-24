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
import urllib.request
from urllib.request import HTTPError


WO_PROTOCOL = "https"
WO_SERVER_USERNAME= params.get("connect_workspaceone_user")
WO_SERVER_PASSWORD = params.get("connect_workspaceone_password")
WO_SERVER_ADDRESS = params.get("connect_workspaceone_server_url")
WO_API_KEY = params.get("connect_workspaceone_api_key")
WO_DEVICE_MAC_ADDRESS = params.get("mac")
WO_SHOULD_RESOLVE = params.get("connect_workspaceone_disable_resolve_request") == "false"

# Proxy support
workspaceone_proxy_enabled = params.get("connect_proxy_enable")
workspaceone_proxy_basic_auth_ip = params.get("connect_proxy_ip")
workspaceone_proxy_port = params.get("connect_proxy_port")
workspaceone_proxy_username = params.get("connect_proxy_username")
workspaceone_proxy_password = params.get("connect_proxy_password")
opener = workspaceone_proxy_support.handle_proxy_configuration(workspaceone_proxy_enabled,
							workspaceone_proxy_basic_auth_ip,
							workspaceone_proxy_port,
							workspaceone_proxy_username,
							workspaceone_proxy_password, ssl_context)


wo_to_ct_props_map = {
	"Id": "connect_workspaceone_deviceID",
	"Udid": "connect_workspaceone_udid",
    "SerialNumber": "connect_workspaceone_serial_number",
    "Ownership": "connect_workspaceone_ownership",
    "Platform": "connect_workspaceone_platform",
    "Model": "connect_workspaceone_model",
    "OperatingSystem": "connect_workspaceone_os_version",
    "PhoneNumber": "connect_workspaceone_phone_number",
    "LastSeen": "connect_workspaceone_last_seen_timestamp",
    "EnrollmentStatus": "connect_workspaceone_enrollment_status",
    "ComplianceStatus": "connect_workspaceone_compliance_status",
    "LastEnrolledOn": "connect_workspaceone_enrollment_status_timestamp",
    "LastComplianceCheckOn": "connect_workspaceone_compliance_status_timestamp",
    "IsCloudBackupEnabled": "connect_workspaceone_cloud_connectivity",
    "Imei": "connect_workspaceone_imei",
    "CompromisedStatus": "connect_workspaceone_compromised_status",
    "LastCompromisedCheckOn": "connect_workspaceone_compromised_status_timestamp"
}


prop_url = WO_PROTOCOL + "://" + WO_SERVER_ADDRESS + "/api/mdm/devices?searchby=macaddress&id=" + WO_DEVICE_MAC_ADDRESS
logging.debug("Resolving for MAC address: " + str(WO_DEVICE_MAC_ADDRESS))
logging.debug("WO Resolve URL " + prop_url)

headers = workspaceone_authentication_and_epoch.get_general_authentication_headers(WO_SERVER_USERNAME, WO_SERVER_PASSWORD, WO_API_KEY)

response = {}
logging.debug("Should skip property resolve: " + str(WO_SHOULD_RESOLVE))
if WO_SHOULD_RESOLVE:
	try:
		logging.debug("Starting WorkspaceONE resolve...")

		prop_request = urllib.request.Request(prop_url, headers=headers)
		prop_response_handle = opener.open(prop_request)

		prop_response = prop_response_handle.read().decode("utf-8")
		prop_response_json = json.loads(prop_response)

		prop = prop_response_json

		properties = {}

		for prop_key, prop_val in prop.items():
			# mac address value should be lowercase
			if prop_key == "MacAddress":
				prop_val = prop_val.lower()

			# all properties in response
			if prop_key in wo_to_ct_props_map.keys():
				# extract deviceID
				if prop_key == "Id":
					prop_val = str(prop_val["Value"])

				# convert the timestamps to epoch timestamps
				elif prop_key in ["LastCompromisedCheckOn", "LastEnrolledOn", "LastComplianceCheckOn", "LastSeen"]:
					epochtimestamp = workspaceone_authentication_and_epoch.convert_to_epoch(prop_val)
					# ignore erroneous timestamp
					if epochtimestamp is None:
						continue
					prop_val = epochtimestamp
				prop_ct_name = wo_to_ct_props_map[prop_key]
				properties[prop_ct_name] = prop_val
				logging.debug("Resolved Property: {} = {}".format(prop_ct_name, prop_val) )

		response["properties"] = properties

		logging.debug("Resolve completed")
	except HTTPError as e:
		response["succeeded"] = False
		response["error"] = "Could not connect to WorkspaceONE. HTTP Response code: {}".format(e.code)
		logging.debug("Resolve Error: " + response["error"])
	except Exception as e:
		response["succeeded"] = False
		response["error"] = "Could not connect to WorkspaceONE. {}".format(str(e))
		logging.debug("Resolve Error: " + response["error"])
else:
	logging.debug("Resolve disabled")
	response["succeeded"] = False
	response["error"] = "Property resolve disabled by app configuration"