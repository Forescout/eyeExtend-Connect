import time
from connectproxyserver import ConnectProxyServer, ProxyProtocol

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params.get("connect_sampleapp_url")  # Server URL

response = {}
properties = {}
action_status = {}
logging.debug("SampleApp delete user")
# Check if we have valid auth token or not before processing.
if params.get("connect_authorization_token"):
	# ***** PART 2 - DELETE USER  ***** #
	# Here, the cookie that was set in adding the user is being used. The user id is used to delete the user.
	jwt_token = params.get("connect_authorization_token")
	delete_user_url = url + "/users/v2/" + params.get("cookie")
	logging.debug(f"Delete user url: {delete_user_url}")
	device_headers = {"Authorization": "Bearer " + str(jwt_token)}
	try:
		# Create proxy server
		proxy_server = ConnectProxyServer(params)
		# Pass to use what HTTPS or HTTP or both in the protocol, pass down the ssl_verify
		with proxy_server.get_requests_session(ProxyProtocol.all, headers=device_headers, verify=ssl_verify) as session:
			delete_response = session.delete(delete_user_url, proxies=proxy_server.proxies)
			logging.debug(f"Proxies: {proxy_server.proxies}")
			logging.debug(f"Delete user response code: {delete_response.status_code}")
			if 200 == delete_response.status_code:
				response["succeeded"] = True
				action_status["status"] = "Succeeded"
				action_status["time"] = int(time.time())
				properties["connect_sampleapp_add_user_action"] = action_status
				response["properties"] = properties
			else:
				response["troubleshooting"] = f"Failed code: {delete_response.status_code}. Reason: {delete_response.reason}."
				logging.debug(f'Delete failed reason: {response["troubleshooting"]}')
				response["succeeded"] = False
				action_status["status"] = "Response is not successful."
				action_status["time"] = int(time.time())
				properties["connect_sampleapp_add_user_action"] = action_status
				response["properties"] = properties
	except Exception as e:
		response["troubleshooting"] = f"Failed delete action. Exception: {str(e)}"
		logging.debug(f'Delete failed reason:{response["troubleshooting"]}')
		response["succeeded"] = False
		action_status["status"] = "Failed. Exception."
		action_status["time"] = int(time.time())
		properties["connect_sampleapp_add_user_action"] = action_status
		response["properties"] = properties
else:
	response["succeeded"] = False
	response["troubleshooting"] = "Unauthorized"
	action_status["status"] = "Failed. Unauthorized."
	action_status["time"] = int(time.time())
	properties["connect_sampleapp_add_user_action"] = action_status
	response["properties"] = properties