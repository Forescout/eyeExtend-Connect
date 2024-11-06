"""

Copyright © 2024 Absolute Software Corporation.
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
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHE
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


from datetime import datetime, timedelta
import json
import math
import logging
import time
import urllib.request
from connectproxyserver import ConnectProxyServer, ProxyProtocol

# SCRIPT
SCRIPT = 'Absolute Poll'
logging.debug('{} - Start of Script'.format(SCRIPT))

get_devices = absolute_library.get_devices
get_properties = absolute_library.get_properties
fields = absolute_library.fields
VALIDATE_URI = absolute_library.VALIDATE_URI
DEVICE_UID = absolute_library.DEVICE_UID
LAST_CONNECTED_DATETIME_UTC = absolute_library.LAST_CONNECTED_DATETIME_UTC
MAX_PAGE_SIZE = absolute_library.MAX_PAGE_SIZE

# CONFIGURATION
url = params["connect_absolute_url"]  # Server URL
url = url + VALIDATE_URI
secret = params["connect_absolute_secret"]  # Application Secret
token = params["connect_absolute_token"]  # Application Token
is_proxy_enabled = str(params['connect_proxy_enable']).lower()

logging.debug('{} - Configuration Loaded'.format(SCRIPT))

# if Proxy Aware create 'opener'; if unable to create set to 'None' and try without
opener = None
if is_proxy_enabled == 'true':
    try:
        proxyserver = ConnectProxyServer(params)
        opener = proxyserver.get_urllib_request_https_opener(ProxyProtocol.all, ssl_context)
        logging.debug('{} - Via Proxy'.format(SCRIPT))
    except Exception as e:
        logging.debug('{} - Via Proxy - Error Getting Opener: {}'.format(SCRIPT, str(e)))
if opener is None:
    logging.debug('{} - No Proxy'.format(SCRIPT))

# For polling, the 'response' dictionary must contain a list called "endpoints", which will contain new endpoint
# information. Each endpoint must have a field named either "mac". The endpoint object/dictionary may also
# have a "properties" field, which contains property information

# Virtual enviro has license limit of 1K hosts and has other hosts based on simulated traffic, so setting max 250 to stay under limit
try:
    status, devices, error = get_devices(token, secret, url, fields, filters='agentStatus=A&sortBy=esn%3Aasc', page_size=MAX_PAGE_SIZE, opener=opener, ssl_context=ssl_context)
except Exception as e:
    error = 'Error getting devices: {}'.format(e)

response = {}
properties = None
if error is not None:
    response['error'] = error
    logging.debug('{} - {}'.format(SCRIPT, error.title()))
else:
    try:
        endpoints = []
        for i, device in enumerate(devices):
            # if we cannot get device UID and/or mac then not possible to discover, resolve, or perform actions on device
            try:
                device_uid = device[DEVICE_UID]
            except:
                continue
            # get properties and add endpoint only if one or more properties
            mac, properties, messages = get_properties(device, SCRIPT)
            if len(messages) > 0:
                for message in messages:
                    logging.debug('{} - Device UID: {} - {}'.format(SCRIPT, device_uid, message))
            n_properties = len(properties)
            if n_properties > 0:
                endpoint = {}
                endpoint['mac'] = mac
                endpoint['properties'] = properties
                endpoints.append(endpoint)
            else:
                logging.debug('{} - Device UID: {} - No Properties Found'.format(SCRIPT, device_uid))
        # set 'endpoints' key-value pair as required for poll script response
        response['endpoints'] = endpoints
        logging.debug('{} - Discovered Endpoints: {}'.format(SCRIPT, len(endpoints)))
    except Exception as e:
        logging.debug('{} - Error Getting Device Properties: {}'.format(SCRIPT, e))
        response['error'] = 'Error getting device properties: {}'.format(e)

logging.debug('{} - End of Script'.format(SCRIPT))
