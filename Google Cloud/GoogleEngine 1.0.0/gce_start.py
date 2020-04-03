'''
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
'''

''' Google Compute Engine action START '''
import json
import urllib.request
import urllib.parse
import urllib
# import ssl
# import jwt
# import time
# from time import gmtime, strftime, sleep
# from datetime import datetime, timedelta
# import base64
# import random

# GET Params Configuration
ENGINE_ID = params["connect_googleengine_id"]
ENGINE_PROJECTID = params["connect_googleengine_projectid"]
ENGINE_ZONE = params["connect_googleengine_zone"]

BEARER_TOKEN = params.get("connect_authorization_token")

# POST URL Example
# https://www.googleapis.com/compute/v1/projects/{PROJECTID}/zones/{ZONE}/instances/{ENGINE_ID}/start
POST_URL = f"https://www.googleapis.com/compute/v1/projects/{ENGINE_PROJECTID}/zones/{ENGINE_ZONE}/instances/{ENGINE_ID}/start"

logging.info("Checking Token")

if BEARER_TOKEN is None or BEARER_TOKEN is "":
    response = {}

    logging.info("No Valid Bearer Token")

    response["succeeded"] = False
    response["troubleshooting"] = {}
else:
    # Header
    header = {"Authorization": "Bearer " + BEARER_TOKEN}

    response = {}

    logging.info(f"Request Start GCE {ENGINE_ID}")
    logging.info(f"URL {POST_URL}")

    # Build POST request
    action_request = urllib.request.Request(POST_URL, headers=header, method="POST")

    try:
        action_response = urllib.request.urlopen(action_request, context=ssl_context)

        if action_response.getcode() == 200:
            json_post_response = json.loads(action_response.read())
            logging.info(f"Start Request ID {json_post_response['id']}")
            logging.info(f"Start Response Code {action_response.getcode()}")

            response["succeeded"] = True

    except urllib.error.HTTPError as error:
        logging.debug(f"HTTPError code : {error.read()}")

        response["succeeded"] = False
        response["error"] = f"Error Could Not Start Engine. {error.reason}"
