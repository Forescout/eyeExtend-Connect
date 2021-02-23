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
slack_app_token = params["connect_slack_workspace_app_oauth_token"]
slack_workspace = params["connect_slack_workspace_name"]

headers = {"content-type": "application/json", "Authorization": "Bearer " + str(slack_app_token)}
response = {}

## Verify all APIs required for the App return valid values back and are authenticated
URL = "https://slack.com/api/conversations.list?limit=5&exclude_archived=true&types=public_channel,private_channel"
request = urllib.request.Request(URL,  headers=headers)
resp = urllib.request.urlopen(request)
json_resp = json.loads(resp.read())
if "channels" not in json_resp:
   response["succeeded"] = False
   response["result_msg"] = str(json_resp)   
else:
	USER_URL = "https://slack.com/api/users.list?limit=5"
	request = urllib.request.Request(USER_URL,  headers=headers)
	resp = urllib.request.urlopen(request)
	json_resp = json.loads(resp.read())

	if "members" not in json_resp:
	   response["succeeded"] = False
	   response["result_msg"] = str(json_resp)
	else:	
		response["succeeded"] = True
		response["result_msg"] = "Successfuly Connected and authenticated with Slack workspace " + slack_workspace
