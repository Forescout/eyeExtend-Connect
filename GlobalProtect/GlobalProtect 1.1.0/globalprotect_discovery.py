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

# Params needed for discovery
connection = globalprotect_library.Connection()
connection.server = params.get("connect_globalprotect_server")
connection.username = params.get("connect_globalprotect_admin_username")
connection.password = params.get("connect_globalprotect_admin_password")
connection.use_syslog = params.get("connect_globalprotect_use_syslog")
connection.ssl_context = ssl_context
# Discovery can't get connect_globalprotect_firewall info since it is not defined in system.conf file

def parse_user_result(tree):
    """
    Parse the result tree and get each current user info
    :param tree: XML tree after result tag. It is a list of entry tag
    :return: Dictionary, IP as key, GPInfo as value. Can be empty
        key: ip of the end user, using virtual-ip
        value: GPInfo object
    """
    logging.debug("In parse_user_result")
    users_info = {}
    for entry in tree.findall('entry'):
        virtual_ip = entry.find("virtual-ip").text
        gp = globalprotect_library.GPInfo()
        gp.domain = entry.find("domain").text
        gp.username = entry.find("username").text
        gp.public_ip = entry.find("public-ip").text
        gp.computer = entry.find("computer").text
        gp.client_type = entry.find("client").text
        users_info[virtual_ip] = gp

    return users_info


def get_current_users():
    """
    Get current user that connected to the gateway
    Returns: GPInfo includes variables or None
        User name
        Computer name
        Client type
        User domain
        Public IP
    """
    logging.debug("In get_current_users")
    api_resp_users = connect_gp.call_api("OC_SHOW_CURRENT_USERS", "")

    # result should be a APIResponse
    if api_resp_users.is_successful:
        # <result>
        # <entry>
        # <domain>calab.forescout.com</domain>
        # <islocal>no</islocal>
        # <username>vpntest1</username>
        # <primary-username>calab.forescout.com\vpntest1</primary-username>
        # <computer>EP-S10-W7-1</computer>
        # <client>
        # Microsoft Windows 7 Ultimate Edition Service Pack 1, 64-bit
        # </client>
        # <vpn-type>Device Level VPN</vpn-type>
        # <virtual-ip>10.100.76.15</virtual-ip>
        # <virtual-ipv6>::</virtual-ipv6>
        # <public-ip>10.100.3.126</public-ip>
        # <public-ipv6>::</public-ipv6>
        # <tunnel-type>IPSec</tunnel-type>
        # <public-connection-ipv6>no</public-connection-ipv6>
        # <login-time>May.07 10:45:14</login-time>
        # <login-time-utc>1588873514</login-time-utc>
        # <lifetime>2592000</lifetime>
        # </entry>
        # <entry>
        # <domain>calab.forescout.com</domain>
        # <islocal>no</islocal>
        # <username>vpntest2</username>
        # <primary-username>calab.forescout.com\vpntest2</primary-username>
        # <computer>EP-S10-W7-2</computer>
        # <client>
        # Microsoft Windows 7 Ultimate Edition Service Pack 1, 64-bit
        # </client>
        # <vpn-type>Device Level VPN</vpn-type>
        # <virtual-ip>10.100.76.16</virtual-ip>
        # <virtual-ipv6>::</virtual-ipv6>
        # <public-ip>10.100.3.131</public-ip>
        # <public-ipv6>::</public-ipv6>
        # <tunnel-type>IPSec</tunnel-type>
        # <public-connection-ipv6>no</public-connection-ipv6>
        # <login-time>May.08 18:53:32</login-time>
        # <login-time-utc>1588989212</login-time-utc>
        # <lifetime>2592000</lifetime>
        # </entry>
        # </result>
        result_tree = api_resp_users.xml_content
        return parse_user_result(result_tree)
    else:
        logging.debug("Result tree is None")
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
endpoints = []

# Token is invalid
if token is None:
    error_msg = globalprotect_library.FSConnectGP.get_error_msg("Failed to get token.", token_error)
    response["succeeded"] = False
    # For resolve, put in error
    response["troubleshooting"] = error_msg
    logging.error(error_msg)
else:
    logging.debug("Call discovery")
    # Get current user info
    users = get_current_users()
    if users is None:
        error_msg = "Failed to get endpoint info."
        logging.debug(error_msg)
        response["troubleshooting"] = error_msg
    else:
        for ip, gp_info in users.items():
            endpoint = {}
            endpoint["ip"] = ip
            logging.debug("IP is: {}".format(ip))
            if gp_info is not None:
                properties = {}
                # gp_info is object of GPInfo
                properties["connect_globalprotect_user"] = gp_info.username
                properties["connect_globalprotect_computer_name"] = gp_info.computer
                properties["connect_globalprotect_domain"] = gp_info.domain
                properties["connect_globalprotect_public_ip"] = gp_info.public_ip
                properties["connect_globalprotect_client_type"] = gp_info.client_type
                endpoint["properties"] = properties
            endpoints.append(endpoint)
    response["endpoints"] = endpoints
