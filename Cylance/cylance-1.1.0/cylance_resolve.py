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


logging.debug('===>Starting Cylance Resolve Script')
# Mapping between Cylance API response fields to CounterACT properties
cylance_to_ct_props_map = {
    "state": "connect_cylance_state",
    "last_logged_in_user": "connect_cylance_last_logged_in_user",
    "mac_addresses": "connect_cylance_mac_addresses",
    "is_safe": "connect_cylance_is_safe",
    "id": "connect_cylance_id",
    "agent_version": "connect_cylance_agent_version",
    "host_name": "connect_cylance_host_name",
    "os_version": "connect_cylance_os_version",
    "update_available": "connect_cylance_update_available",
    "policy": "connect_cylance_policy",
    "ip_addresses": "connect_cylance_ip_addresses",
    "date_offline": "connect_cylance_date_offline"
}

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
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
        jwt_token = json.loads(resp.read())['access_token']  # access_token to be passed to GET request
        logging.debug('===>Cylance Resolve Script - via proxy - JWT')
    else:
        # Making an API call to get the JWT token
        request = urllib.request.Request(url + "/auth/v2/token", headers=headers,
                                         data=bytes(json.dumps(payload), encoding="utf-8"))

        # To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
        resp = urllib.request.urlopen(request, context=ssl_context)

        jwt_token = json.loads(resp.read())['access_token']  # access_token to be passed to GET request
        logging.debug('===>Cylance Resolve Script - No proxy - JWT')

# For properties and actions defined in the 'property.conf' file, CounterACT properties can be
# added as dependencies. These values will be found in the params dictionary if CounterACT was
# able to resolve the properties. If not, they will not be found in the params dictionary.
if "mac" in params:
    mac = '-'.join(params["mac"][i:i+2] for i in range(0,12,2))
    GETMAC_URL = url + "/devices/v2/macaddress/" + mac
    device_headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + str(jwt_token)}

    # Proxy Aware
    if is_proxy_enabled:

        proxyserver = ConnectProxyServer(params)
        opener = proxyserver.get_urllib_request_https_opener(ProxyProtocol.all, ssl_context)
        request = urllib.request.Request(GETMAC_URL, headers=device_headers)
        r = opener.open(request)
        request_response = json.loads(r.read())
        logging.debug('===>Cylance Resolve Script - via proxy - MAC Data')
    else:
        # Get MAC data
        request = urllib.request.Request(GETMAC_URL, headers=device_headers)
        r = urllib.request.urlopen(request, context=ssl_context)
        request_response = json.loads(r.read())
        logging.debug('===>Cylance Resolve Script - No proxy - MAC Data')

    # All responses from scripts must contain the JSON object 'response'. Host property resolve scripts will need to
    # populate a 'properties' JSON object within the JSON object 'response'. The 'properties' object will be a key,
    # value mapping between the CounterACT property name and the value of the property.
    response = {}
    properties = {}
    if request_response:
        properties["connect_cylance_agent_installed"] = True
        return_values = request_response[0]
        for key, value in return_values.items():
            if key in cylance_to_ct_props_map:
                if key != 'date_offline':
                    properties[cylance_to_ct_props_map[key]] = value
                elif value is not None:
                    date_time_obj = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
                    properties[cylance_to_ct_props_map[key]] = math.floor(date_time_obj.timestamp())
    else:
        properties["connect_cylance_agent_installed"] = False
    response["properties"] = properties
else:
    response = {}
    response["error"] = "No mac address to query the endpoint for."

logging.debug('===>End of Cylance Resolve Script')
