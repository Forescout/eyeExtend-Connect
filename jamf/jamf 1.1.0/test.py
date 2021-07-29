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
username = params["connect_jamf_username"]
password = params["connect_jamf_password"]

request = urllib.request.Request(url + "/JSSResource/computers")
request.add_header("Authorization", "Basic %s" % jamf_lib.create_auth(username, password))
request.add_header("Accept", "application/json")
response = {}
try:
	resp = urllib.request.urlopen(request, context=ssl_context)
	response["succeeded"] = True
	response["result_msg"] = "Successfully connected to Jamf."
except HTTPError as e:
	response["succeeded"] = False
	response["error"] = "Could not connect to Jamf. Response code: {}".format(e.code)
except URLError as e:
	response["succeeded"] = False
	response["error"] = "Could not connect to Jamf. {}".format(e.reason)
except Exception as e:
	response["succeeded"] = False
	response["error"] = "Could not connect to Jamf. {}".format(str(e))