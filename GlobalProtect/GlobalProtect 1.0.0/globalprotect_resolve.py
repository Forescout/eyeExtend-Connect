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

logging.debug("Resolve for GlobalProtect Connect App")

# Params needed for resolve
server = params.get("connect_globalprotect_server")
username = params.get("connect_globalprotect_admin_username")
password = params.get("connect_globalprotect_admin_password")
ip = params.get("ip")


def get_ip_user_mapping():
    """
    Get current user mapping using the endpoint IP
    Returns: Triplets
        user name
        IP type
        virtual system name
    """
    logging.debug("in get_ip_user_mapping")
    api_ip_user_resp = connect_gp.call_api("OC_SHOW_IP_USER_MAPPING", ip)
    if api_ip_user_resp.is_successful:
        # <response status="success">
        # <result>
        # <entry>
        # <ip>10.100.76.13</ip>
        # <vsys>vsys1</vsys>
        # <type>GP</type>
        # <user>labvpnuser1</user>
        # <idle_timeout>9576</idle_timeout>
        # <timeout>9576</timeout>
        # </entry>
        # </result>
        # </response>
        # When user is logged out
        # <response status="success"><result></result></response>
        result_tree = api_ip_user_resp.xml_content
        # Assuming only one entry ??
        user_from_ip = globalprotect_library.FSConnectGP.get_element(result_tree, 'entry/user')
        logging.debug("Get user: {}".format(user_from_ip))
        type_from_ip = globalprotect_library.FSConnectGP.get_element(result_tree, 'entry/type')
        logging.debug("Get IP type: {}".format(type_from_ip))
        vsys_from_ip = globalprotect_library.FSConnectGP.get_element(result_tree, 'entry/vsys')
        logging.debug("Get location: {}".format(vsys_from_ip))
        return user_from_ip, type_from_ip, vsys_from_ip
    else:
        "", "", ""


def get_user_gateway_info(info_user):
    """
    Get user gateway information
    Returns: Four variables
        User name
        Computer name
        Client type
        User domain
    """
    logging.debug("In get_user_gateway_info")
    api_resp_user_info = connect_gp.call_api("OC_SHOW_USER_GATEWAY_INFO", info_user)
    # result should be a APIResponse
    if api_resp_user_info.is_successful:
        # <response status="success">
        # <result>
        # <entry>
        # <domain/>
        # <islocal>yes</islocal>
        # <username>labvpnuser1</username>
        # <primary-username>labvpnuser1</primary-username>
        # <computer>EP-S10-W7-1</computer>
        # <client>
        # Microsoft Windows 7 Ultimate Edition Service Pack 1, 64-bit
        # </client>
        # <vpn-type>Device Level VPN</vpn-type>
        # <virtual-ip>10.100.76.13</virtual-ip>
        # <virtual-ipv6>::</virtual-ipv6>
        # <public-ip>10.100.3.126</public-ip>
        # <public-ipv6>::</public-ipv6>
        # <tunnel-type>IPSec</tunnel-type>
        # <public-connection-ipv6>no</public-connection-ipv6>
        # <login-time>Feb.18 11:51:00</login-time>
        # <login-time-utc>1582055460</login-time-utc>
        # <lifetime>2592000</lifetime>
        # </entry>
        # </result>
        # </response>
        # Error case
        # <response status="error" code="17"><msg><line>
        # <![CDATA[ show -> global-protect-gateway -> current-user -> user is invalid]]></line></msg></response>
        result_tree = api_resp_user_info.xml_content
        result_computer = globalprotect_library.FSConnectGP.get_element(result_tree, 'entry/computer')
        logging.debug("Get computer: {}".format(result_computer))
        result_client_type = globalprotect_library.FSConnectGP.get_element(result_tree, 'entry/client')
        logging.debug("Get client type: {}".format(result_client_type))
        result_username = globalprotect_library.FSConnectGP.get_element(result_tree, 'entry/username')
        logging.debug("Get user name: {}".format(result_username))
        result_domain = globalprotect_library.FSConnectGP.get_element(result_tree, 'entry/domain')
        logging.debug("Get domain: {}".format(result_domain))
        return result_username, result_computer, result_client_type, result_domain
    else:
        "", "", "", ""


def get_current_user_gateway(vir_sys):
    """
    Get current user gateway info
    Args:
        vir_sys: virtual machine name
    Returns:
        gateway name. Can be empty string if not found or error
    """
    logging.debug("In get_current_user_gateway")
    api_resp_user_gateway = connect_gp.call_api("XPATH_GET_GATEWAY", vir_sys)
    # result should be a APIResponse
    if api_resp_user_gateway.is_successful:
        # Only return a string of the gateway name, not in XML format
        result_tree = api_resp_user_gateway.xml_content
        result_gateway = result_tree.find('entry').get('name', "")
        logging.debug("Response get_current_user_gateway content: " + result_gateway)
        return result_gateway
    else:
        return ""


def parse_ip_user(user):
    """
    Get user without domain name
    Args:
        user: user name. Might have domain name with it. calab.forescout.com\vpntest1
    Returns:
        user name without domain. vpntest1 is returned
    """
    logging.debug("In parse_ip_user")
    name = user
    names = name.split("\\")
    if len(names) >= 2:
        name = names[1]
    return name


# Init GP class
logging.debug("Init library")
connect_gp = globalprotect_library.FSConnectGP()
connect_gp.set_init(server, username, password, ssl_context)

# Get the key_token first. All other API calls require this.
token = connect_gp.token.token
token_error = connect_gp.token.error_msg

# Return objects
response = {}
properties = {}

# Token is invalid
if token is None:
    error_msg = globalprotect_library.FSConnectGP.get_error_msg("Failed to get token.", token_error)
    response["succeeded"] = False
    # For resolve, put in error
    response["error"] = error_msg
    logging.error(error_msg)
else:
    logging.debug("Call user IP mapping")
    # Get user
    ip_user, ip_type, virtual_sys = get_ip_user_mapping()
    properties["connect_globalprotect_iptype"] = ip_type
    logging.debug("Full User: {}".format(ip_user))
    logging.debug("IP type: {}".format(ip_type))
    logging.debug("Virtual system: {}".format(virtual_sys))
    error_msg = ""

    if ip_user:
        logging.debug("Call get user info")
        user_no_domain = parse_ip_user(ip_user)
        username, computer, client_type, domain = get_user_gateway_info(user_no_domain)
        properties["connect_globalprotect_user"] = username
        properties["connect_globalprotect_computer_name"] = computer
        properties["connect_globalprotect_client_type"] = client_type
        properties["connect_globalprotect_domain"] = domain
        logging.debug("Computer: {}".format(computer))
        logging.debug("Client type: {}".format(client_type))
        logging.debug("Domain: {}".format(domain))
        logging.debug("User: {}".format(username))
    else:
        error_msg += "No user mapping info found. "

    if virtual_sys:
        # Get gateway name
        gateway = get_current_user_gateway(virtual_sys)
        properties["connect_globalprotect_gateway"] = gateway
        logging.debug("Gateway: {}".format(gateway))
    else:
        error_msg += "No gateway info found. "

    # Store info
    response["properties"] = properties
    if len(error_msg) > 0:
        logging.error(error_msg)
        response["error"] = error_msg + "User might be disconnected."
