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

# Get Managed Device ID
EP_DEVICE_ID = params.get("connect_intune_id")

# Need to convert tokens from STR to DICT
P_STR_TOKENS = params.get("connect_authorization_token", "{}")
DICT_TOKENS = json.loads(P_STR_TOKENS)

#
P_INTUNE_ENVIRONMENT = params.get("connect_intune_environment")
P_INTUNE_GRAPH_VERSION = params.get("connect_intune_graph_version")

#
UTILS_GRAPH_RESOURCE = intune_utils.INTUNE_ENVIRONMENT_RESOURCES[
    P_INTUNE_ENVIRONMENT]['GRAPH_RESOURCE_ENV_URL']

# Get GRAPH token
GRAPH_DELEGATED_TOKEN = DICT_TOKENS.get("graph_delegated_token")

response = {}

if EP_DEVICE_ID:
    if GRAPH_DELEGATED_TOKEN:
        user_header = {"Authorization": "Bearer " + GRAPH_DELEGATED_TOKEN}

        post_url = f"{UTILS_GRAPH_RESOURCE}{P_INTUNE_GRAPH_VERSION}/deviceManagement/managedDevices/" + \
            EP_DEVICE_ID + "/syncDevice"

        logging.debug("POST URL: " + post_url)

        values = {}
        data = parse.urlencode(values).encode("utf-8")

        try:
            # Create proxy server
            proxy_server = intune_utils.ConnectProxyServer()
            proxy_server.set_init(params)
            opener = proxy_server.get_urllib_request_https_opener(
                intune_utils.ProxyProtocol.all, ssl_context)

            sync_request = request.Request(post_url, data, headers=user_header)
            sync_response = request.urlopen(sync_request)
            if sync_response.getcode() == 204:
                response["succeeded"] = True
        except HTTPError as e:
            response["succeeded"] = False
            response[
                "troubleshooting"] = f"HTTP Error : Failed remote lock action. Response code: {e.code}"
        except URLError as e:
            response["succeeded"] = False
            response["troubleshooting"] = f"URL Error : Failed remote lock action. {e.reason}"
        except Exception as e:
            logging.exception(e)
            response["succeeded"] = False
            response["troubleshooting"] = f"Exception : Failed remote lock action. {str(e)}"
        # else:
        #    response["succeeded"] = False
        #    response["error"] = "No Intune device ID associated with this endpoint"
    else:
        response["succeeded"] = False
        response["error"] = "GRAPH DELEGATED Bearer Token is empty. Check Intune ACTION Tab"
else:
    logging.debug("Check : Intune Device ID : null/empty")
    response["succeeded"] = False
    response["error"] = "Check : Intune Device ID : null/empty"
