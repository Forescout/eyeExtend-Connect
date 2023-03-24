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
import json
import logging

import requests
from requests.exceptions import HTTPError

MI_PROTOCOL = "https"
MI_SERVER_USERNAME = params["connect_mobileironmdm_user"]
MI_SERVER_PASSWORD = params["connect_mobileironmdm_password"]
MI_SERVER_ADDRESS = params["connect_mobileironmdm_server_url"]
MI_DEVICE_MAC_ADDRESS = params.get("connect_mobileironmdm_testmac")

test_url = MI_PROTOCOL + "://" + MI_SERVER_ADDRESS + "/msa/v1/cps/device/mac"

logging.debug("MI Test URL " + test_url)

auth_string = "{}:{}".format(MI_SERVER_USERNAME, MI_SERVER_PASSWORD)
base64string = base64.b64encode(auth_string.encode('utf-8'))
header_auth_string = "".join(chr(x) for x in base64string)
# logging.debug("Auth Basic " + header_auth_string)

payload = "{ \"identifiers\": [\"\"] }"
if MI_DEVICE_MAC_ADDRESS:
    payload = "{ \"identifiers\": [\"" + MI_DEVICE_MAC_ADDRESS + "\"] }"

logging.debug("Data-raw: " + payload)
data = payload.encode("utf-8")

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic ' + header_auth_string
}

response = {}

try:
    test_response = requests.request("POST", test_url, headers=headers, data=payload, verify=ssl_verify)
    logging.debug("MI Test response: " + str(test_response.text.encode("utf-8")))

    test_response = test_response.text

    logging.debug("MI Test response: " + test_response)
    test_response_json = json.loads(test_response)

    if len(test_response_json) > 0:
        test_response_json = test_response_json[0]
        test_response_json["macAddress"] = test_response_json["macAddress"].replace(":", "")
        test_response_str = ",\n  ".join(
            {"\"" + str(p) + "\"" + ": " + "\"" + str(v) + "\"" for p, v in test_response_json.items()})
        test_response_json = "\n{\n  " + test_response_str + "\n}"
    elif not test_response_json:  # check if list is empty
        # MAC address not provided, but connection to server could be established
        test_response_json = \
            "\nTest device MAC address Not Found.\nSuccessfully established connection to the MobileIron Server."

    response["succeeded"] = True
    response["result_msg"] = str(test_response_json)

except HTTPError as e:
    response["succeeded"] = False
    response["error"] = "Could not connect to MobileIron. HTTP Response code: {}".format(e.code)
except Exception as e:
    response["succeeded"] = False
    response["error"] = "{}".format(str(e))
