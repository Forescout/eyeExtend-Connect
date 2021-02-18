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

A_CUSTOM_ATTRIBUTES = params.get("connect_clearpass_custom_attributes")

EP_MAC = params.get("mac")

# Build JSON Custom payload convert to DICT
ATTRIBUTE_PAYLOAD_DICT = json.loads(A_CUSTOM_ATTRIBUTES)
# Dump DICT to STR
ATTRIBUTE_PAYLOAD_JSON_STR = json.dumps(ATTRIBUTE_PAYLOAD_DICT)

logging.debug("ATTRIBUTE_PAYLOAD_JSON_STR: %s", ATTRIBUTE_PAYLOAD_JSON_STR)

# AUTH endcoded payload
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
            custom_attr_request = request.Request(
                ATTRIBUTE_URL, data=ATTRIBUTE_PAYLOAD_ENCODE, headers=BEARER_HEADER, method="PATCH")
            custom_attr_response = request.urlopen(custom_attr_request, context=ssl_context)
            custom_attr_response_json = json.loads(custom_attr_response.read())

            logging.debug("custom_attr_response_json : %s", custom_attr_response_json)
            response['succeeded'] = True
            response['result_msg'] = f'Successfully updated endpoint custom attribute. \n{custom_attr_response_json}'

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
