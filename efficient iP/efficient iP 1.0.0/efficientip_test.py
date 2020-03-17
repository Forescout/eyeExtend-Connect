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
import json
import urllib.request
from base64 import b64encode

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params["connect_efficientip_url"] # Server URL
login = params["connect_efficientip_login"]  # login
password = params["connect_efficientip_password"]  # password
userAndPass = b64encode(bytes('%s:%s' % (login, password),'ascii')) # base64(Login and password) needed for Authorization

# Prepare API CALL
GET_URL = url + "/rest/dhcp_server_list"
device_headers = {"Authorization": "Basic " + userAndPass.decode('utf-8')}
request = urllib.request.Request(GET_URL, headers=device_headers)

# To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
r = urllib.request.urlopen(request, context=ssl_context)
response = {}

# Like the action response, the response object must have a "succeeded" field to denote success. It can also optionally have
# a "result_msg" field to display a custom test result message.
if r.getcode() == 200:
    response["succeeded"] = True
    response["result_msg"] = "Successfully connected."
else:
    response["succeeded"] = False
    response["result_msg"] = "Could not connect to Efficient IP"
