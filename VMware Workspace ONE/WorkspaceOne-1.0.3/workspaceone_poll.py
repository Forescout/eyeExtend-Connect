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
    "EnrollmentStatus": "connect_workspaceone_enrollment_status",
    "ComplianceStatus": "connect_workspaceone_compliance_status",
    "IsCloudBackupEnabled": "connect_workspaceone_cloud_connectivity",
    "Imei": "connect_workspaceone_imei",
    "CompromisedStatus": "connect_workspaceone_compromised_status",
    "LastSeen": "connect_workspaceone_last_seen_timestamp",
    "LastEnrolledOn": "connect_workspaceone_enrollment_status_timestamp",
    "LastComplianceCheckOn": "connect_workspaceone_compliance_status_timestamp",
    "LastCompromisedCheckOn": "connect_workspaceone_compromised_status_timestamp"
}


headers = workspaceone_authentication_and_epoch.get_general_authentication_headers(WO_SERVER_USERNAME, WO_SERVER_PASSWORD, WO_API_KEY)


# construct 'device discovery' response to CounterACT
response = {}
# initialize list to hold all endpoints data
endpoints = []
# page number from which to begin polling
page_number = 0
# page size variable indicating number of devices per page
server_response_page_size = params.get("connect_workspaceone_server_response_page_size")

try:
	logging.debug("Starting WorkspaceONE Discovery...")

	while(True):
		# get all devices until server returns 204 No Content
		poll_url = WO_PROTOCOL + "://" + WO_SERVER_ADDRESS + "/api/mdm/devices/search?page=" + str(page_number) + "&pagesize=" + str(server_response_page_size)
		logging.debug("WO Poll URL " + poll_url)

		poll_request = urllib.request.Request(poll_url, headers=headers)
		poll_response_handle = opener.open(poll_request)
		# stop if status code == 204
		if poll_response_handle.getcode() == 204:
			break

		# else load response
		poll_response = poll_response_handle.read().decode("utf-8")
		logging.debug("WO Poll Server Response: " + poll_response)

		poll_response_json = json.loads(poll_response)

		devices = poll_response_json.get("Devices")
		total_devices = poll_response_json.get("Total")
		for i in range(total_devices):
			properties = {}
			endpoint = {}
			prop = devices[i]
			for poll_key, poll_val in prop.items():
				# mac address for discovery of endpoint -- convert to lowercase
				if poll_key == "MacAddress":
					if poll_val == "":
						# terminate inner loop and move on to next device if MAC absent
						break
					endpoint["mac"] = poll_val.lower()
					logging.debug("WO device MAC: " + endpoint["mac"])

				# all properties in response
				if poll_key in wo_to_ct_props_map.keys():
					# ignore empty property values
					if poll_val == "":
						continue

					# extract deviceID
					if poll_key == "Id":
						poll_val = str(poll_val["Value"])

					# convert the timestamps to epoch timestamps
					elif poll_key in ["LastCompromisedCheckOn", "LastEnrolledOn", "LastComplianceCheckOn", "LastSeen"]:
						epochtimestamp = workspaceone_authentication_and_epoch.convert_to_epoch(poll_val)
						# ignore erroneous timestamp
						if epochtimestamp is None:
							continue
						poll_val = epochtimestamp

					poll_ct_name = wo_to_ct_props_map[poll_key]
					properties[poll_ct_name] = poll_val

			endpoint["properties"] = properties
			endpoints.append(endpoint)

		# check next page for device list
		page_number += 1

	response["endpoints"] = endpoints
	
	logging.debug("Poll completed")
except HTTPError as e:
	response["succeeded"] = False
	response["error"] = "Could not connect to WorkspaceONE. HTTP Response code: {}".format(e.code)
except Exception as e:
	response["succeeded"] = False
	response["error"] = "Could not connect to WorkspaceONE. {}".format(str(e))
	