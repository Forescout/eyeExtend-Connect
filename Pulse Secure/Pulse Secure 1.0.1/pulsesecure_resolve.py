"""
Copyright © 2021 Forescout Technologies, Inc.

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
"""

import logging


def get_session_with_username_and_ip(resolve_username, resolve_ip):
    """
    Get the connection details with the given IP address and the username
    Args:
        resolve_username: the username of the user who has active sessions
        resolve_ip: string representation of the IP address used for resolving the specific session
    Returns:
        A JSON object representing the session details from the given IP address
    """
    # Call the api using the GET_A_PARTICULAR_ACTIVE_SESSION command to get all the sessions opened by resolve_username
    api_active_sessions = connect_ps.call_api("GET_A_PARTICULAR_ACTIVE_SESSION", urllib.parse.quote_plus(resolve_username), "GET")

    # Result should be an APIResponse
    if api_active_sessions.is_successful:
        json_object = api_active_sessions.json

        # The active session list is a few more levels deeper into the JSON object
        active_sessions = json_object["active-users"]["active-user-records"]

        # If the "active-user-record" key exists in active_sessions, that means there exists a list of active sessions
        if "active-user-record" in active_sessions:
            for session in active_sessions["active-user-record"]:
                if session["network-connect-ip"] == resolve_ip:
                    return session
    else:
        logging.debug("Result is None")
        return None


logging.debug("Resolving for PulseSecure Connect App")

# Mapping between Pulse Secure API response fields to CounterACT properties
pulsesecure_to_ct_props_map = {
    "active-user-name": "connect_pulsesecure_active_username",
    "agent-type": "connect_pulsesecure_agent_type",
    "authentication-realm": "connect_pulsesecure_authentication_realm",
    "endpoint-security-status": "connect_pulsesecure_endpoint_security_status",
    "events": "connect_pulsesecure_events",
    "login-node": "connect_pulsesecure_login_node",
    "network-connect-transport-mode": "connect_pulsesecure_network_connect_transport_mode",
    "session-id": "connect_pulsesecure_session_id",
    "user-roles": "connect_pulsesecure_user_roles",
    "user-sign-in-time": "connect_pulsesecure_user_sign_in_time"
}

# Params needed for resolve
server = params.get("connect_pulsesecure_server")
username = params.get("connect_pulsesecure_admin_username")
password = params.get("connect_pulsesecure_admin_password")
resolve_ip = params.get("ip")
resolve_username = params.get("connect_pulsesecure_active_username")

# Proxy support
proxy_params = {}
proxy_params["proxy_enabled"] = params.get("connect_proxy_enable")
proxy_params["proxy_basic_auth_ip"] = params.get("connect_proxy_ip")
proxy_params["proxy_port"] = params.get("connect_proxy_port")
proxy_params["proxy_username"] = params.get("connect_proxy_username")
proxy_params["proxy_password"] = params.get("connect_proxy_password")

# Initialize the PulseSecure object
connect_ps = pulsesecure_library.FSConnectPS()
connect_ps.set_init(server, username, password, ssl_context, proxy_params)

# Get the API key first. All other API calls required this
api_key = connect_ps.api_key.key
api_key_error = connect_ps.api_key.error_msg

# Response and properties required for the script
response = {}
properties = {}

# If API Key is invalid, then set the error message and the response "succeeded" key to False
if api_key is None:
    error_msg = pulsesecure_library.FSConnectPS.get_error_msg("Failed to get api_key.", api_key_error)
    response["error"] = error_msg
    logging.error(error_msg)
else:
    logging.debug("Resolving VPN endpoint properties")

    # Get the active session associated with the resolve_username and resolve_ip
    user_session = get_session_with_username_and_ip(resolve_username, resolve_ip)

    # If no active session was returned, then set an error message
    if user_session is None:
        error_msg = "Failed to get endpoint info"
        response["error"] = error_msg
        logging.error(error_msg)
    else:
        logging.debug("Getting user session properties")
        # Iterate through the properties of the user session and fill the Connect properties dictionary accordingly
        for key, value in user_session.items():
            if key in pulsesecure_to_ct_props_map and key != "network-connect-ip":
                # The events property should be cast to an int
                if key == "events":
                    properties[pulsesecure_to_ct_props_map[key]] = int(value)
                # The user-sign-in-time property should be converted to an epoch number
                elif key == "user-sign-in-time":
                    properties[pulsesecure_to_ct_props_map[key]] = pulsesecure_library.FSConnectPS.convert_time_str_to_epoch_num(value)
                # All other properties are strings
                else:
                    properties[pulsesecure_to_ct_props_map[key]] = value
        logging.debug(f"Resolved properties: {properties}")
        response["properties"] = properties
