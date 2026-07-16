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

# Set response
response = {}

# Check if server URL ends with /login
if server and server.endswith("/login"):
    logging.debug("Test: Failed - Server URL should not end with /login")
    response["succeeded"] = False
    response["result_msg"] = "Server URL should not include /login. Please use the base URL (e.g., https://usea1-012.sentinelone.net)"
else:
    headers = {
        "Content-type": "application/json",
        "Authorization": "ApiToken " + token
    }

    try:
        # Call resource
        resp = requests.get(f"{server}/web/api/v2.1/accounts?limit=1&countOnly=true", headers=headers)

        if resp.status_code == 200:
            # Verify that the response is valid JSON with expected structure
            try:
                resp_json = resp.json()
                # SentinelOne API responses typically have a 'data' field or pagination info
                if isinstance(resp_json, dict) and ('data' in resp_json or 'pagination' in resp_json):
                    logging.debug("Test: Succeeded")
                    response["succeeded"] = True
                    response["result_msg"] = f"Successfully connected to SentinelOne Server."
                else:
                    logging.debug(f"Test: Failed - Unexpected JSON structure: {resp_json}")
                    response["succeeded"] = False
                    response["result_msg"] = "Connected but received unexpected response. Verify API token is correct."
            except ValueError as json_error:
                # Response is not JSON (likely HTML from login page)
                logging.debug(f"Test: Failed - Response is not JSON: {str(json_error)}")
                response["succeeded"] = False
                response["result_msg"] = "Connected but received HTML instead of JSON. Check API token."
        else:
            logging.debug(f"Test: Failed - Status code: {resp.status_code}")
            response["succeeded"] = False
            response["result_msg"] = f"Could not connect to SentinelOne Server. Status code: {resp.status_code}"
    except Exception as e:
        logging.debug("Test: Failed. Exception when connecting to SentinelOne server: " + str(e))
        response["succeeded"] = False
        response["result_msg"] = "Could not connect to SentinelOne Server. " + str(e)