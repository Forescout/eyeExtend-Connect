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

import jwt  # PyJWT version 1.6.1 as of the time of authoring
import uuid
import json
import urllib.request
import time
from time import gmtime, strftime, sleep
from datetime import datetime, timedelta

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
iss_serviceaccount = params["connect_googlemdm_service_account"]

# Scope for the calls
scope = params["connect_googlemdm_device_context"]

# Token Server URL
url_aud = params["connect_googlemdm_token_url"] # Server URL

# Token Server URL
token_url = params["connect_googlemdm_token_url"] # Server URL

impersonate_sub = params["connect_googlemdm_impersonate_id"]

# Private key retrieved from google mdm
pkey = params["connect_googlemdm_private_key"]

# Private key ID from google MDM
pkeyid = params["connect_googlemdm_private_key_id"]

# ***** START - AUTH API CONFIGURATION ***** #
timeout = 1800  # 30 minutes from now
now = datetime.utcnow()
timeout_datetime = now + timedelta(seconds=timeout)
epoch_time = int((now - datetime(1970, 1, 1)).total_seconds())
epoch_timeout = int((timeout_datetime - datetime(1970, 1, 1)).total_seconds())
jti_val = str(uuid.uuid4())
payload = {
    "iss": iss_serviceaccount,
    "sub": impersonate_sub,
    "scope": scope,
    "aud": url_aud,
    "exp": epoch_timeout,
    "iat": epoch_time
}

# Encode the jwt so it can be used to retrive a token from Google MDM
additional_headers = {'alg': 'RS256', 'typ': 'JWT', 'kid': pkeyid}
signed_jwt = jwt.encode(payload, pkey, headers=additional_headers, algorithm='RS256')
jwt_token = signed_jwt.decode("utf-8")
headers = {"Content-Type": "application/json; charset=utf-8"}
token_payload = 'grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=' + jwt_token
token_data={
    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
    'assertion': jwt_token
}

# Making an API call to get the JWT token
# To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
request = urllib.request.Request(token_url, headers=headers, data=bytes(json.dumps(token_data), encoding="utf-8"))
resp = urllib.request.urlopen(request, context=ssl_context)

# Read the json responses
request_response = json.loads(resp.read())

# Extract the token
bearer_token = request_response["access_token"]
response = {}
if resp.getcode() == 200:
    response["token"] = bearer_token
else:
    response["token"] = ""