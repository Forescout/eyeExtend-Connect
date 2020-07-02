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

# Test script for CounterACT
import urllib.request,urllib.error
import base64
import logging

logging.debug('===>Starting Cisco Prime Test Script')

response = {}
resp = None

base_url = params.get('connect_ciscoprime_url')
username = params.get('connect_ciscoprime_username')
password = params.get('connect_ciscoprime_password')
ctx = ssl_context

# Defining Headers and Adding Authentication header-----
headers = {
    'Content-Type': "application/json",
    'Accept' : "application/json",
    'charset': 'utf-8',
    'User-Agent': "FSCT/1.16.2020",
    }
credentials = ('%s:%s' % (username, password))
encoded_credentials = base64.b64encode(credentials.encode('ascii'))
headers['Authorization'] = 'Basic %s' % encoded_credentials.decode("ascii")

#-------------------------End of Headers

try:
    request = urllib.request.Request(base_url + "/webacs/api/v4/data/Devices", headers=headers)
    resp = urllib.request.urlopen(request,context=ctx)
    if resp.getcode() == 200:
        response["succeeded"] = True
        response["result_msg"] = "Successfully connected to  Cisco Prime Server."
    else:
        response["succeeded"] = False
        response["result_msg"] = "Could not connect to Cisco Prime server"

except Exception as e:
    response["succeeded"] = False
    error = str(e)
    response["result_msg"] = "Could not connect to Cisco Prime server"
    logging.debug("Cannot connect. Error : " + error)

logging.debug('===>End of Cisco Prime Test Script')
