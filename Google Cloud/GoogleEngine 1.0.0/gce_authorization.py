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

''' Obtain bearer token from Google Cloud '''
import json
import urllib.request
import urllib.parse
import urllib
# import ssl
from datetime import datetime, timedelta
# import base64
import jwt
# import time
# from time import gmtime, strftime, sleep


# GET Params Configuration
AUD_URL = params["connect_googleengine_aud_url"]
CLIENT_EMAIL = params["connect_googleengine_client_email"]
SCOPE = params["connect_googleengine_claim_scope"]
PRIVATE_KEY = params["connect_googleengine_private_key"]

logging.info("Getting Bear Token")

# Build OAuth Claim
jwt_header = {'alg': 'RS256', 'typ': 'JWT'}

timeout = 3600  # 60 minutes from now
now = datetime.utcnow()
timeout_datetime = now + timedelta(seconds=timeout)
epoch_time = int((now - datetime(1970, 1, 1)).total_seconds())
epoch_timeout = int((timeout_datetime - datetime(1970, 1, 1)).total_seconds())
claim_set = {
    'iss': CLIENT_EMAIL,
    'scope': SCOPE,
    'aud': AUD_URL,
    'exp': epoch_timeout,
    'iat': epoch_time
}

# Build JWT
signature = jwt.encode(claim_set, PRIVATE_KEY,
                       algorithm='RS256', headers=jwt_header)
payloadx = {"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": signature}

# Request Bearer
request_bearer = urllib.request.Request(AUD_URL, data=bytes(
    urllib.parse.urlencode(payloadx), 'utf-8'))

response = {}

try:
    resp = urllib.request.urlopen(request_bearer, context=ssl_context)
    if resp.getcode() == 200:
        logging.info("Obtained Bearer Token")
        # Extract Bearer from request
        BEARER_TOKEN = json.loads(resp.read())['access_token']
        response["token"] = BEARER_TOKEN

except urllib.error.HTTPError as error:
    logging.info("No Valid Bearer Token")
    response["token"] = ""
    response["error"] = f"Error Authorization Failed : {error.reason}"
