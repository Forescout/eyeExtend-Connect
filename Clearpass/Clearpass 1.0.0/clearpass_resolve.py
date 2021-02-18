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

''' ClearPass Resolve Endpoints
'''

from urllib import request, parse
from urllib.request import HTTPError, URLError
import json
import logging

# Mapping between clearpass response fields to CounterACT properties
CLEARPASS_TO_CT_PROPS_MAP = {
    "id": "connect_clearpass_id",
    "username": "connect_clearpass_username",
    "nasipaddress": "connect_clearpass_nasipaddress",
    "acctstarttime": "connect_clearpass_acctstarttime",
    "callingstationid": "connect_clearpass_callingstationid",
    "calledstationid": "connect_clearpass_calledstationid",
    "cppm_uuid": "connect_clearpass_cppm_uuid",
    "nasportid": "connect_clearpass_nasportid",
    "nasporttype": "connect_clearpass_nasporttype",
    "nas_name": "connect_clearpass_nas_name",
    "acctterminatecause": "connect_clearpass_acctterminatecause",
    "servicetype": "connect_clearpass_servicetype",
    "ssid": "connect_clearpass_ssid",
    "ap_name": "connect_clearpass_ap_name",
    "mac_address": "connect_clearpass_mac_address",
    "visitor_name": "connect_clearpass_visitor_name",
    "visitor_company": "connect_clearpass_visitor_company",
    "visitor_phone": "connect_clearpass_visitor_phone",
    "sponsor_name": "connect_clearpass_sponsor_name",
    "sponsor_email": "connect_clearpass_sponsor_email",
    "sponsor_profile_name": "connect_clearpass_sponsor_profile_name",
    "role_name": "connect_clearpass_role_name"
}
# VARS
# CONFIGURATION
P_BEARER_TOKEN = params.get("connect_authorization_token")
P_SERVER_ADDRESS = params.get("connect_clearpass_server_address")

EP_MAC = params.get('mac')

response = {}
if EP_MAC:
    if P_BEARER_TOKEN:

        # Build Request
        RESOLVE_URL = f'https://{P_SERVER_ADDRESS}/api/session?filter={{"mac_address":"{EP_MAC}","acctstoptime":{{"$exists":false}}}}&calculate_count=true'
        # Header
        BEARER_HEADER = {"Authorization": "Bearer " + P_BEARER_TOKEN,
                         "Accept": "application/json"}
        logging.debug("RESOLVE_URL : %s", RESOLVE_URL)

        try:
            resolve_request = request.Request(RESOLVE_URL, headers=BEARER_HEADER, method="GET")
            resolve_response = request.urlopen(resolve_request, context=ssl_context)
            resolve_response_json = json.loads(resolve_response.read())

            count = resolve_response_json["count"]
            logging.debug(f'Count : {count}')
            properties = {}
            # Check Count
            if count != 0:
                for i in range(count):
                    endpoint = {}
                    prop = resolve_response_json["_embedded"]["items"][i]
                    if prop["state"] == "active":
                        for prop_key, prop_val in list(prop.items()):
                            if prop_key in CLEARPASS_TO_CT_PROPS_MAP.keys():
                                prop_ct_name = CLEARPASS_TO_CT_PROPS_MAP[prop_key]
                                properties[prop_ct_name] = prop_val
                        logging.debug("Resolve completed")
                        logging.debug("properties : %s", properties)
                        response["properties"] = properties
                        break
            else:
                response["error"] = "No ClearPass Device Found"

        except HTTPError as e:
            response["succeeded"] = False
            response["error"] = "HTTP Error : Could not connect to ClearPass. Response code: {}".format(e.code)

        except URLError as e:
            response["succeeded"] = False
            response["error"] = "URL Error : Could not connect to ClearPass. {}".format(e.reason)

        except Exception as e:
            response["succeeded"] = False
            response["error"] = "Exception : Could not connect to ClearPass. {}".format(str(e))

    else:
        response["succeeded"] = False
        response["error"] = "Authorization token is empty."
else:
    response["succeeded"] = False
    response["error"] = "No MAC Address, can not query ClearPass."
