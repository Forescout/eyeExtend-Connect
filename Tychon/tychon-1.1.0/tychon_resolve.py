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
from urllib.request import HTTPError, URLError

ip = params["connect_tychon_ip"]
port = params["connect_tychon_port"]
apiKey = params["connect_tychon_api_key"]
days = params["connect_tychon_vulnerability_days"]
index = params["connect_tychon_cve_iava_index"]
mac = params["mac"]

upper_mac = mac.upper()
colon_mac = ":".join(upper_mac[i:i+2] for i in range(0,12,2))

request = urllib.request.Request("https://" + ip + ":" + port + "/dmn/partner/compliance-failed/" + colon_mac)

request.add_header("accept", "application/json")
request.add_header("PARTNER-API-KEY", apiKey)
request.add_header("Content-Type", "application/json")

body = '\
{\
   "eventDays": '+ days + ' ,\
   "targetIndex": "' + index + '"\
}'

request.data = body.encode(encoding="UTF-8")

request.get_method = lambda: 'PUT'

response = {}
try:
	resp = urllib.request.urlopen(request, context=ssl_context)
	resp_bytes = resp.read()
	resp_ascii = resp_bytes.decode(encoding="UTF-8")
	resp_json = json.loads(resp_ascii)
	host_id = ""
	cves = ""
	iavas = ""
	if len(resp_json) > 0:
		host_id = resp_json[0]["host.id"]
		cves = resp_json[0]["cveFailed"]
		iavas = resp_json[0]["iavaFailed"]
	properties = {}
	properties["connect_tychon_host_id"] = host_id
	properties["connect_tychon_cves"] = cves
	properties["connect_tychon_iavas"] = iavas
	response["properties"] = properties
except HTTPError as e:
	response["error"] = "HTTPError: {}".format(e.code)
except URLError as e:
	response["error"] = "URLError: {}".format(e.reason)
except Exception as e:
	response["error"] = "Exception: {}".format(str(e))
