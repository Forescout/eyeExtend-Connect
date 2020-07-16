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

# Intune action properties.
intune_to_ct_props_map = {
    "id": "connect_intune_id",
    "deviceActionResults": "connect_intune_device_action_result"
}

response = {}
if "connect_authorization_token" in params and params.get("connect_authorization_token") != "":
    access_token = params.get("connect_authorization_token")
    user_header = {"Authorization": "Bearer " + access_token}
    device_id = params.get("connect_intune_id")
    if device_id is not None:
        post_url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/" + device_id + "/wipe"
        logging.debug("POST URL: " + post_url)
        values = {}
        data = urllib.parse.urlencode(values).encode("utf-8")
        endpoint = dict()

        try:
            wipe_request = request.Request(post_url, data, headers=user_header)
            wipe_response = request.urlopen(wipe_request, context=ssl_context)
            wipe_response_json = json.loads(wipe_response.read())

            if "deviceActionResults" not in wipe_response_json:
                response["succeeded"] = True
            else:
                deviceActionResults = wipe_response_json["deviceActionResults"]
                endpoint[intune_to_ct_props_map["deviceActionResults"]] = deviceActionResults
                endpoint[intune_to_ct_props_map["id"]] = device_id
                response["response_message"] = endpoint
                response["succeeded"] = True

            logging.debug("Parsed device: " + json.dumps(response))
        except HTTPError as e:
            response["succeeded"] = False
            response["error"] = "Could not connect to Intune. Response code: {}".format(e.code)
        except URLError as e:
            response["succeeded"] = False
            response["error"] = "Could not connect to Intune. {}".format(e.reason)
        except Exception as e:
            response["succeeded"] = False
            response["error"] = "Could not connect to Intune. {}".format(str(e))
    else:
        response["succeeded"] = False
        response["error"] = "No Intune device ID associated with this endpoint"
else:
    response["succeeded"] = False
    response["error"] = "Authroization token is empty."


