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

from urllib import request
from urllib.request import HTTPError, URLError
from datetime import datetime
import json
import logging

# The resolve script will require access to the GRAPTH API
# Query the NAC API with MAC address to obtain the azureDeviceId
# Then query the GRAPH API with the azureDeviceId to obtain data


INTUNE_TO_CT_PROPS_MAP = {
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
    "partnerReportedThreatState": 'connect_intune_partner_reported_threat_state',
    "managementAgent": "connect_intune_management_agent",
    "deviceEnrollmentType": "connect_intune_device_enrollment_type",
    "deviceRegistrationState": "connect_intune_device_registration_state",
    "isEncrypted": "connect_intune_is_encrypted",
    "userPrincipalName": "connect_intune_user_principal_name",
    "androidSecurityPatchLevel": "connect_intune_android_security_patch_level",
    "subscriberCarrier": "connect_intune_subscriber_carrier",
    "totalStorageSpaceInBytes": "connect_intune_total_storage_space_in_bytes",
    "freeStorageSpaceInBytes": "connect_intune_free_storage_space_in_bytes",
    "managedDeviceName": "connect_intune_managed_device_name"
}

# Get Azure Device ID Dependencies
AZURE_DEVICE_ID = params.get("connect_intune_nac_azure_device_id")

# Need to convert tokens from STR to DICT
P_STR_TOKENS = params.get("connect_authorization_token", "{}")
DICT_TOKENS = json.loads(P_STR_TOKENS)

# Get GRAPH token
GRAPH_TOKEN = DICT_TOKENS.get("graph_token")

response = {}
# initialize list to hold all endpoints data
endpoints = []

if GRAPH_TOKEN:
    BEARER_HEADER = {"Authorization": "Bearer " + GRAPH_TOKEN}
    SPACE = "%20"
    QUOTE = "%27"

    query_filter = "?$filter=azureADDeviceId" + SPACE + "eq" + SPACE + QUOTE + AZURE_DEVICE_ID + QUOTE
    resolve_url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices" + query_filter

    logging.info("RESOLVE QUERY : [%s]", resolve_url)

    try:
        logging.debug("Starting resolve...")
        if AZURE_DEVICE_ID:
            resolve_request = request.Request(resolve_url, headers=BEARER_HEADER)
            resolve_response = request.urlopen(resolve_request, context=ssl_context)
            polled_response_json = json.loads(resolve_response.read())

            prop = polled_response_json["value"][0]
            properties = {}
            for prop_key, prop_val in list(prop.items()):
                if prop_key == "lastSyncDateTime" or prop_key == "enrolledDateTime":
                    prop_val = int(datetime.strptime(prop_val, '%Y-%m-%dT%H:%M:%SZ').strftime('%s'))

                # Some customers we have seen lower case and capitalized values.
                # Force to capitalize
                if prop_key == "jailBroken":
                    prop_val = prop_val.capitalize()

                if prop_key in INTUNE_TO_CT_PROPS_MAP.keys():
                    prop_ct_name = INTUNE_TO_CT_PROPS_MAP[prop_key]
                    properties[prop_ct_name] = prop_val

            logging.debug("Resolve completed")
            logging.debug("properties : %s", properties)
            response["properties"] = properties
        else:
            response["error"] = "No active directory ID for this device"
    except HTTPError as e:
        response["succeeded"] = False
        response["error"] = "HTTP Error : Could not connect to Intune. Response code: {}".format(e.code)
    except URLError as e:
        response["succeeded"] = False
        response["error"] = "URL Error : Could not connect to Intune. {}".format(e.reason)
    except Exception as e:
        response["succeeded"] = False
        response["error"] = "Exception : Could not connect to Intune. {}".format(str(e))
else:
    response["succeeded"] = False
    response["error"] = "Authorization token is empty."
