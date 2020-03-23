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
			try:
				if (user['real_name'] == user_name):
					slack_message_user_id = user['id']
					logging.debug("Found user id " + slack_message_user_id + "for user" + user_name)
					return slack_message_user_id
			except:
				logging.debug("Slack user id not found for user " + user_name)
				return ''
		return ''
	except:
		logging.debug("No data returned from json response ")
		return ''

def get_user_channel_id (json_data, user_id):
	try:
		im_channels = json_data['ims']
		for im_channel in im_channels:
			try:
				if (im_channel['user']== user_id):
					slack_id = im_channel['id']
					logging.debug("Found slack_channel_id " + slack_id + "for user id " + user_id)
					return slack_id
			except:
				logging.debug("Slack user channel id not found for user id " + user_id)
				return ''
		return ''
	except:
		logging.debug("No data returned from json response ")
		return ''





slack_id = ""
if (slack_action_type == 'connect_slack_action_type_1'):
	#Get list of channels from workspace
	URL = "https://slack.com/api/channels.list"
	request = urllib.request.Request(URL,  headers=headers)
	resp = urllib.request.urlopen(request)
	json_resp = json.loads(resp.read())
	logging.debug("get channel.list" + str(json_resp))
	
	slack_id = get_channel_id (json_resp, slack_message_channel)

else:
	USER_URL = "https://slack.com/api/users.list"
	request = urllib.request.Request(USER_URL,  headers=headers)
	resp = urllib.request.urlopen(request)
	json_resp = json.loads(resp.read())
	logging.debug("get users.list" + str(json_resp))
	
	user_id = ""
	user_id = get_user_id(json_resp, slack_message_channel)
	logging.debug("User id is " + user_id)
	
	try:
		if (user_id != ""):
			logging.debug("In try and if user_id passed w/ " + user_id)
			IM_URL = "https://slack.com/api/im.list"
			request = urllib.request.Request(IM_URL,  headers=headers)
			resp = urllib.request.urlopen(request)
			json_resp = json.loads(resp.read())
			logging.debug(str(json_resp))
			slack_id = get_user_channel_id(json_resp,user_id)
	except:
		logging.debug("User ID failed")

	


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




