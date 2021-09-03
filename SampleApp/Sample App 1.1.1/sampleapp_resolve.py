from connectproxyserver import ConnectProxyServer, ProxyProtocol
# Mapping between SampleApp API response fields to CounterACT properties
sampleapp_to_ct_props_map = {
	"state": "connect_sampleapp_state",
	"last_logged_in_user": "connect_sampleapp_last_logged_in_user",
	"mac_addresses": "connect_sampleapp_mac_addresses",
	"is_safe": "connect_sampleapp_is_safe",
	"id": "connect_sampleapp_id"
}

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params.get("connect_sampleapp_url")  # Server URL

response = {}
logging.debug("SampleApp resolve")
token_returned = params.get("connect_authorization_token")
# Check if we have valid auth token or not before processing.
if token_returned:
	# For properties and actions defined in the 'property.conf' file, CounterACT properties can be added as dependencies.
	# These values will be found in the params dictionary if CounterACT was able to resolve the properties.
	# If not, they will not be found in the params dictionary.
	jwt_token = token_returned
	if "mac" in params:
		logging.debug(f'mac is: {params.get("mac")}')
		mac = '-'.join(params.get("mac")[i:i+2] for i in range(0, 12, 2))
		get_mac_url = url + "/devices/v2/macaddress/" + mac
		logging.debug(f"get mac url is: {get_mac_url}")
		device_headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + str(jwt_token)}

		try:
			# Create proxy server
			proxy_server = ConnectProxyServer(params)
			# Pass to use what HTTPS or HTTP or both in the protocol, pass down the ssl_verify
			with proxy_server.get_requests_session(ProxyProtocol.all, headers=device_headers, verify=ssl_verify) as session:
				# Example to show app writer can see what is set in the session to debug
				logging.debug(f"Headers is: {session.headers}")
				logging.debug(f"Session proxies is: {session.proxies}")
				logging.debug(f"Proxies: {proxy_server.proxies}")
				logging.debug(f"Verify is: {session.verify}")
				resolve_response = session.get(get_mac_url, proxies=proxy_server.proxies)
				logging.debug(f"Resolve response code: {resolve_response.status_code}")
				if 200 == resolve_response.status_code:
					logging.debug(f"Resolve response text: {resolve_response.text}")
					request_response = json.loads(resolve_response.text)
					"""			
					# All responses from scripts must contain the JSON object 'response'. Host property resolve scripts will 
					need to populate a 'properties' JSON object within the JSON object 'response'. The 'properties' object will 
					be a key, value mapping between the CounterACT property name and the value of the property
					"""
					properties = {}
					if request_response:
						return_values = request_response[0]
						logging.debug(f"Resolve response text on 0 element: {request_response[0]}")
						for key, value in return_values.items():
							if key in sampleapp_to_ct_props_map:
								properties[sampleapp_to_ct_props_map[key]] = value

					response["properties"] = properties
				else:
					response["error"] = resolve_response.reason
		except Exception as e:
			response["error"] = f"Could not resolve properties: {e}."
	else:
		response["error"] = "No mac address to query the endpoint for."
else:
	response["error"] = "Unauthorized"
