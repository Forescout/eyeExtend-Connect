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

from urllib.request import HTTPError, URLError

jamf_to_ct_props_map = {
	"id": "connect_jamf_id",
	"managed": "connect_jamf_managed"
}

url = params["connect_jamf_url"]
url += "/JSSResource/computers/subset/basic"
username = params["connect_jamf_username"] 
password = params["connect_jamf_password"]  
response = {}

logging.info("The URL is: {}".format(url))
request = urllib.request.Request(url)
request.add_header("Authorization", "Basic %s" % jamf_lib.create_auth(username, password))
request.add_header("Accept", "application/json")
try:
	resp = urllib.request.urlopen(request, context=ssl_context)
	endpoint_data = json.loads(resp.read())["computers"]
	logging.debug("The response from Jamf is {}".format(endpoint_data))
	properties = {}
	endpoints = []
	for endpoint in endpoint_data:
		new_endpoint = {}
		mac = endpoint["mac_address"]
		mac = mac.replace(":", "").lower()
		new_endpoint["mac"] = mac
		properties = {}
		for key, value in jamf_to_ct_props_map.items():
			if key in endpoint:
				properties[value] = endpoint[key]
		new_endpoint["properties"] = properties
		endpoints.append(new_endpoint)
	response["endpoints"] = endpoints
except HTTPError as e:
	response["error"] = "Failed to poll. Response code: {}".format(e.code)
except URLError as e:
	response["error"] = "Failed to poll. {}".format(e.reason)
except Exception as e:
	response["error"] = "Failed to poll. {}".format(str(e))

