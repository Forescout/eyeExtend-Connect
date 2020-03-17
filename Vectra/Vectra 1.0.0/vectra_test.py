
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
import urllib.request

# Import Param
#All server configuration fields will be available in the 'params' dictionary.
URL = params["connect_vectra_url"] # Server URL
TOKEN = params["connect_vectra_token_id"]  # Token ID

# Prepare request
GET_URL = URL + "/"
DEVICE_HEADER = {"Authorization": "Token " + str(TOKEN)}
REQUEST = urllib.request.Request(GET_URL, headers=DEVICE_HEADER)

# To use the server validation feature, use the keyword 'ssl_context' in the http reqeust
R = urllib.request.urlopen(REQUEST, context=ssl_context)
response = {}

# Like the action response, the response object must have a "succeeded" field to denote success.
# It can also optionally have a "result_msg" field to display a custom test result message.
if R.getcode() == 200:
    response["succeeded"] = True
    response["result_msg"] = "Successfully connected."
else:
    response["succeeded"] = False
    response["result_msg"] = "Could not connect to Vectra."
