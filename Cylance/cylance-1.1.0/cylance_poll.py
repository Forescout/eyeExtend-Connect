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
import math
from datetime import datetime, timedelta
import urllib.request
import json
from connectproxyserver import ConnectProxyServer,ProxyProtocol
import logging


logging.debug('===>Starting Cylance Poll Script')
# Mapping between Cylance API response fields to CounterACT properties
cylance_to_ct_props_map = {
    "state": "connect_cylance_state",
    "mac_addresses": "connect_cylance_mac_addresses",
    "id": "connect_cylance_id",
    "agent_version": "connect_cylance_agent_version",
    "policy": "connect_cylance_policy",
    "ip_addresses": "connect_cylance_ip_addresses",
    "date_offline": "connect_cylance_date_offline"
}

# CONFIGURATION
url = params["connect_cylance_url"]  # Server URL
tenant = params["connect_cylance_tenant_id"]  # Tenant ID
app = params["connect_cylance_application_id"]  # Application ID
secret = params["connect_cylance_application_secret"]  # Application Secret
jwt_token = "" # JWT token prefetched
is_proxy_enabled = params["connect_proxy_enable"]  # Proxy enable or not


if "connect_authorization_token" in params:
    jwt_token = params["connect_authorization_token"] # use JWT token prefetched
else:
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
        logging.debug('===>Cylance Poll Script - via Proxy JWT')

    else:
        # Making an API call to get the JWT token
        request = urllib.request.Request(url + "/auth/v2/token", headers=headers,
                                         data=bytes(json.dumps(payload), encoding="utf-8"))

        # To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
        resp = urllib.request.urlopen(request, context=ssl_context)

        jwt_token = json.loads(resp.read())['access_token']  # access_token to be passed to GET request
        # ***** END - AUTH API CONFIGURATION ***** #
        logging.debug('===>Cylance Poll Script - No proxy - JWT Token')


# ***** PART 2 - QUERY FOR DEVICES  ***** #
GETMAC_URL = url + "/devices/v2/"
device_headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + str(jwt_token)}

# Proxy Aware
if is_proxy_enabled:
    proxyserver = ConnectProxyServer(params)
    opener = proxyserver.get_urllib_request_https_opener(ProxyProtocol.all, ssl_context)
    request = urllib.request.Request(url + "/auth/v2/token", headers=headers,
                                     data=bytes(json.dumps(payload), encoding="utf-8"))

    r = opener.open(request)
    request_response = json.loads(r.read())
    logging.debug('===>Cylance Poll Script - via Proxy - MAC Data')
else:
    # Get MAC data
    request = urllib.request.Request(GETMAC_URL, headers=device_headers)
    r = urllib.request.urlopen(request, context=ssl_context)
    request_response = json.loads(r.read())
    logging.debug('===>Cylance Poll Script - No Proxy - MAC Date')

# For polling, the response dictionary must contain a list called "endpoints", which will contain new endpoint
# information. Each endpoint must have a field named either "mac" or "ip". The endpoint object/dictionary may also
# have a "properties" field, which contains property information in the format
endpoints = []
for endpoint_data in request_response["page_items"]:
    endpoint = {}
    mac_with_dash = endpoint_data["mac_addresses"][0]
    mac = "".join(mac_with_dash.split("-"))
    endpoint["mac"] = mac
    properties = {}
    properties["connect_cylance_agent_installed"] = True
    for key, value in endpoint_data.items():
        if key in cylance_to_ct_props_map and key is not "mac_addresses":
            if key != 'date_offline':
                properties[cylance_to_ct_props_map[key]] = value
            elif value is not None:
                date_time_obj = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
                properties[cylance_to_ct_props_map[key]] = math.floor(date_time_obj.timestamp())
    endpoint["properties"] = properties
    endpoints.append(endpoint)
response = {}
response["endpoints"] = endpoints

logging.debug('===>End of Cylance Poll Script')
