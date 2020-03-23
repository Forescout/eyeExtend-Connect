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
# v1.0.0 Azure Active Directory Test
# Keith Gilbert
from urllib import request, parse

logging.info("****************************** params: {}".format(params))

# Values for system.conf passed to params
response = {}
if ("connect_authorization_token" in params) and params["connect_authorization_token"] != "":
	access_token = params["connect_authorization_token"]
	if "connect_azuread_test_user" in params:
		test_user = params["connect_azuread_test_user"]
		user_url_start = "https://graph.microsoft.com/v1.0/users?$filter=startswith(userPrincipalName%2C+\'"
		user_url_end = "\')"
		user_url = user_url_start + test_user + user_url_end
		user_header = {"Authorization": "Bearer " + str(access_token)}
		req2 = request.Request(user_url, headers=user_header)
		resp2 = request.urlopen(req2, context=ssl_context)
		req2_response = json.loads(resp2.read())
		logging.info("******************************req2_response = {}".format(str(req2_response)))
		if resp2.getcode() == 200 and req2_response["value"]:
			logging.info("****************************** resp2.getcode() == 200")
			response["succeeded"] = True
			response["result_msg"] = "Successful connection : Test User = " + test_user + " >> " + str(req2_response["value"])
		else:
			response["succeeded"] = True
			response["result_msg"] = "Successful connection : Test User doesn't exist"
	else:
		response["succeeded"] = True
		response["result_msg"] = "Successful connection : Test User not defined"
else:
	response["succeeded"] = False
	response["result_msg"] = "Failed connection : couldn't connect to login.microsoftonline server."