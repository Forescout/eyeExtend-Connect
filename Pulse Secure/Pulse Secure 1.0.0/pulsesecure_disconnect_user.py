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


def disconnect_user(session_id):
    """
    Disconnect a user given the session id
    Args:
        session_id: the session id used for disconnect
    Returns:
        APIResponse object with the results of disconnecting the user
    """
    # Call the api using the END_ACTIVE_SESSION command to delete the session with the session_id
    api_disconnect_session = connect_ps.call_api("END_ACTIVE_SESSION", session_id, "DELETE")

    # Return the APIResponse object from the API call
    return api_disconnect_session


logging.debug("Disconnect user action for PulseSecure Connect App")

# Params needed for disconnecting a user
server = params.get("connect_pulsesecure_server")
username = params.get("connect_pulsesecure_admin_username")
password = params.get("connect_pulsesecure_admin_password")
session_id = params.get("connect_pulsesecure_session_id")

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

# Response and error message required for the script
error_msg = ""
response = {}

# If API Key is invalid, then set the error message and the response "succeeded" key to False
if api_key is None:
    error_msg = pulsesecure_library.FSConnectPS.get_error_msg("Failed to get api_key.", api_key_error)
    response["succeeded"] = False
    response["troubleshooting"] = error_msg
    logging.error(error_msg)
else:
    logging.debug("Attempting to disconnect user")

    # Get the APIResponse object from calling the disconnect_user function
    api_disconnect_response = disconnect_user(session_id)
    if api_disconnect_response.is_successful:
        result_msg = "Successfully disconnected user"
        response["succeeded"] = True
        logging.debug(result_msg)
    else:
        response["succeeded"] = False
        error_msg = "Failed to disconnect session with sid: {}. {}"
        if api_disconnect_response.http_resp_code and api_disconnect_response.http_resp_code == -1:
            error_msg = error_msg.format(session_id, f"Response message: {api_disconnect_response.exception}")
        else:
            error_msg = error_msg.format(session_id, f"HTTP code: {api_disconnect_response.http_resp_code}")
        logging.error(error_msg)
        response["troubleshooting"] = error_msg
