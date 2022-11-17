"""
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
"""

import logging

logging.debug("Test for GlobalProtect Connect App")

# General params
connection = globalprotect_library.Connection()
connection.server = params.get("connect_globalprotect_server")
connection.username = params.get("connect_globalprotect_admin_username")
connection.password = params.get("connect_globalprotect_admin_password")
connection.use_syslog = params.get("connect_globalprotect_use_syslog")
# Test can't get connect_globalprotect_firewall info since it is not defined in system.conf file
connection.ssl_context = ssl_context

logging.debug("Disconnect user action for GlobalProtect Connect App")
# Init GP class
logging.debug("Init library")
connect_gp = globalprotect_library.FSConnectGP()
connect_gp.set_init(connection)

# Get the key_token first. All other API calls require this.
token = connect_gp.token.token
token_error = connect_gp.token.error_msg

response = {}

# Token is invalid
if token is None:
    error_msg = globalprotect_library.FSConnectGP.get_error_msg("Failed to get token.", token_error)
    response["succeeded"] = False
    response["result_msg"] = error_msg
    logging.error(error_msg)
else:
    # Do test, using checking admin user get user info.
    logging.debug("Test to show user gateway.")
    api_show_user_gateway = connect_gp.call_api("OC_SHOW_USER_GATEWAY_INFO", connection.username)
    # result should be a APIResponse
    if api_show_user_gateway.is_successful:
        logging.debug("Test: Succeeded")
        response["succeeded"] = True
        response["result_msg"] = "Successfully connected to Global Protect server."
    else:
        logging.debug("Test: Failed")
        response["succeeded"] = False
        response["result_msg"] = "Failed to connect to Global Protect server. "
        error_msg = ""
        if api_show_user_gateway.http_resp_code == -1:  # case for exception
            error_msg = "Error: {}".format(str(api_show_user_gateway.exception))
        else:
            if api_show_user_gateway.http_resp_code is None:
                error_msg = "Error is: {}".format(api_show_user_gateway.api_status.error_msg)
            else:
                error_msg = "Response code is: {}. Error is: {}".format(api_show_user_gateway.http_resp_code,
                                                                        api_show_user_gateway.api_status.error_msg)
        response["troubleshooting"] = error_msg

