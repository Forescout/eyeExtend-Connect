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
slack_message_post = params["connect_slack_action_message"]
slack_message_channel = params["connect_slack_action_input_channel"]
slack_message_content_message_type = params["connect_slack_action_message_type"]
slack_action_type = params["connect_slack_action_type"] 

headers = {"content-type": "application/json", "Authorization": "Bearer " + str(slack_app_token)}
response = {}

def get_channel_id (json_data, channel_name):
	try:
		slack_channels = json_data['channels']
		for slack_channel in slack_channels:
			try:
				if (slack_channel['name'] == slack_message_channel):
					slack_id = slack_channel['id']
					logging.debug("Found slack_id " + slack_id + "for channel" + channel_name)
					return slack_id
			except:
				logging.debug("Slack channel not found for channel " + channel_name)
				return ''
		return ''
	
	except:
		logging.debug("No data returned from json response ")
		return ''
	
def get_user_id (json_data, user_name):
	try:
		users = json_data['members']
		for user in users:
			if ('real_name' in user): 
				if (user['real_name'] == user_name):
					slack_message_user_id = user['id']
					logging.debug("Found user id " + slack_message_user_id + "for user" + user_name)
					return slack_message_user_id
			else:
				continue
		return ''
	except:
		logging.debug("No data returned from json response" )
		return ''





slack_id = ""
if (slack_action_type == 'connect_slack_action_type_1'):
	#Get list of channels from workspace
	URL = "https://slack.com/api/channels.list"
	request = urllib.request.Request(URL,  headers=headers)
	resp = urllib.request.urlopen(request)
	json_resp = json.loads(resp.read())
	#logging.debug("get channel.list" + str(json_resp))
	
	slack_id = get_channel_id (json_resp, slack_message_channel)

else:
	USER_URL = "https://slack.com/api/users.list"
	request = urllib.request.Request(USER_URL,  headers=headers)
	resp = urllib.request.urlopen(request)
	json_resp = json.loads(resp.read())
	logging.debug("get users.list" + str(json_resp))
	
	user_id = ""
	user_id = get_user_id(json_resp, slack_message_channel)
	#logging.debug("User id is " + user_id)
	
	if (user_id != ""):
		conv_headers = {"Authorization": "Bearer " + str(slack_app_token)}
		CONV_URL = "https://slack.com/api/conversations.open?users=" + user_id
		
		request = urllib.request.Request(CONV_URL, headers=conv_headers, data=bytes(0))
		resp = urllib.request.urlopen(request)
		json_resp = json.loads(resp.read())
		logging.debug("Conv API Status: " + str(json_resp['ok']))
		logging.debug(str(json_resp))
		if json_resp['ok'] == True:
			ch_id = json_resp['channel']
			try:
				slack_id = json_resp['channel']['id']
				logging.debug("slack id " + slack_id)
			except:
				logging.debug("Failed to retrieve Channel ID from Conversation API Response")
		else:
			logging.debug("Conversation API Response with Failure")

	


if (slack_id != ""):
	URL = "https://slack.com/api/chat.postMessage"

	if (slack_message_content_message_type == 'connect_slack_message_type_1'):
		body = {"channel": str(slack_id), "text": str(slack_message_post)}	
	else:
		body = {"channel": str(slack_id), "blocks": slack_message_post}

	request = urllib.request.Request(URL,  headers=headers, data=bytes(json.dumps(body),encoding="utf-8"))
	resp = urllib.request.urlopen(request)
	response["succeeded"] = True
	response["response_message"] = "Posted slack_action_type is" + slack_action_type
else:
	logging.debug("Unable to find slack_id for channel or user" + slack_message_channel)
	response["succeeded"] = False
	response["troubleshooting"] = "Unable to find " + slack_message_channel  +" channel or user in workspace"




