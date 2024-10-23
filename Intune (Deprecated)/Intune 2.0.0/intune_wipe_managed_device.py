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

from urllib import request, parse
from urllib.request import HTTPError, URLError
import json
import logging

# Get Panel vars
P_CONNECT_INTUNE_SKIP_MACOSUNLOCKCODE = params.get("connect_intune_skip_macosunlockcode")

# Need to convert tokens from STR to DICT
P_STR_TOKENS = params.get("connect_authorization_token", "{}")
DICT_TOKENS = json.loads(P_STR_TOKENS)

# Get Managed Device ID
EP_DEVICE_ID = params.get("connect_intune_id")

# ACTION Properties
A_KEEPENROLLMENTDATA = params.get("connect_intune_wipe_device_keepenrollmentdata")
A_KEEPUSERDATA = params.get("connect_intune_wipe_device_keepuserdata")
A_MACOSUNLOCKCODE = params.get("connect_intune_wipe_device_macosunlockcode")

logging.debug("A_KEEPENROLLMENTDATA: %s", A_KEEPENROLLMENTDATA)
logging.debug("A_KEEPUSERDATA: %s", A_KEEPUSERDATA)
logging.debug("A_MACOSUNLOCKCODE: %s", A_MACOSUNLOCKCODE)

# Get GRAPH token
GRAPH_DELEGATED_TOKEN = DICT_TOKENS.get("graph_delegated_token")

# Decide if we need to send the macosunlockcode
if P_CONNECT_INTUNE_SKIP_MACOSUNLOCKCODE == A_MACOSUNLOCKCODE:
    # SKIP sending unlock code
    BODY_PAYLOAD = {
        "keepEnrollmentData": A_KEEPENROLLMENTDATA,
        "keepUserData": A_KEEPUSERDATA
    }
else:
    BODY_PAYLOAD = {
        "keepEnrollmentData": A_KEEPENROLLMENTDATA,
        "keepUserData": A_KEEPUSERDATA,
        "macOsUnlockCode": A_MACOSUNLOCKCODE
    }

logging.debug("BODY_PAYLOAD: %s", BODY_PAYLOAD)

response = {}

if EP_DEVICE_ID:
    # Check for token
    if GRAPH_DELEGATED_TOKEN != "" and GRAPH_DELEGATED_TOKEN is not None:
        user_header = {"Authorization": "Bearer " + GRAPH_DELEGATED_TOKEN}

        post_url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/" + EP_DEVICE_ID + "/wipe"
        logging.debug("POST URL: " + post_url)

        # encode payload
        data = parse.urlencode(BODY_PAYLOAD).encode("utf-8")

        try:
            wipe_request = request.Request(post_url, data, headers=user_header)
            wipe_response = request.urlopen(wipe_request, context=ssl_context)

            # Check if we were succesful
            if wipe_response.getcode() == 204:
                response["succeeded"] = True

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
        response["error"] = "GRAPH DELEGATED Bearer Token is empty. Check Intune ACTION Tab"
else:
    logging.debug("Check : Intune Device ID : null/empty")
    response["succeeded"] = False
    response["error"] = "Check : Intune Device ID : null/empty"
