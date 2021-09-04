import time
from connectproxyserver import ConnectProxyServer, ProxyProtocol

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params.get("connect_sampleapp_url")  # Server URL

response = {}
properties = {}
action_status = {}
# Example of check what proxy is set for the session
logging.debug("SampleApp add user")
# Check if we have valid auth token or not before processing.
if params.get("connect_authorization_token"):
    # ***** Execute add user action  ***** #
    jwt_token = params.get("connect_authorization_token")
    # connect_app_instance_cache data is available when you enable app_instance_cache feature in system.conf
    # the data is available in the 'params' dictionary.
    # In this example, we are getting the existing users.
    user_list = params.get("connect_app_instance_cache")
    user_email = params.get("sampleapp_email")
    if user_list and user_email in user_list:
        # return action failed if user already exists
        logging.debug("User {} already exists. ".format(user_email))
        response["succeeded"] = False
        response["troubleshooting"] = "User already exists."
        action_status["status"] = "Failed. User already exists."
        action_status["time"] = int(time.time())
        # Add properties dictionary to response to resolve properties. It is optional
        properties["connect_sampleapp_add_user_action"] = action_status
        response["properties"] = properties
    else:
        add_user_url = url + "/users/v2/"
        device_headers = {"Content-Type": "application/json; charset=utf-8",
                          "Authorization": "Bearer " + str(jwt_token)}
        body = dict()
        logging.debug(f"Add user url: {add_user_url}")

        # For actions, you can specify user inputted parameters that must be defined in the 'property.conf' file.
        # These parameters will take in user input
        # from the CounterACT console and will be available in the 'params' dictionary.
        zones = {
            "id": "0927bf62-83f4-4766-a825-0b5d2e9749d0",
            "role_type": "00000000-0000-0000-0000-000000000002",
            "role_name": "User"
        }
        zone_array = [zones]
        body = {
            "email": params.get("sampleapp_email"),
            "user_role": "00000000-0000-0000-0000-000000000001",
            "first_name": params.get("sampleapp_first_name"),
            "last_name": params.get("sampleapp_last_name"),
            "zones": zone_array
        }

        try:
            # Create proxy server
            proxy_server = ConnectProxyServer(params)
            # Pass to use what HTTPS or HTTP or both in the protocol, pass down the ssl_verify
            with proxy_server.get_requests_session(ProxyProtocol.all, headers=device_headers, verify=ssl_verify) as session:
                # If body in json or dictionary, use "json". If encoding, or not json format, use "data".
                add_response = session.post(add_user_url, json=body, proxies=proxy_server.proxies, timeout=10)
                logging.debug("Add user response code: " + str(add_response.status_code))
                # Created response code is 201
                if 201 == add_response.status_code:
                    # If response is in json, use response.json(), otherwise, use response.text
                    logging.debug(f"Add user response text: {add_response.json()}")
                    request_response = add_response.json()

                    # For actions, the response object must have a field named "succeeded" to denote if the action
                    # succeeded or not. The field "troubleshooting" is optional to display user defined messages in
                    # CounterACT for actions. The field "cookie" is available for continuous/cancellable actions to
                    # store information for the same action. For this example, the cookie stores the id of the user,
                    # which will be used to delete the same user when this action is cancelled.
                    response["succeeded"] = True
                    id = request_response.get('id')
                    logging.debug(f"The cookie content is: {id}")
                    response["cookie"] = id
                    action_status["status"] = "Succeeded"
                    action_status["time"] = int(time.time())
                    properties["connect_sampleapp_add_user_action"] = action_status
                    properties["connect_sampleapp_last_logged_in_user"] = params.get("sampleapp_email")
                    response["properties"] = properties
                else:
                    response["succeeded"] = False
                    response["troubleshooting"] = f"Failed action. Response code: {add_response.status_code}."
                    action_status["status"] = "Failed. API return code is not successful."
                    action_status["time"] = int(time.time())
                    properties["connect_sampleapp_add_user_action"] = action_status
                    response["properties"] = properties
        except Exception as e:
            response["troubleshooting"] = f"Failed action: {str(e)}"
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
