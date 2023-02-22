# TEST: Test connection for Cisco DNA Center
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

ciscodna_func.debug('Starting Cisco DNA Center Test Script')

URL = params.get('connect_ciscodna_url') + ":" + params.get("connect_ciscodna_port")
cisco_username = params.get('connect_ciscodna_username')
cisco_password = params.get('connect_ciscodna_password')
encodedData = b64encode(bytes(cisco_username + ':' + cisco_password, "utf-8")).decode("ascii")

# Login and get Cisco DNA Center token
ciscodna_func.debug('\n=====  Getting SessionID  =====')
(code, token) = ciscodna_func.ciscodna_login(URL, encodedData, ssl_context)
ciscodna_func.debug("Session ID Returned: {}".format(token))

# Get Version from Cisco DNA Center to verify connection
ciscodna_func.debug("\n=====  Test Getting count of VPN Gateways  =====")
req_url = URL + "/dna/intent/api/v1/dnac-release"
(code, resp) = ciscodna_func.ciscodna_get_data(req_url, token, ssl_context)
version = resp.get("response")["displayVersion"]

if code == 200:
    response['succeeded'] = True
    response['result_msg'] = 'Successfully connected to Cisco DNA Center. Software Version: ' + str(version)
else:
    response['succeeded'] = False
    response['result_msg'] = 'Could NOT connect to Cisco DNA Center...'

ciscodna_func.debug('Ending Cisco DNA Center Test Script')
