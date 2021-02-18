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

''' Test connection to ClearPass
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
if P_SERVER_ADDRESS:
    logging.debug("P_SERVER_ADDRESS : %s", P_SERVER_ADDRESS)

response = {}

if P_BEARER_TOKEN:

    # Build Request
    TEST_URL = f'https://{P_SERVER_ADDRESS}/api/cppm-version'
    # Header
    BEARER_HEADER = {"Authorization": "Bearer " + P_BEARER_TOKEN,
                     "Accept": "application/json"}

    logging.debug("TEST_URL : %s", TEST_URL)

    try:
        test_request = request.Request(TEST_URL, headers=BEARER_HEADER, method="GET")
        test_response = request.urlopen(test_request, context=ssl_context)
        test_response_json = json.loads(test_response.read())

        logging.debug("test_response_json : %s", test_response_json)
        response['succeeded'] = True
        response['result_msg'] = f'Successfully connected. \n{test_response_json}'

    except HTTPError as e:
        response["succeeded"] = False
        response["error"] = "HTTP Error : Could not connect to ClearPass. Response code: {}".format(e.code)

    except URLError as e:
        response["succeeded"] = False
        response["error"] = "URL Error : Could not connect to ClearPass. {}".format(e.reason)

    except Exception as e:
        response["succeeded"] = False
        response["error"] = "Exception : Could not connect to ClearPass. {}".format(str(e))

else:
    response["succeeded"] = False
    response["error"] = "Authorization token is empty."
