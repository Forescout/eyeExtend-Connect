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

url = params["connect_jamf_url"]
policy_name = urllib.parse.quote(params["jamf_policy"])
url += "/JSSResource/policies/name/" + policy_name
logging.debug("The URL is: {}".format(url))
username = params["connect_jamf_username"] 
password = params["connect_jamf_password"]  
response = {}

if "dhcp_hostname" in params:
	xml_body = '<policy><name>' + params["jamf_policy"] + '</name><scope><computer_additions><computer>'
	computer = '<name>' + params["dhcp_hostname"] + '</name>'
	xml_body += computer + '</computer></computer_additions></scope></policy>'
	logging.debug("Content of xml body: {}".format(xml_body))
	xml_body = xml_body.encode("utf-8")
	try:
		request = urllib.request.Request(url, data=xml_body, method='PUT')
		request.add_header("Authorization", "Basic %s" % jamf_lib.create_auth(username, password))
		request.add_header("Content-Type", "application/xml")
		resp = urllib.request.urlopen(request, context=ssl_context)
		logging.info("Response code is {}".format(resp.getcode()))
		if resp.getcode() >= 200 and resp.getcode() < 300:
			response["succeeded"] = True
	except HTTPError as e:
		response["succeeded"] = False
		response["troubleshooting"] = "Failed action. Response code: {}".format(e.code)
	except URLError as e:
		response["succeeded"] = False
		response["troubleshooting"] = "Failed action. {}".format(e.reason)
	except Exception as e:
		response["succeeded"] = False
		response["troubleshooting"] = "Failed action. {}".format(str(e))				
else:
	logging.error("Adding the endpoint to the scope of the policy requires a hostname.")
	response["succeeded"] = False
	response["troubleshooting"] = "Failed action. Endpoint does not have a hostname."
