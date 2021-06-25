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

from datetime import datetime
from urllib import request
from urllib.request import HTTPError, URLError
import json
import logging

# The resolve script will require access to the NAC API
# Query the NAC API with MAC address to obtain the azureDeviceId
# Then query the GRAPH API with the azureDeviceId to obtain data

#
# FUNCTIONS
#
def date_utc_to_epoch(passed_utc):
    ''' Converts UTC Date to EPOCH
    '''
    # passed_utc = "10/18/2020 14:05:26"
    date_object = datetime.strptime(passed_utc, "%m/%d/%Y %H:%M:%S")

    epoch_date = int(datetime.timestamp(date_object))

    return epoch_date

#
# FUNCTIONS END
#

NAC_API_TO_CT_PROPS_MAP = {
    "azureDeviceId": "connect_intune_nac_azure_device_id",
    "complianceState": "connect_intune_nac_compliance_state",
    "deviceOwner": "connect_intune_nac_device_owner",
    "imei": "connect_intune_nac_imei",
    "isManaged": "connect_intune_nac_is_managed",
    "lastContactTimeUtc": "connect_intune_nac_last_contact_time_utc",
    "macAddress": "connect_intune_nac_mac_address",
    "manufacturer": "connect_intune_nac_manufacturer",
    "meid": "connect_intune_nac_meid",
    "model": "connect_intune_nac_model",
    "osVersion": "connect_intune_nac_os_version",
    "serialNumber": "connect_intune_nac_serial_number",
    "udid": "connect_intune_nac_udid"
}

# Get PANEL and Dependencies
P_SERVICE_URI = params.get("connect_intune_service_endpoint_uri")
P_MAC = params.get('mac')

# Need to convert tokens from STR to DICT
P_STR_TOKENS = params.get("connect_authorization_token", "{}")
DICT_TOKENS = json.loads(P_STR_TOKENS)

# Get NAC token
NAC_TOKEN = DICT_TOKENS.get("nac_token")

# construct 'device discovery' response to CounterACT
response = {}
# initialize list to hold all endpoints data
endpoints = []

if NAC_TOKEN:
    BEARER_HEADER = {"Authorization": "Bearer " + NAC_TOKEN}
    RESOLVE_URL = f"{P_SERVICE_URI}/devices/?querycriteria=macaddress&api-version=1.1&value={P_MAC}"

    logging.debug("RESOLVE QUERY : [%s]", RESOLVE_URL)

    try:
        logging.debug("Starting resolve...")

        # Check we have a MAC address
        if P_MAC:
            # Create proxy server
            proxy_server = intune_proxy_server.ConnectProxyServer()
            proxy_server.set_init(params)
            opener = proxy_server.get_urllib_request_https_opener(intune_proxy_server.ProxyProtocol.all, ssl_context)

            resolve_request = request.Request(RESOLVE_URL, headers=BEARER_HEADER)
            resolve_response = request.urlopen(resolve_request)

            resolve_response_json = json.loads(resolve_response.read())

            logging.debug("resolve_response_json: [%s]", resolve_response_json)

            # Check if the device is managed
            if resolve_response_json["isManaged"]:
                properties = {}

                for prop_key, prop_val in list(resolve_response_json.items()):
                    if prop_key in NAC_API_TO_CT_PROPS_MAP.keys():

                        # Convert UTC Date to Epoch
                        if prop_key == "lastContactTimeUtc":
                            prop_val = date_utc_to_epoch(prop_val)

                        prop_ct_name = NAC_API_TO_CT_PROPS_MAP[prop_key]
                        properties[prop_ct_name] = prop_val

                logging.debug("Resolve completed")
                logging.debug("Response : %s", properties)
                response["properties"] = properties
            else:
                # Device not enrolled
                logging.debug("NOT Managed : %s", P_MAC)
                response["error"] = "MAC Address not found, NOT Managed"
                response["properties"] = {}

        else:
            response["error"] = "** ERROR ** MAC Adreess is BLANK/None"

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
    response["error"] = "NAC Authorization token is empty."
