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
Change Device Profile
'''

from urllib import request, parse
from urllib.request import HTTPError, URLError
import json
import logging

# VARS
# CONFIGURATION
P_BEARER_TOKEN = params.get("connect_authorization_token")
P_SERVER_ADDRESS = params.get("connect_clearpass_server_address")

A_REAUTH_PROFILE = params.get("connect_clearpass_reauthorize_profile")

EP_CONNECT_CLEARPASS_ID = params.get("connect_clearpass_id")

if P_BEARER_TOKEN:
    logging.debug("P_BEARER_TOKEN (First 10) : %s", P_BEARER_TOKEN[0:10])

# Build PROFILE payload
PROFILE_PAYLOAD = {
    "confirm_reauthorize": "true",
    "reauthorize_profile": A_REAUTH_PROFILE
}

PROFILE_PAYLOAD_JSON = json.dumps(PROFILE_PAYLOAD)

logging.debug("PROFILE_PAYLOAD : %s", PROFILE_PAYLOAD)

# AUTH endcoded payload
PROFILE_PAYLOAD_ENCODE = PROFILE_PAYLOAD_JSON.encode("utf-8")

response = {}

# Check we have ClearPass ID
if EP_CONNECT_CLEARPASS_ID:
    # Check we have a Bearer token
    if P_BEARER_TOKEN:
        # Build Request
        REAUTH_URL = f"https://{P_SERVER_ADDRESS}/api/session/{EP_CONNECT_CLEARPASS_ID}/reauthorize"
        # Header
        BEARER_HEADER = {"Authorization": "Bearer " + P_BEARER_TOKEN,
                         "Content-Type": "application/json",
                         "Accept": "application/json"}

        logging.debug("REAUTH_URL : %s", REAUTH_URL)

        try:
            reauth_request = request.Request(
                REAUTH_URL, data=PROFILE_PAYLOAD_ENCODE, headers=BEARER_HEADER, method="POST")
            reauth_response = request.urlopen(reauth_request, context=ssl_context)
            reauth_response_json = json.loads(reauth_response.read())

            logging.debug("reauth_response_json : %s", reauth_response_json)
            response['succeeded'] = True
            response['result_msg'] = f'Successfully re-authorized. \n{reauth_response_json}'

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
    response["error"] = "ClearPass ID null/empty"
