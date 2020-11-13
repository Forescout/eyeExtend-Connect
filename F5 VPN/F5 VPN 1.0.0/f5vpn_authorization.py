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
'''
F5 Authorization Token
Keep-Alive used by Connect
'''
import logging
import json
import urllib

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
# CONFIGURATION from UI Panels
P_F5_HOST = params.get('connect_f5vpn_host')
P_USERNAME = params.get('connect_f5vpn_username')
P_PASSWORD = params.get('connect_f5vpn_password')

# BODY TO GET TOKEN
BODY = {'username': P_USERNAME,
        'password': P_PASSWORD,
        'loginProviderName': 'tmos'
        }

# Login URL
F5_URL_AUTH = '/mgmt/shared/authn/login'
logging.info('Getting Token : %s%s', {P_F5_HOST}, {F5_URL_AUTH})

REQUEST = urllib.request.Request(P_F5_HOST+F5_URL_AUTH)
REQUEST.add_header('Content-Type', 'application/json')

JSON_BODY = json.dumps(BODY)
JSON_BODY_BYTES = JSON_BODY.encode('utf8')

# Forescout response
response = {}

try:
    # ssl_context obtained from panel configuration.
    RESPONSE = urllib.request.urlopen(REQUEST, data=JSON_BODY_BYTES, context=ssl_context)

    if RESPONSE.getcode() == 200:
        RESPONSE_BODY = json.loads(RESPONSE.read())
        # Extract TOKEN from request
        TOKEN = RESPONSE_BODY['token']['token']
        logging.info('Obtained Token')
        # Update Forescout Authorization Token, used by other .py files
        response['token'] = TOKEN

except urllib.error.HTTPError as error:
    logging.info('Error : Did Not Obtain A Valid Token')
    response['token'] = ''
    response['error'] = f'Error Authorization Failed : {error.reason}'
