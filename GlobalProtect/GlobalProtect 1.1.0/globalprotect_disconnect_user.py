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

logging.debug("Disconnect user action for GlobalProtect Connect App")
# General Params
connection = globalprotect_library.Connection()
connection.server = params.get("connect_globalprotect_server")
connection.username = params.get("connect_globalprotect_admin_username")
connection.password = params.get("connect_globalprotect_admin_password")
connection.use_syslog = params.get("connect_globalprotect_use_syslog")
connection.server_from_syslog = params.get("connect_globalprotect_firewall")
connection.ssl_context = ssl_context
# Properties that use to disconnect user
user_name = params.get("connect_globalprotect_user")
user_domain = params.get("connect_globalprotect_domain")
user_computer = params.get("connect_globalprotect_computer_name")
user_gateway = params.get("connect_globalprotect_gateway")

def get_gateway_portal():
    """
    Get gateway associated portal info that is in <Gateway-N> format and used to disconnect a user
    Returns:
         Portal name. Can be empty string if not found or error
    """
    logging.debug("In get_gateway_portal")
    api_resp_gateway = connect_gp.call_api("OC_SHOW_GATEWAY", user_gateway)
    # result should be a APIResponse
    if api_resp_gateway.is_successful:
        # Only return a string of the gateway name, not in XML format
        result_tree = api_resp_gateway.xml_content
        result_portal = globalprotect_library.FSConnectGP.get_element(result_tree, 'entry/portal')
        logging.debug("get_gateway_portal content: " + result_portal)
        return result_portal
    else:
        return ""


def get_missing_props():
    """
    Check user name, computer name and gateway required to disconnect a user has content or not
    Returns:
         A set that contains missing required fields to disconnect a user
    """
    missing = set()
    if user_name is None or user_name is "":
        missing.add("User name")
    if user_computer is None or user_computer is "":
        missing.add("Computer name")
    if user_gateway is None or user_gateway is "":
        missing.add("Gateway")
    return missing


# Token
logging.debug("Init library")
connect_gp = globalprotect_library.FSConnectGP()
connect_gp.set_init(connection)
token = connect_gp.token.token
token_error = connect_gp.token.error_msg

error_msg = ""
response = {}

# Check token
if token is None:
    error_msg = globalprotect_library.FSConnectGP.get_error_msg("Failed to get token.", token_error)
    response["succeeded"] = False
    # Action, use troubleshooting
    response["troubleshooting"] = error_msg
    logging.error(error_msg)
else:
    param_missing = get_missing_props()
    # Check required fields
    if len(param_missing) > 0:
        flat_missing = ", ".join(param_missing)
        missing_msg = "Dependencies not met, required fields are missing: {}".format(flat_missing)
        response["succeeded"] = False
        # For action, put in troubleshooting
        response["troubleshooting"] = missing_msg
        logging.warning(missing_msg)
    else:
        # Get gateway portal, used to disconnect
        gateway_portal = get_gateway_portal()
        if gateway_portal is None or gateway_portal is "":
            response["succeeded"] = False
            error_msg = "Failed to get gateway portal."
            response["troubleshooting"] = error_msg
            logging.error(error_msg)
        else:
            disconnect_param = {
                "user": user_name,
                "domain": user_domain,
                "computer": user_computer,
                "gateway": gateway_portal,
            }

            # Send logout
            api_resp_disconnect = connect_gp.call_api("REQ_CLIENT_LOGOUT", disconnect_param)
            if api_resp_disconnect.is_successful:
                # <response status="success">
                # <result>
                # <response status="error">
                # <gateway>GatewayN</gateway>
                # <user>UserName</user>
                # <computer>ComputerName</computer>
                # <error>Invalid user name</error>
                # </response>
                # </result>
                # </response>
                # Response has another layer of response
                logging.debug("In disconnect after successful.")
                response_status = connect_gp.parse_status_with_error_ele(api_resp_disconnect.xml_content)
                if "success" == response_status.status:
                    response["succeeded"] = True
                    response["result_msg"] = "Successfully disconnect user."
                else:
                    response["succeeded"] = False
                    response["troubleshooting"] = response_status.error_msg
            else:
                response["succeeded"] = False
                error_msg = "Failed to disconnect user {}. {}"
                if api_resp_disconnect.http_resp_code and api_resp_disconnect.http_resp_code == -1:
                    # case for exception
                    error_msg = error_msg.format(
                        user_name, "Response message is: {}".format(str(api_resp_disconnect.result.exception)))
                else:
                    error_msg = error_msg.format(
                        user_name, "Response code is: {}".format(api_resp_disconnect.http_resp_code))
                response["troubleshooting"] = error_msg
