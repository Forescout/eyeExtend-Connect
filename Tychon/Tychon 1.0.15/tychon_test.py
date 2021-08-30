# -*- coding: utf-8 -*-
#Software: Copyright © 2020-21 Tychon, LLC
#License: Copyright © 2020 Forescout Technologies, Inc.
 
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
 
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
 
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import logging
import urllib
import json
import ssl
import urllib
from urllib import request, parse
from urllib.request import HTTPError, URLError


ip = params.get("connect_tychon_ip")
port = params.get("connect_tychon_port")
apiKey = params.get("connect_tychon_api_key")

headers = {
    "accept": "application/json",
    "PARTNER-API-KEY": apiKey,
    "content-type":"application/json"
}

response = {}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    _test_ping = request.Request("https://" + ip + ":" + port + "/dmn/partner/version", headers=headers, method="GET")
    _test_res = request.urlopen(_test_ping, context=ssl_context)
    _response = json.loads(_test_res.read())

    response["succeeded"] = True
    response['result_msg'] = f'Successfully connected. \n{_response}'
    

except HTTPError as e:
    response["succeeded"] = False
    response["error"] = "HTTP Error : Could not connect to TYCHON. Response code: {}".format(e.code) 

    if e.code == 400:
        response["error"] = response["error"] + " " + "BAD REQUEST"
    elif e.code == 401:
        response["error"] = response["error"] + " " + "NOT FOUND"
    elif e.code == 403:
        response["error"] = response["error"] + " " + "FORBIDDEN"
    elif e.code == 404:
        response["error"] = response["error"] + " " + "UNAUTHORIZED"
    elif e.code == 500:
        response["error"] = response["error"] + " " + "INTERNAL SERVER ERROR"
    
except URLError as e:
    response["succeeded"] = False
    response["error"] = "URL Error : Could not connect to TYCHON. {}".format(e.reason)
    
except Exception as e:
    response["succeeded"] = False
    response["error"] = "Exception : Could not connect to TYCHON. {}".format(str(e))
    
