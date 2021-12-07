"""
Copyright © 2021 Forescout Technologies, Inc.
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

import logging

logging.debug('===>Starting Cisco FMC authorisation Script')

# Definining Variables
response = {}

server = params['connect_ciscofmc_url']
username = params['connect_ciscofmc_username']
password = params['connect_ciscofmc_password']
Access_Token = params["connect_authorization_token"]
ctx = ssl_verify

try:
    fmc = ciscofmc.CiscoFMC(server, username, password, ctx)
    fmc.get_auth_token()

    if fmc.access_token != '':
        response["token"] = fmc.access_token
        logging.debug(f'===>Cisco FMC Authorisation. Access token:{fmc.access_token}')
    else:
        response["token"] = ''
        response['token'] = fmc.access_token
        response['error'] = f'Could not get the Access Token. Verify the Settings'
        logging.debug('===>Cisco FMC Authorisation Failed')

except Exception as e:
    logging.debug(f'===>Cisco FMC Authorisation Failed : {e}')

logging.debug('===>End Cisco FMC authorisation Script')
