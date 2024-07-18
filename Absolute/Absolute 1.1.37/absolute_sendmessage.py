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
import html
from connectproxyserver import ConnectProxyServer, ProxyProtocol

SCRIPT = 'Absolute Send Message'
logging.debug('{} - Start of Script'.format(SCRIPT))

send_message = absolute_library.send_message
VALIDATE_URI = absolute_library.VALIDATE_URI
DEVICE_UID = absolute_library.DEVICE_UID
UNKNOWN = absolute_library.UNKNOWN
notification_emails = None

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
try:
    device_uid = params['connect_absolute_device_uid']
except:
    device_uid = UNKNOWN
try:
    message = params['connect_absolute_message']
    logging.debug('{} - Message: {}'.format(SCRIPT, message))
except:
    message = None

logging.debug('{} - Configuration Loaded'.format(SCRIPT))

# if Proxy Aware create 'opener'; if unable to create set to 'None' and try without
opener = None
if is_proxy_enabled == 'true':
    logging.debug('{} - Proxy Enabled: {} - Getting Opener'.format(SCRIPT, is_proxy_enabled))
    try:
        proxyserver = ConnectProxyServer(params)
        opener = proxyserver.get_urllib_request_https_opener(ProxyProtocol.all, ssl_context)
        logging.debug('{} - Via Proxy'.format(SCRIPT))
    except Exception as e:
        logging.debug('{} - Via Proxy - Error Getting Opener: {}'.format(SCRIPT, e))

if opener is None:
    logging.debug('{} - No Proxy'.format(SCRIPT))

response = {}
response['succeeded'] = False
# if unable to lookup device UID return error; otherwise perform action
if device_uid == UNKNOWN:
    logging.debug('{} - Unable to get device UID from params for mac: {}'.format(SCRIPT, mac))
    response['troubleshooting'] = 'Unable to get device UID from parmas for mac: {}'.format(mac)
elif message is None:
    logging.debug('{} - No message provided'.format(SCRIPT))
    response['troubleshooting'] = 'No message provided'
else:
    message = "<p>{}</p>".format(html.escape(message).replace('\n', '<br>'))
    logging.debug('{} - Device UID: {} - Message: {}'.format(SCRIPT, device_uid, message))
    data, metadata, error = send_message(token, secret, url, device_uid, message, opener=opener, ssl_context=ssl_context) 
    if error is None:
        response['succeeded'] = True
    else:
        response['troubleshooting'] = error
logging.debug('{} - End of Script'.format(SCRIPT))







