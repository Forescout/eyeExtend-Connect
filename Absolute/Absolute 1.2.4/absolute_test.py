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

import logging
from connectproxyserver import ConnectProxyServer,ProxyProtocol

#SCRIPT NAME
SCRIPT = 'Absolute Test'
logging.debug('{} - Loading From Library'.format(SCRIPT))
error = None


try:
    AGENT_STATUS = absolute_library.AGENT_STATUS
    DEVICE_UID = absolute_library.DEVICE_UID
    IPV4_ADDRESS = absolute_library.IPV4_ADDRESS
    LOCAL_IP = absolute_library.LOCAL_IP
    MAC = absolute_library.MAC
    PUBLIC_IP = absolute_library.PUBLIC_IP
    VALIDATE_URI = absolute_library.VALIDATE_URI
    NO_DATA = absolute_library.NO_DATA
    UNKNOWN = absolute_library.UNKNOWN
    get_devices_page = absolute_library.get_devices_page
    get_properties = absolute_library.get_properties
    fields = absolute_library.fields
except Exception as e:
    error = 'Error Loading From Library: {}'.format(e)
    logging.debug('{} - {}'.format(SCRIPT, error))
    
logging.debug('{} - Loading Configuration'.format(SCRIPT))
# CONFIGURATION

url = params["connect_absolute_url"]  # Server URL
url = url + VALIDATE_URI
secret = params["connect_absolute_secret"]  # Application Secret
token = params["connect_absolute_token"]  # Application Token
is_proxy_enabled = str(params["connect_proxy_enable"]).lower()  # Proxy enable or not

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

devices = []
response = {}
response['succeeded'] = False
if error is None:
    logging.debug('{} - Getting Devices'.format(SCRIPT))
    status, devices, next_page, error = get_devices_page(token, secret, url, fields, page_size=10, opener=opener, ssl_context=ssl_context)
    logging.debug('{} - Status: {}, error: {}'.format(SCRIPT, status, error))

if error is None:
    logging.debug('{} - Devices: {}'.format(SCRIPT, len(devices)))
    msg = ''
    for device in devices:
        mac, properties, messages = get_properties(device)
        try:
            device_uid = device[DEVICE_UID]
            agent_status = device[AGENT_STATUS]
            mac, properties, messages = get_properties(device)
            msg += 'Device UID: {} - Agent Status: {} - Mac: {}\n'.format(device_uid, agent_status, mac)
        except Exception as e:
            msg += 'Error: {}\n'.format(e)
    response['succeeded'] = True
    response['result_msg'] = msg
    logging.debug('{} - SUCCESS'.format(SCRIPT))
else:
    response['error'] = error
    logging.debug('{} - {}'.format(SCRIPT, error))
logging.debug('{} - End of Script'.format(SCRIPT))
# if error is None:
#     #print(response['result_msg'])