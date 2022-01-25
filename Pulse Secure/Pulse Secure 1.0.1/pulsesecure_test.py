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

logging.debug("Test for Pulse Secure Connect App")

# General params
server = params.get("connect_pulsesecure_server")
username = params.get("connect_pulsesecure_admin_username")
password = params.get("connect_pulsesecure_admin_password")

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

# Get the api_key first. All other API calls require this.
api_key = connect_ps.api_key.key
api_key_error = connect_ps.api_key.error_msg

# Response required for the script
response = {}

# If API Key is invalid, then set the response "succeeded" key to False and the error message
if api_key is None:
    error_msg = pulsesecure_library.FSConnectPS.get_error_msg("Failed to get api_key.", api_key_error)
    response["succeeded"] = False
    response["result_msg"] = error_msg
    logging.error(error_msg)
else:
    logging.debug("Test to get all active Pulse Secure sessions.")

    # Test getting all the active sessions
    api_all_active_sessions = connect_ps.call_api("GET_ALL_ACTIVE_SESSIONS", api_key, "GET")

    # If the APIResponse was successful, then set the response "succeeded" key to True and the successful result message
    if api_all_active_sessions.is_successful:
        logging.debug("Test succeeded")
        response["succeeded"] = True
        response["result_msg"] = f"Successfully connected to Pulse Secure server.\nResponse code: {api_all_active_sessions.http_resp_code}"
    else:
        # Otherwise, set the response "succeeded" key to False and the failed result message
        response["succeeded"] = False

        # Initialize the result message to display the failed test results
        result_msg = "Failed to connect to Pulse Secure server. {}"

        # If the response code is -1, then output the exception in the result message
        if api_all_active_sessions.http_resp_code == -1:
            error_msg = f"Error: {api_all_active_sessions.exception}"
            result_msg = result_msg.format(error_msg)
        else:
            # Otherwise, output the response code in the result message
            error_msg = f"Response code is: {api_all_active_sessions.http_resp_code}"
            result_msg = result_msg.format(error_msg)

        # Set the result_msg in the response
        logging.error(result_msg)
        response["result_msg"] = result_msg
