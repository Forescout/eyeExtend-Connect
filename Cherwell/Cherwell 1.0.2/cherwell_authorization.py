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

import json
import urllib.request

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.

# Token Server URL
token_url = params["connect_cherwell_token_url"]

# Token Header Information
url_content_type = params["connect_cherwell_content_type"]
url_accept_type = params["connect_cherwell_accept_type"]

# Token Response Information
http_response_field_type = params["connect_cherwell_response_field_type"]
http_response_keyword = params["connect_cherwell_response_keyword"]

# Account Information
account_grant_type = "password"
account_client_id = params["connect_cherwell_client_id"]
account_service_account = params["connect_cherwell_service_account"]
account_service_account_pass = params["connect_cherwell_service_account_password"]

# Setup the information to retrieve a token from Cherwell
header_info = {
    'Content-Type': http_response_field_type,
    'Accept': url_accept_type
}
payload = 'client_id=' + account_client_id + '&grant_type=' + account_grant_type + '&username=' + account_service_account + '&password=' + account_service_account_pass

payload_data = payload  # urllib.parse.urlencode(payload).encode()
response = {}
# Making an API call to get the token
# To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
# request = urllib.request.Request(token_url, headers=headers, data=payload_data)
# resp = urllib.request.urlopen(request, context=ssl_context)
try:
    request_response = urllib.request.Request(token_url, headers=header_info,
                                              data=bytes(payload_data, encoding="utf-8"))
    resp = urllib.request.urlopen(request_response, context=ssl_context)

    # Read the json responses
    request_response = json.loads(resp.read())

    # Extract the token
    bearer_token = request_response["access_token"]

    if resp.getcode() == 200:
        response["token"] = bearer_token
    else:
        response["token"] = ""
except Exception as e:
    response["succeeded"] = False
    response["result_msg"] = "Failed action. Response: {}".format(str(e))
