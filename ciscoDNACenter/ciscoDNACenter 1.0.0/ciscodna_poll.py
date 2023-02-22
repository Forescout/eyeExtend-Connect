# POLL: Discover wireless sensors from Cisco DNA Center
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
import datetime
import logging
import time

begin_time = datetime.datetime.now()

endpoints = []
response = {}

ciscodna_func.debug('Starting Cisco DNA Center Poll Script')

URL = params.get('connect_ciscodna_url') + ":" + params.get("connect_ciscodna_port")
cisco_username = params.get('connect_ciscodna_username')
cisco_password = params.get('connect_ciscodna_password')
encodedData = b64encode(bytes(cisco_username + ':' + cisco_password, "utf-8")).decode("ascii")

# Login and get Cisco DNA Center token
ciscodna_func.debug('\n=====  Getting SessionID  =====')
(code, token) = ciscodna_func.ciscodna_login(URL, encodedData, ssl_context)
ciscodna_func.debug("Session ID Returned: {}".format(token))

# Get Cisco DNA Center Wireless Sensors
ciscodna_func.debug("\n=====  Getting Wireless Sensors  =====")
(code, sensors) = ciscodna_func.ciscodna_get_wireless_sensors(URL, token, ssl_context)
ciscodna_func.debug("Sensors Returned: {}".format(sensors))

num_endpoints = len(sensors)
ciscodna_func.debug("Total number of endpoints:" + str(num_endpoints))

response["endpoints"] = sensors
elapsed_time = (datetime.datetime.now() - begin_time)
ciscodna_func.debug('Ending Cisco DNA Center Poll Script, Polling Time: ' + str(elapsed_time))
