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

response = {}
if "connect_authorization_token" in params and params.get("connect_authorization_token") != "":
    access_token = params.get("connect_authorization_token")
    user_header = {"Authorization": "Bearer " + access_token}
    device_id = params.get("connect_intune_id")
    if device_id is not None:
        post_url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/" + device_id + "/remoteLock"
        logging.debug("POST URL: " + post_url)
        values = {}
        data = urllib.parse.urlencode(values).encode("utf-8")

        try:
            remote_lock_request = request.Request(post_url, data, headers=user_header)
            remote_lock_response = request.urlopen(remote_lock_request, context=ssl_context)
            if remote_lock_response.getcode() == 204:
                response["succeeded"] = True
        except HTTPError as e:
            response["succeeded"] = False
            response["troubleshooting"] = "Failed remote lock action. Response code: {}".format(e.code)
        except URLError as e:
            response["succeeded"] = False
            response["troubleshooting"] = "Failed remote lock action. {}".format(e.reason)
        except Exception as e:
            response["succeeded"] = False
            response["troubleshooting"] = "Failed remote lock action. {}".format(str(e))
    else:
        response["succeeded"] = False
        response["error"] = "No Intune device ID associated with this endpoint"
else:
    response["succeeded"] = False
    response["error"] = "Authroization token is empty."

