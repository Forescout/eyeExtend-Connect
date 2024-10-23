"""
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
"""

from urllib.request import HTTPError, URLError
from datetime import datetime
import json

intune_to_ct_props_map = {
    "intune_source_account_tenant_id": "connect_intune_source_account_tenant_id",
    "id": "connect_intune_id",
    "userId": "connect_intune_user_id",
    "deviceName": "connect_intune_device_name",
    "managedDeviceOwnerType": "connect_intune_managed_device_owner_type",
    "enrolledDateTime": "connect_intune_enrolled_datetime",
    "lastSyncDateTime": "connect_intune_last_sync_datetime",
    "operatingSystem": "connect_intune_operating_system",
    "complianceState": "connect_intune_compliance_state",
    "jailBroken": "connect_intune_jail_broken",
    "osVersion": "connect_intune_os_version",
    "azureADRegistered": "connect_intune_aad_registered",
    "emailAddress": "connect_intune_email_address",
    "azureADDeviceId": "connect_intune_aad_device_id",
    "isSupervised": "connect_intune_is_supervised",
    "model": "connect_intune_model",
    "manufacturer": "connect_intune_manufacturer",
    "serialNumber": "connect_intune_serial_number",
    "phoneNumber": "connect_intune_phone_number",
    "userDisplayName": "connect_intune_user_display_name",
    "wiFiMacAddress": "connect_intune_wifi_mac_address",
    "imei": "connect_intune_imei",
    "meid": "connect_intune_meid",
    "partnerReportedThreatState": "connect_intune_partner_reported_threat_state"
}

# construct 'device discovery' response to CounterACT
response = {}
# initialize list to hold all endpoints data
endpoints = []

if "connect_authorization_token" in params and params.get("connect_authorization_token") != "":
    access_token = params.get("connect_authorization_token")
    user_header = {"Authorization": "Bearer " + access_token}
    poll_url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices"
    try:
        logging.debug("Starting poll...")
        while True:
            poll_request = urllib.request.Request(poll_url, headers=user_header)
            poll_response = urllib.request.urlopen(poll_request, context=ssl_context)
            polled_response_json = json.loads(poll_response.read())

            count = polled_response_json["@odata.count"]
            for i in range(count):
                endpoint = {}
                prop = polled_response_json["value"][i]
                properties = {}
                for prop_key, prop_val in list(prop.items()):
                    if prop_key == "lastSyncDateTime" or prop_key == "enrolledDateTime":
                        prop_val = int(datetime.strptime(prop_val, "%Y-%m-%dT%H:%M:%SZ").strftime('%s'))

                    # store mac address as a separate endpoint key
                    if prop_key == "wiFiMacAddress":
                        endpoint["mac"] = prop_val

                    if prop_key in intune_to_ct_props_map.keys():
                        prop_ct_name = intune_to_ct_props_map[prop_key]
                        properties[prop_ct_name] = prop_val

                endpoint["properties"] = properties
                endpoints.append(endpoint)

            if "@odata.nextLink" in polled_response_json:
                poll_url = polled_response_json["@odata.nextLink"]
            else:
                break

        logging.debug("Poll completed")
        response["endpoints"] = endpoints
    except HTTPError as e:
        response["succeeded"] = False
        response["error"] = "Could not connect to Intune. Response code: {}".format(e.code)
    except URLError as e:
        response["succeeded"] = False
        response["error"] = "Could not connect to Intune. {}".format(e.reason)
    except Exception as e:
        response["succeeded"] = False
        response["error"] = "Could not connect to Intune. {}".format(str(e))
else:
    response["succeeded"] = False
    response["error"] = "Authroization token is empty."
