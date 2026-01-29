'''MIT License

Copyright (c) 2020 Ryan Kelleher (Welltok)

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

import logging
import requests

logging.info("SentinelOne Test Script")

# General params
token = params.get("connect_sentinelone_api_token")
server = params.get("connect_sentinelone_server")
headers = {
    "Content-type": "application/json",
    "Authorization": "APIToken " + token
}
# Set response
response = {}

try:
    # Call resource
    resp = requests.get(f"{server}/web/api/v2.1/accounts?limit=1&countOnly=true", headers=headers)

    if resp.status_code == 200:
        logging.debug("Test: Succeeded")
        response["succeeded"] = True
        response["result_msg"] = f"Successfully connected to SentinelOne Server."
    else:
        logging.debug("Test: Failed")
        response["succeeded"] = False
        response["result_msg"] = "Could not connect to SentinelOne Server."
except Exception as e:
    logging.debug("Test: Failed. Exception when connecting to SentinelOne server: " + str(e))
    response["succeeded"] = False
    response["result_msg"] = "Could not connect to SentinelOne Server. " + str(e)