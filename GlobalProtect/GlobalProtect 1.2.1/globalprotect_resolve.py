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
import urllib.parse

logging.debug("Resolve for GlobalProtect Connect App")

# Params needed for resolve
connection = globalprotect_library.Connection()
connection.server = params.get("connect_globalprotect_server")
connection.username = params.get("connect_globalprotect_admin_username")
connection.password = params.get("connect_globalprotect_admin_password")
connection.use_syslog = params.get("connect_globalprotect_use_syslog")
connection.server_from_syslog = params.get("connect_globalprotect_firewall")
connection.ssl_context = ssl_context
ip = params.get("ip")


def get_gateways():
    """
    Get all gateways in the PAN.
    :return: Set of gateway names. Could be None or empty.
    """
    logging.debug("In get_gateways")
    gateways = set()
    api_resp_user_gateway = connect_gp.call_api("OC_SHOW_GET_GATEWAY", "")
    if api_resp_user_gateway.is_successful:
        # Only return gateway names in a set
        result_tree = api_resp_user_gateway.xml_content
        entries = result_tree.findall('entry')
        for entry in entries:
            gateway_name = globalprotect_library.FSConnectGP.get_element(entry, 'gateway-name')
            logging.debug("Found gateway: {}.".format(gateway_name))
            if gateway_name:
                gateways.add(gateway_name)

        return gateways
    else:
        return None


def is_in_current_user_gateway(gateway_name, host_ip, host_user, host_domain):
    """
    Get current user gateway info
    Args:
        gateway_name: gateway to check if user has host IP in the gateway
        host_ip: host IP to check if it is in the gateway
        host_user: Use to filter hosts in the gateway
        host_domain: Optional, use to filter hosts in the gateway
    Returns:
        True if the user and host IP found in the gateway. Otherwise False.
    """
    # <entry>
    # <domain>calab.forescout.com</domain>
    # <islocal>no</islocal>
    # <username>vpntest1</username>
    # <primary-username>calab.forescout.com\vpntest1</primary-username>
    # <computer>EP-S10-W7-1</computer>
    # <client>Microsoft Windows 7 Ultimate Edition Service Pack 1, 64-bit</client>
    # <vpn-type>Device Level VPN</vpn-type>
    # <virtual-ip>10.100.76.15</virtual-ip>
    # <virtual-ipv6>::</virtual-ipv6>
    # <public-ip>10.100.3.126</public-ip>
    # <public-ipv6>::</public-ipv6>
    # <tunnel-type>IPSec</tunnel-type>
    # <public-connection-ipv6>no</public-connection-ipv6>
    # <login-time>Sep.29 14:31:20</login-time>
    # <login-time-utc>1601415080</login-time-utc>
    # <lifetime>2592000</lifetime>
    # </entry>
    # <entry>
    # <domain>calab.forescout.com</domain>
    # <islocal>no</islocal>
    # <username>vpntest1</username>
    # <primary-username>calab.forescout.com\vpntest1</primary-username>
    # <computer>EP-S10-W7-2</computer>
    # <client>Microsoft Windows 7 Ultimate Edition Service Pack 1, 64-bit</client>
    # <vpn-type>Device Level VPN</vpn-type>
    # <virtual-ip>10.100.76.10</virtual-ip>
    # <virtual-ipv6>::</virtual-ipv6>
    # <public-ip>10.100.3.131</public-ip>
    # <public-ipv6>::</public-ipv6>
    # <tunnel-type>IPSec</tunnel-type>
    # <public-connection-ipv6>no</public-connection-ipv6>
    # <login-time>Sep.29 14:31:28</login-time>
    # <login-time-utc>1601415088</login-time-utc>
    # <lifetime>2592000</lifetime>
    # </entry>
    # </result>
    logging.debug("In is_in_current_user_gateway")
    logging.debug("Check if gateway {} contains host {}".format(gateway_name, host_ip))
    # Add user, gateway and domain as filter so only hosts matched in gateway are returned
    user_gateway_param = {}
    if gateway_name:
        user_gateway_param["gateway"] = urllib.parse.quote(gateway_name)
    else:
        return False

    if host_user:
        user_gateway_param["user"] = urllib.parse.quote(host_user)
    else:
        return False

    if host_domain:
        user_gateway_param['domain'] = host_domain

    api_resp_user_gateway = connect_gp.call_api("OC_SHOW_CURRENT_USER_GATEWAY", user_gateway_param)
    # result should be a APIResponse
    if api_resp_user_gateway.is_successful:
        # Only return a string of the gateway name, not in XML format
        result_tree = api_resp_user_gateway.xml_content
        hosts = result_tree.findall('entry')
        for entry in hosts:
            virtual_ip = globalprotect_library.FSConnectGP.get_element(entry, 'virtual-ip')
            if virtual_ip and virtual_ip == host_ip:
                logging.debug("Found IP {} in gateway {} with user {}.".format(virtual_ip, gateway_name, host_user))
                return True
        logging.debug("Cannot find IP {} in gateway {}".format(host_ip, gateway_name))
        return False
    else:
        logging.debug("Cannot find IP {} in gateway {}".format(host_ip, gateway_name))
        return False


def find_current_user_gateway(host_ip, user_name, host_domain):
    """
    Go through all gateways, find if the host with user is in the gateway
    :param host_ip: Find matched host and user in the gateway
    :param user_name: Find matched user with host in the gateway
    :param host_domain: Find matched domain with host in the gateway
    :return: gateway name if he host and user is found in gateway. None if not found
    """
    gateways = get_gateways()
    if gateways:
        for gateway_name in gateways:
            if is_in_current_user_gateway(gateway_name, host_ip, user_name, host_domain):
                return gateway_name
    return None


# Init GP class
logging.debug("Init library")
connect_gp = globalprotect_library.FSConnectGP()
connect_gp.set_init(connection)

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
    ip_user, ip_type, virtual_sys = globalprotect_library.get_ip_user_mapping(connect_gp, ip)
    logging.debug("Full User: {}".format(ip_user))
    logging.debug("IP type: {}".format(ip_type))
    logging.debug("Virtual system: {}".format(virtual_sys))
    if ip_type:
        properties["connect_globalprotect_iptype"] = ip_type
    error_msg = ""
    gateway_user = None
    domain_name = None

    if ip_user:
        user_no_domain = globalprotect_library.parse_ip_user(ip_user)
        gp_info_list = globalprotect_library.get_user_gateway_info(connect_gp, user_no_domain)
        # Hash is not null and has values
        if gp_info_list and ip in gp_info_list:
            gp_info = gp_info_list[ip]
            properties["connect_globalprotect_user"] = gp_info.username
            gateway_user = gp_info.username
            properties["connect_globalprotect_computer_name"] = gp_info.computer
            properties["connect_globalprotect_client_type"] = gp_info.client_type
            properties["connect_globalprotect_domain"] = gp_info.domain
            domain_name = gp_info.domain
            properties["connect_globalprotect_public_ip"] = gp_info.public_ip
            logging.debug("Computer: {}".format(gp_info.computer))
            logging.debug("Client type: {}".format(gp_info.client_type))
            logging.debug("Domain: {}".format(gp_info.domain))
            logging.debug("User: {}".format(gp_info.username))
            logging.debug("Public IP: {}".format(gp_info.public_ip))
        else:
            error_msg += "No user gateway info found. "
    else:
        error_msg += "No user mapping info found. "

    # Find gateway name
    gateway = find_current_user_gateway(ip, gateway_user, domain_name)
    if gateway:
        properties["connect_globalprotect_gateway"] = gateway
        logging.debug("Gateway: {}".format(gateway))
    else:
        error_msg += "No gateway info found. "

    # Store info
    response["properties"] = properties

    if len(error_msg) > 0:
        logging.error(error_msg)
        response["error"] = error_msg + "User might be disconnected."
