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

import json
import logging
from connectproxyserver import ConnectProxyServer, ProxyProtocol
from datetime import datetime
import json
import math
import time

# SCRIPT NAME
SCRIPT = 'Absolute Resolve'
logging.debug('{} - Start of Script'.format(SCRIPT))

VALIDATE_URI = absolute_library.VALIDATE_URI
UNKNOWN = absolute_library.UNKNOWN
NOT_APPLICABLE = absolute_library.NOT_APPLICABLE
DEVICE_UID = absolute_library.DEVICE_UID
AGENT_STATUS = absolute_library.AGENT_STATUS
get_devices = absolute_library.get_devices
get_properties = absolute_library.get_properties
fields = absolute_library.fields

logging.debug('{} - Loading Configuration'.format(SCRIPT))

# CONFIGURATION
url = params["connect_absolute_url"]  # Server URL
url = url + VALIDATE_URI
secret = params["connect_absolute_secret"]  # Application Secret
token = params["connect_absolute_token"]  # Application Token
is_proxy_enabled = str(params["connect_proxy_enable"]).lower()  # Proxy enable or not

try:
    mac = params['mac']
except:
    mac = UNKNOWN
    logging.debug('{} - No Mac found'.format(SCRIPT))
try:
    device_uid = params['connect_absolute_device_uid']
except:
    device_uid = UNKNOWN
    logging.debug('{} - No DeviceUid found'.format(SCRIPT))

logging.debug('{} - Configuration Loaded'.format(SCRIPT))

# if Proxy Aware create 'opener'; if unable to create set to 'None' and try without
opener = None
if is_proxy_enabled == 'true':
    try:
        proxyserver = ConnectProxyServer(params)
        opener = proxyserver.get_urllib_request_https_opener(ProxyProtocol.all, ssl_context)
        logging.debug('{} - Via Proxy'.format(SCRIPT))
    except Exception as e:
        logging.debug('{} - Via Proxy - Error Getting Opener: {}'.format(SCRIPT, e))
if opener is None:
    logging.debug('{} - No Proxy'.format(SCRIPT))

response = {}
if device_uid != UNKNOWN and device_uid != NOT_APPLICABLE:
    filters = '='.join([DEVICE_UID, device_uid])
    filters += "&"
    filters += '='.join([AGENT_STATUS, "A"])
    logging.debug('{} - Filter: {}'.format(SCRIPT, filters))
    status, devices, next_page, error = get_devices(token, secret, url, fields, filters=filters, opener=opener,ssl_context=ssl_context)
    if error is not None:
        response['error'] = error
        logging.debug('{} - Status: {} - Device UID: {} - Error Getting Device: {}'.format(SCRIPT, status, device_uid, error))
    else:
        try:
            mac, properties, messages = get_properties(devices[0], SCRIPT)
            n_properties = len(properties)
            response['properties'] = properties
            logging.debug('{} - Device UID: {} - Mac: {} - Properties: {}'.format(SCRIPT, device_uid, mac, n_properties))
        except Exception as e:
            logging.debug('{} - Device UID: {} - Error Getting Properties: {}'.format(SCRIPT, device_uid, e))

logging.debug('{} - End of Script'.format(SCRIPT))
