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

import base64
import logging

import requests
from requests.exceptions import HTTPError

MI_PROTOCOL = "https"
MI_SERVER_USERNAME = params["connect_mobileironmdm_user"]
MI_SERVER_PASSWORD = params["connect_mobileironmdm_password"]
MI_SERVER_ADDRESS = params["connect_mobileironmdm_server_url"]

# mac assignment
MI_DEVICE_MAC_ADDRESS = params.get("mac")
if MI_DEVICE_MAC_ADDRESS is None:
    MI_DEVICE_MAC_ADDRESS = ""
# uid assignment
MI_DEVICE_UID = params.get("connect_mobileironmdm_device_uid")
if MI_DEVICE_UID is None:
    MI_DEVICE_UID = ""


def randomized_mac(mac=MI_DEVICE_MAC_ADDRESS):
    # return True if MAC address is randomized
    if mac == "":
        return False
    # any MAC address’ first octet that ends 2,6,A,E would be random
    if (mac[1] == "2") or (mac[1] == "6") or (mac[1] == "a") or (mac[1] == "e"):
        logging.debug("MAC is random: mac=" + str(mac))
        return True
    return False


mi_to_ct_props_map = {
    "compliant": "connect_mobileironmdm_compliance_state",
    "quarantined": "connect_mobileironmdm_quarantined",
    "blocked": "connect_mobileironmdm_blocked",
    "compromised": "connect_mobileironmdm_compromised",
    "status": "connect_mobileironmdm_status",
    "lastCheckInTime": "connect_mobileironmdm_last_check_in_time",
    "registrationTime": "connect_mobileironmdm_registration_time",
    "identifier": "connect_mobileironmdm_device_uid",
    "imei": "connect_mobileironmdm_imei",
    "imsi": "connect_mobileironmdm_imsi",
    "macAddress": "connect_mobileironmdm_mac_address",
    "manufacturer": "connect_mobileironmdm_manufacturer",
    "model": "connect_mobileironmdm_model",
    "os": "connect_mobileironmdm_os",
    "osVersion": "connect_mobileironmdm_os_version",
    "phoneNumber": "connect_mobileironmdm_phone_number",
    "serialNumber": "connect_mobileironmdm_serial_number",
    "userId": "connect_mobileironmdm_user_id",
    "userUuid": "connect_mobileironmdm_user_uuid",
    "ownership": "connect_mobileironmdm_ownership"
}

prop_url = ""
MI_IDENTIFIER = ""
# select resolve API using mac / uid
if randomized_mac() and MI_DEVICE_UID != "":
    # resolve with device uuid
    prop_url = MI_PROTOCOL + "://" + MI_SERVER_ADDRESS + "/msa/v1/cps/device/uuid"
    MI_IDENTIFIER = MI_DEVICE_UID
    logging.debug("Using uuid as key to resolve")
elif MI_DEVICE_MAC_ADDRESS != "":
    # resolve with MAC address -- even if randomized, in case uid is missing
    prop_url = MI_PROTOCOL + "://" + MI_SERVER_ADDRESS + "/msa/v1/cps/device/mac"
    MI_IDENTIFIER = MI_DEVICE_MAC_ADDRESS
    logging.debug("Using uuid as key to resolve")
logging.debug("MI Resolve URL " + prop_url)

auth_string = "{}:{}".format(MI_SERVER_USERNAME, MI_SERVER_PASSWORD)
base64string = base64.b64encode(auth_string.encode('utf-8'))
header_auth_string = "".join(chr(x) for x in base64string)
# logging.debug("Auth Basic " + header_auth_string)

payload = "{ \"identifiers\": [\"" + MI_IDENTIFIER + "\"] }"
logging.debug("Data-raw: " + payload)
data = payload.encode("utf-8")

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic ' + header_auth_string
}

# construct 'resolve' response to CounterACT
response = {}

if (MI_DEVICE_MAC_ADDRESS != "") or (MI_DEVICE_UID != ""):

    try:
        logging.debug("Starting resolve...")

        prop_response = requests.request("POST", prop_url, headers=headers, data=payload, verify=ssl_verify)
        logging.debug("MI Resolve response: " + str(prop_response.text.encode("utf-8")))

        prop = prop_response.json()[0]

        properties = {}

        for prop_key, prop_val in prop.items():
            # converting compliance state from boolean to string type
            if prop_key == "compliant":
                if prop_val:
                    prop_val = "true"
                else:
                    prop_val = "false"

            # remove ":" from mac address value
            if prop_key == "macAddress":
                prop_val = prop_val.replace(":", "")

            # all properties in response
            if prop_key in mi_to_ct_props_map.keys():
                prop_ct_name = mi_to_ct_props_map[prop_key]
                properties[prop_ct_name] = prop_val

        properties["connect_mobileironmdm_ios_device_jailbroken"] = False
        properties["connect_mobileironmdm_android_device_rooted"] = False
        # ios jailbroken or android rooted
        if properties["connect_mobileironmdm_compromised"]:
            if (properties.get("connect_mobileironmdm_os") == "IOS") or (
                    properties.get("connect_mobileironmdm_os") == "OSX"):
                properties["connect_mobileironmdm_ios_device_jailbroken"] = True
            elif properties.get("connect_mobileironmdm_os") == "ANDROID":
                properties["connect_mobileironmdm_android_device_rooted"] = True
            else:
                logging.debug(
                    "Resolve: Could not find connect_mobileironmdm_os: " + properties["connect_mobileironmdm_os"])
        # mdm managed
        if properties.get("connect_mobileironmdm_device_uid"):
            properties["connect_mobileironmdm_mdm_managed"] = True
        else:
            properties["connect_mobileironmdm_mdm_managed"] = False
        response["properties"] = properties
        logging.debug("Resolve completed")
    except HTTPError as e:
        response["succeeded"] = False
        response["error"] = "Could not connect to MobileIron. HTTP Response code: {}".format(e.code)
    except Exception as e:
        response["succeeded"] = False
        response["error"] = "Could not connect to MobileIron. {}".format(str(e))
else:
    response["succeeded"] = False
    response["error"] = "Device MDM identifier field is empty: MAC = {}, UID = {}.".format(MI_DEVICE_MAC_ADDRESS,
                                                                                       MI_DEVICE_UID)
