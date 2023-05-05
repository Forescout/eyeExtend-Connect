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

import jwt  # PyJWT version 1.6.1 as of the time of authoring
import uuid
import json
import urllib.request
from datetime import datetime, timedelta
from connectproxyserver import ConnectProxyServer,ProxyProtocol
import logging


logging.debug('===>Starting Cylance Authorisation')

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params["connect_cylance_url"]  # Server URL
tenant = params["connect_cylance_tenant_id"]  # Tenant ID
app = params["connect_cylance_application_id"]  # Application ID
secret = params["connect_cylance_application_secret"]  # Application Secret
is_proxy_enabled = params["connect_proxy_enable"]  # Proxy enable or not
# ***** START - AUTH API CONFIGURATION ***** #
timeout = 1800  # 30 minutes from now
now = datetime.utcnow()
timeout_datetime = now + timedelta(seconds=timeout)
epoch_time = int((now - datetime(1970, 1, 1)).total_seconds())
epoch_timeout = int((timeout_datetime - datetime(1970, 1, 1)).total_seconds())
jti_val = str(uuid.uuid4())
claims = {
    "exp": epoch_timeout,
    "iat": epoch_time,
    "iss": "http://cylance.com",
    "sub": app,
    "tid": tenant,
    "jti": jti_val,
}

encoded = jwt.encode(claims, secret, algorithm='HS256')
payload = {"auth_token": encoded.decode("utf-8")}
headers = {"Content-Type": "application/json; charset=utf-8"}

# Proxy Aware
if is_proxy_enabled:
    proxyserver = ConnectProxyServer(params)
    opener = proxyserver.get_urllib_request_https_opener(ProxyProtocol.all, ssl_context)
    request = urllib.request.Request(url + "/auth/v2/token", headers=headers,
                                     data=bytes(json.dumps(payload), encoding="utf-8"))
    resp = opener.open(request)
    jwt_token = json.loads(resp.read())['access_token']
    logging.debug('===>Starting Cylance Authorization - via Proxy')
else:
    # Making an API call to get the JWT token
    request = urllib.request.Request(url + "/auth/v2/token", headers=headers,
                                     data=bytes(json.dumps(payload), encoding="utf-8"))

    # To use the server validation feature, use the keyword 'ssl_context' in the http request
    resp = urllib.request.urlopen(request, context=ssl_context)
    jwt_token = json.loads(resp.read())['access_token']  # access_token to be passed to GET request
    logging.debug('===>Starting Cylance Authorisation - No proxy')


response = {}
if resp.getcode() == 200:
    response["token"] = jwt_token
else:
    response["token"] = ""
logging.debug('===>End of Script Cylance Authorization -')
