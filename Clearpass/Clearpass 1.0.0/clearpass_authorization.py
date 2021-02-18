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
Retrieve the Bearer token from ClearPass
'''

from urllib import request, parse
from urllib.request import HTTPError, URLError
import json
import logging

# Panel Vars
P_SERVER_ADDRESS = params.get("connect_clearpass_server_address")
P_CLIENT_ID = params.get("connect_clearpass_client_id")
P_SECRET = params.get("connect_clearpass_secret")

if P_CLIENT_ID:
    logging.debug("Client ID (First 5): %s", P_CLIENT_ID[0:5])

# Build AUTH payload
AUTH_PAYLOAD = {"grant_type": "client_credentials",
                "client_id": P_CLIENT_ID,
                "client_secret": P_SECRET}

# AUTH endcoded payload
AUTH_PAYLOAD_ENCODE = parse.urlencode(AUTH_PAYLOAD).encode()

# AUTH URL
AUTH_URL = f"https://{P_SERVER_ADDRESS}/api/oauth"

response = {}
response["token"] = ""

# Request Token
try:
    # POST AUTH
    logging.info('Requesting ClearPass Bearer Token')
    auth_req = request.Request(
        AUTH_URL, data=AUTH_PAYLOAD_ENCODE, method="POST")
    auth_resp = request.urlopen(auth_req, context=ssl_context)
    auth_json_resp = json.loads(auth_resp.read())
    auth_access_token = auth_json_resp.get('access_token')

    if auth_access_token:
        logging.info('Retrieved Bearer Token')
        logging.debug("Bearer Token (First 10): %s", auth_access_token[0:10])
        response["succeeded"] = True
        response["token"] = auth_access_token
    else:
        response["succeeded"] = False
        response["error"] = "Exception Error could not obtain token"
        logging.info("Exception Error could not obtain token")

except HTTPError as e:
    response["succeeded"] = False
    response["error"] = "Could not connect to ClearPass service. Response code: {}".format(
        e.code)
    logging.debug(
        'HTTP Error not connect to ClearPass service : %s', format(e.code))

except URLError as e:
    response["succeeded"] = False
    response["error"] = "Could not connect to ClearPass service. {}".format(
        e.reason)
    logging.debug(
        'URL Error not connect to ClearPass service : %s', format(e.reason))

except Exception as e:
    response["succeeded"] = False
    response["error"] = "Could not connect to ClearPass service. {}".format(
        str(e))
    logging.debug(
        'Exception Error not connect to ClearPass service : %s', format(str(e)))
