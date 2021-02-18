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

'''
Modify ClearPass endpoint attribute Forescout-ACTION
'''

from urllib import request, parse
from urllib.request import HTTPError, URLError
import json
import logging

# VARS
# CONFIGURATION
P_BEARER_TOKEN = params.get("connect_authorization_token")
P_SERVER_ADDRESS = params.get("connect_clearpass_server_address")

if P_BEARER_TOKEN:
    logging.debug("P_BEARER_TOKEN (First 10) : %s", P_BEARER_TOKEN[0:10])

A_FS_ACTION = params.get("connect_clearpass_fs_action_attribute")

EP_MAC = params.get("mac")

# Build JSON Forescout-ACTION payload
ATTRIBUTE_PAYLOAD = {
    "attributes": {
        "Forescout-ACTION": A_FS_ACTION
    }
}

ATTRIBUTE_PAYLOAD_JSON_STR = json.dumps(ATTRIBUTE_PAYLOAD)

logging.debug("ATTRIBUTE_PAYLOAD_JSON: %s", ATTRIBUTE_PAYLOAD_JSON_STR)

# endcoded payload
ATTRIBUTE_PAYLOAD_ENCODE = ATTRIBUTE_PAYLOAD_JSON_STR.encode("utf-8")

response = {}

# Check we have ClearPass MAC Address
if EP_MAC:
    # Check we have a Bearer token
    if P_BEARER_TOKEN:
        # Build Request
        ATTRIBUTE_URL = f"https://{P_SERVER_ADDRESS}/api/endpoint/mac-address/{EP_MAC}"
        # Header
        BEARER_HEADER = {"Authorization": "Bearer " + P_BEARER_TOKEN,
                         "Content-Type": "application/json",
                         "Accept": "application/json"}

        logging.debug("ATTRIBUTE_URL : %s", ATTRIBUTE_URL)

        try:
            action_attr_request = request.Request(
                ATTRIBUTE_URL, data=ATTRIBUTE_PAYLOAD_ENCODE, headers=BEARER_HEADER, method="PATCH")
            action_attr_response = request.urlopen(action_attr_request, context=ssl_context)
            action_attr_response_json = json.loads(action_attr_response.read())

            logging.debug("action_attr_response_json : %s", action_attr_response_json)
            response['succeeded'] = True
            response['result_msg'] = f'Successfully updated Forescout-ACTION attribute. \n{action_attr_response_json}'

        except HTTPError as e:
            response["succeeded"] = False
            response["error"] = "HTTP Error : Could not connect to ClearPass. Response code: {}".format(
                e.code)

        except URLError as e:
            response["succeeded"] = False
            response["error"] = "URL Error : Could not connect to ClearPass. {}".format(
                e.reason)

        except Exception as e:
            response["succeeded"] = False
            response["error"] = "Exception : Could not connect to ClearPass. {}".format(e)

    else:
        response["succeeded"] = False
        response["error"] = "Authorization token is empty."
else:
    response["succeeded"] = False
    response["error"] = "ClearPass MAC Address null/empty"
