# TEST: Test connection for Citrix ADM (VPN)
# Connect Plugin V1.6

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

from base64 import b64encode
response = {}

citrix_func.debug('Starting Citrix ADM Test Script')

URL = params.get('connect_citrix_ADM') + ":" + params.get("connect_citrix_ADM_port")
citrix_username = params.get('connect_citrix_username')
citrix_password = params.get('connect_citrix_password')

# Login and get ADM session ID
citrix_func.debug('\n=====  Test Getting SessionID  =====')
(code, sessid, session) = citrix_func.citrix_login(URL, citrix_username, citrix_password, ssl_context)
citrix_func.debug("Session ID Returned: {}".format(sessid))

# Get VPN GWs from Citrix ADM to verify connection
citrix_func.debug("\n=====  Test Getting count of VPN Gateways  =====")
req_url = URL + "/nitro/v2/stat/ns_vpnvserver?count=yes"
(code, resp) = citrix_func.citrix_get_data(req_url, sessid, session, ssl_context, "")
vpnservers = resp.get("ns_vpnvserver")
vpnserver = vpnservers[0]
gw_count = vpnserver["__count"]

if gw_count:
    response['succeeded'] = True
    response['result_msg'] = 'Successfully connected to Citrix ADM. Number of VPN Gateways detected: ' + str(gw_count)
else:
    response['succeeded'] = False
    response['result_msg'] = 'Could NOT connect to Citrix ADM...'

citrix_func.debug('Ending Citrix ADM Test Script')
