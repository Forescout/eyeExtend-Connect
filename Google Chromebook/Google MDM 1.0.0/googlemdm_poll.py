'''
Copyright © 2020 Forescout Technologies, Inc.

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
'''

import jwt  # PyJWT version 1.6.1 as of the time of authoring
import uuid
import json
import urllib.request
import time
from time import gmtime, strftime, sleep
from datetime import datetime, timedelta

# ***** START - AUTH API CONFIGURATION ***** #
timeout = 1800  # 30 minutes from now
now = datetime.utcnow()
timeout_datetime = now + timedelta(seconds=timeout)
epoch_time = int((now - datetime(1970, 1, 1)).total_seconds())
epoch_timeout = int((timeout_datetime - datetime(1970, 1, 1)).total_seconds())
jti_val = str(uuid.uuid4())

# Get the token
bearer_token = params["connect_authorization_token"]


request_header = {
    'Authorization': 'Bearer ' + bearer_token,
    'Accept': 'application/json'
}
request_url = 'https://www.googleapis.com/admin/directory/v1/customer/my_customer/devices/chromeos?projection=full'
endpoints=[]

request = urllib.request.Request(request_url, headers=request_header)
resp = urllib.request.urlopen(request, context=ssl_context)
request_response = json.loads(resp.read())
response_json = request_response
# print(response_json)

# Mapping between GoogleMDM API response fields to CounterACT properties
googlemdm_to_ct_props_map = {
    "serialNumber": "connect_googlemdm_serial_number",
    "deviceId": "connect_googlemdm_device_id",
    "macAddress": "connect_googlemdm_mac_address",
    "status": "connect_googlemdm_status",
    "annotatedAssetId": "connect_googlemdm_asset_id",
    "platformVersion": "connect_googlemdm_platform_version",
    "firmwareVersion": "connect_googlemdm_firmware_version",
    "annotatedUser": "connect_googlemdm_user",
    "lastSync": "connect_googlemdm_last_sync",
    "model": "connect_googlemdm_model",
    "osVersion": "connect_googlemdm_os_version",
    "bootMode": "connect_googlemdm_boot_mode",
    "orgUnitPath": "connect_googlemdm_org_unit",
    "annotatedLocation": "connect_googlemdm_location",
    "notes": "connect_googlemdm_notes"
    }

for endpoint_data in request_response["chromeosdevices"]:
    # Setup the endpoint json for push to forescout
    endpoint={}


    # Setup the device mac address that is to be loaded
    endpoint["mac"] = response_json["chromeosdevices"][0]["macAddress"]
    properties = {}

    # Extraction of the device information from GoogleMDM
    device_diskvolume_01 = response_json["chromeosdevices"][0]["diskVolumeReports"][0]["volumeInfo"][0]["volumeId"]
    device_diskvolume_01_free = response_json["chromeosdevices"][0]["diskVolumeReports"][0]["volumeInfo"][0]["storageFree"]
    properties[googlemdm_to_ct_props_map["deviceId"]] = response_json["chromeosdevices"][0]["deviceId"]
    properties[googlemdm_to_ct_props_map["serialNumber"]] = response_json["chromeosdevices"][0]["serialNumber"]
    properties[googlemdm_to_ct_props_map["status"]] = response_json["chromeosdevices"][0]["status"]
    properties[googlemdm_to_ct_props_map["annotatedAssetId"]] = response_json["chromeosdevices"][0]["annotatedAssetId"]
    properties[googlemdm_to_ct_props_map["orgUnitPath"]] = response_json["chromeosdevices"][0]["orgUnitPath"]
    properties[googlemdm_to_ct_props_map["model"]] = response_json["chromeosdevices"][0]["model"]
    properties[googlemdm_to_ct_props_map["platformVersion"]] = response_json["chromeosdevices"][0]["platformVersion"]
    properties[googlemdm_to_ct_props_map["firmwareVersion"]] = response_json["chromeosdevices"][0]["firmwareVersion"]
    properties[googlemdm_to_ct_props_map["osVersion"]] = response_json["chromeosdevices"][0]["osVersion"]
    properties[googlemdm_to_ct_props_map["bootMode"]] = response_json["chromeosdevices"][0]["bootMode"]
    properties[googlemdm_to_ct_props_map["annotatedUser"]] = response_json["chromeosdevices"][0]["annotatedUser"]
    properties[googlemdm_to_ct_props_map["lastSync"]] = response_json["chromeosdevices"][0]["lastSync"]
    properties[googlemdm_to_ct_props_map["macAddress"]] = response_json["chromeosdevices"][0]["macAddress"]
    properties[googlemdm_to_ct_props_map["annotatedLocation"]] = response_json["chromeosdevices"][0]["annotatedLocation"]
    properties[googlemdm_to_ct_props_map["notes"]] = response_json["chromeosdevices"][0]["notes"]

    endpoint["properties"] = properties
    endpoints.append(endpoint)
response = {}
response["endpoints"] = endpoints
