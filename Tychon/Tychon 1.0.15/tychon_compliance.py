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
mac = params["mac"]

upper_mac = mac.upper()
colon_mac = ":".join(upper_mac[i:i+2] for i in range(0,12,2))

request = urllib.request.Request("https://" + ip + ":" + port + "/dmn/partner/compliance/mac/")

request.add_header("accept", "application/json")
request.add_header("PARTNER-API-KEY", apiKey)
request.add_header("Content-Type", "application/json")

body = '\
{\
  "macs": ["' + colon_mac + '"]\
}'

logging.info(body)

request.data = body.encode(encoding="UTF-8")

request.get_method = lambda: 'PUT'

response = {}
try:
	resp = urllib.request.urlopen(request, context=ssl_context)
	resp_bytes = resp.read()
	resp_ascii = resp_bytes.decode(encoding="UTF-8")
	resp_json = json.loads(resp_ascii)
	tags = ""
	managed = False
	hbss = ""
	if len(resp_json) > 0:
		tags_list = resp_json[0]["host.tags"]
		tags = json.dumps(tags_list)
		managed = resp_json[0]["host.managed"]
		hbss_list = resp_json[0]["host.hbss"]
		hbss = json.dumps(hbss_list)
	properties = {}
	properties["connect_tychon_compliance_managed"] = managed
	properties["connect_tychon_compliance_tags"] = tags
	properties["connect_tychon_compliance_hbss"] = hbss
	response["properties"] = properties
except HTTPError as e:
	response["error"] = "HTTPError: {}".format(e.code)
except URLError as e:
	response["error"] = "URLError: {}".format(e.reason)
except Exception as e:
	response["error"] = "Exception: {}".format(str(e))
