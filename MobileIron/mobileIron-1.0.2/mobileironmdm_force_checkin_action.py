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

# construct 'action' response to CounterACT
response = {}

if params.get("connect_mobileironmdm_device_uid"):
    device_mdm_id = params.get("connect_mobileironmdm_device_uid")

    action_url = MI_PROTOCOL + "://" + MI_SERVER_ADDRESS + "/msa/v1/cps/device/forceCheckin"

    logging.debug("MI Action URL " + action_url)

    auth_string = "{}:{}".format(MI_SERVER_USERNAME, MI_SERVER_PASSWORD)
    base64string = base64.b64encode(auth_string.encode('utf-8'))
    header_auth_string = "".join(chr(x) for x in base64string)
    # logging.debug("Auth Basic " + header_auth_string)

    payload = "{ \"identifiers\": [\"" + device_mdm_id + "\"] }"
    logging.debug("Data-raw: " + payload)
    data = payload.encode("utf-8")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + header_auth_string
    }

    try:
        logging.debug("Starting Force check-in action...")

        action_response = requests.request("POST", action_url, headers=headers, data=payload, verify=ssl_verify)
        logging.debug("MI Force check-in response: " + str(action_response.text.encode("utf-8")))

        force_check_in_response = action_response.json()
        result = force_check_in_response["result"]

        if (action_response.status_code == 200) and (result != 0):
            response["succeeded"] = True
        else:
            response["succeeded"] = False
            response["error"] = "Force Check-In Action Failed for Device ID= {}".format(device_mdm_id)

        logging.debug("Force check-in action completed")

    except HTTPError as e:
        response["succeeded"] = False
        response["error"] = "Device Force Check-in failed. HTTP Response code: {}".format(e.code)
    except Exception as e:
        response["succeeded"] = False
        response["error"] = "Device Force Check-in failed. {}".format(str(e))
else:
    response["succeeded"] = False
    response["error"] = "Device MDM identifier field is empty."
