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

poll_url = MI_PROTOCOL + "://" + MI_SERVER_ADDRESS + "/msa/v1/cps/device/?limit=200"
logging.debug("MI Polling URL " + poll_url)

auth_string = "{}:{}".format(MI_SERVER_USERNAME, MI_SERVER_PASSWORD)
base64string = base64.b64encode(auth_string.encode('utf-8'))
header_auth_string = "".join(chr(x) for x in base64string)
# logging.debug("Auth Basic " + header_auth_string)

payload = "{ \"identifiers\": [] }"
logging.debug("Data-raw: " + payload)

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic ' + header_auth_string
}

# construct 'device discovery' response to CounterACT
response = {}
# initialize list to hold all endpoints data
endpoints = []

try:
    logging.debug("Starting poll...")

    poll_response = requests.request("GET", poll_url, headers=headers, data=payload, verify=ssl_verify)
    logging.debug("MI Poll response: " + str(poll_response.text.encode("utf-8")))

    polled_response_json = poll_response.json()

    count = polled_response_json["results"]

    for i in range(count):
        prop = polled_response_json["searchResults"][i]
        endpoint = {}
        properties = {}
        # skip adding hosts without a MAC to the response
        if "macAddress" not in prop.keys():
            logging.debug("MAC address not found for host with Device UID: " + prop["identifier"])
            continue
        else:
            for prop_key, prop_val in list(prop.items()):
                # compliance state should be string type
                if prop_key == "compliant":
                    if prop_val:
                        prop_val = "true"
                    else:
                        prop_val = "false"
                # mac address is the key for every endpoint
                if prop_key == "macAddress":
                    prop_val = prop_val.replace(":", "")
                    endpoint["mac"] = prop_val

                if prop_key in mi_to_ct_props_map.keys():
                    prop_ct_name = mi_to_ct_props_map[prop_key]
                    properties[prop_ct_name] = prop_val

        endpoint["properties"] = properties
        endpoints.append(endpoint)

    logging.debug("Poll completed")
    response["endpoints"] = endpoints

except HTTPError as e:
    response["succeeded"] = False
    response["error"] = "Could not connect to MobileIron. HTTP Response code: {}".format(e.code)
except Exception as e:
    response["succeeded"] = False
    response["error"] = "Could not connect to MobileIron. {}".format(str(e))
