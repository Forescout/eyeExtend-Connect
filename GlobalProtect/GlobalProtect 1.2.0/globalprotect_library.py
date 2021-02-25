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
import urllib.request
import xml.etree.ElementTree as ElementTree
from datetime import datetime

GP_ENDPOINT_PARAM = {
    "GET_TOKEN": "?type=keygen&user={}&password={}",
    "OC_SHOW_IP_USER_MAPPING":
        "?type=op&cmd=<show><user><ip-user-mapping><ip>{}</ip></ip-user-mapping></user></show>",
    "OC_SHOW_USER_GATEWAY_INFO":
        "?type=op&cmd=<show><global-protect-gateway><current-user><user>{}</user></current-user>"
        "</global-protect-gateway></show>",
    "OC_SHOW_CURRENT_USERS":
        "?type=op&cmd=<show><global-protect-gateway><current-user></current-user></global-protect-gateway></show>",
    "OC_SHOW_CURRENT_USER_GATEWAY_NO_DOMAIN":
        "?type=op&cmd=<show><global-protect-gateway><current-user><gateway>{}</gateway><user>{}</user>"
        "</current-user></global-protect-gateway></show>",
    "OC_SHOW_CURRENT_USER_GATEWAY":
        "?type=op&cmd=<show><global-protect-gateway><current-user><gateway>{}</gateway><user>{}</user><domain>"
        "{}</domain></current-user></global-protect-gateway></show>",
    "OC_SHOW_GET_GATEWAY":
        "?type=op&cmd=<show><global-protect-gateway><gateway></gateway></global-protect-gateway></show>",
    "OC_SHOW_GATEWAY":
        "?type=op&cmd=<show><global-protect-gateway><gateway><name>{}</name></gateway></global-protect-gateway></show>",
    "OC_SHOW_HIP_REPORT":
        "?type=op&cmd=<show><user><hip-report><computer>{}</computer><ip>{}</ip><user>{}</user></hip-report></user></show>",
    "REQ_CLIENT_LOGOUT":
        "?type=op&cmd=<request><global-protect-gateway><client-logout><gateway>{}</gateway><user>{}</user>"
        "<domain>{}</domain><reason>force-logout</reason><computer>{}</computer></client-logout>"
        "</global-protect-gateway></request>",
    "REQ_CLIENT_LOGOUT_NO_DOMAIN":
        "?type=op&cmd=<request><global-protect-gateway><client-logout><gateway>{}</gateway><user>{}</user>"
        "<reason>force-logout</reason><computer>{}</computer></client-logout></global-protect-gateway></request>"
}

GP_TOKEN_FORMAT = "{}/api/{}"
GP_ENDPOINT_FORMAT = "{}/api/{}&key={}"
GP_HTTPS_FORMAT = "https://{}"

RESPONSE_CODE_SUCCESS = 200


class FSConnectGP:
    """GlobalProtect class to construct API calls and parse info methods for actions and features"""
    def set_init(self, connection):
        """ This was intended for _init_ """
        self.server = self.get_server(connection)
        logging.debug("Server is: {}".format(self.server))
        # User name is used for test connection to GP
        self.username = connection.username
        self.ssl_context = connection.ssl_context
        self.token = self.get_token(connection.username, connection.password)

    def get_token(self, username, password):
        """
        All GlobalProtect (PanOS) calls require a key token. Get the token in this method and use it for API calls.
        Args:
            username: admin user name
            password: admin password
        Returns:
            GPToken:
                token: valid token or None
                error_msg: error message or None
        """
        logging.debug("In get_token")
        # First set the url. The main one if for the actual API call. The safe one has no password, debug only.
        param = GP_ENDPOINT_PARAM.get("GET_TOKEN").format(username, password)
        safe_param = GP_ENDPOINT_PARAM.get("GET_TOKEN").format(username, "*****")
        url = GP_TOKEN_FORMAT.format(self.server, param)
        safe_url = GP_TOKEN_FORMAT.format(self.server, safe_param)
        logging.debug("Get token url = " + safe_url)
        token_info = GPToken()

        try:
            request = urllib.request.Request(url)
            resp = urllib.request.urlopen(request, context=self.ssl_context)
            response_code = resp.getcode()
            logging.debug("Get token response code: {}".format(response_code))
            if RESPONSE_CODE_SUCCESS == response_code:
                content = resp.read().decode("utf-8")
                # Content to XML parser
                root = ElementTree.fromstring(content)
                # <response status = 'success'><result><key>*******</key></result></response>
                # <response status = 'error' code = '403'><result><msg>Invalid credentials.</msg></result></response>
                status = root.attrib.get('status')
                if "success" == status:
                    token = FSConnectGP.get_element(root, 'result/key')
                    token_info.token = token
                    token_info.error_msg = None
                else:
                    error_code = content.attrib.get('code')
                    token_info.error_msg = FSConnectGP.get_element(root, 'result/msg')
                    token_info.token = None
                    logging.error(
                        "Failed to get token. Error code: {}. Message: {}".format(error_code, token_info.error_msg))
        except Exception as exp:
            token_info.token = None
            token_info.error_msg = str(exp)
            logging.warning("Got exception pulling token: " + str(exp))
            logging.exception(exp)

        # Return None token, since empty could be a token
        return token_info

    def call_api(self, gb_cmd, arg):
        """
        Method makes http api calls to the GlobalProtect server and get response back
        Args:
            gb_cmd: Keys in GP_ENDPOINT_PARAM
            arg: Property variables to pass to the API command. Can be a dictionary
        Returns:
            APIResponse :
                http_resp_code: http request response code
                api_status: ResponseStatus,
                xml_content: content in ElementTree after result tag for success, otherwise None.
                is_successful: True when HTTP call and response status are successful, otherwise, False.
        """
        url = self.get_url(gb_cmd, arg)
        # When requests is available, can use requote_uri, from requests.utils import requote_uri
        # url = requote_uri(ori_url)
        request = urllib.request.Request(url)
        result = APIResponse()
        try:
            resp = urllib.request.urlopen(request, context=self.ssl_context)
            result = FSConnectGP.parse_api_response(resp)
        except Exception as e:
            logging.error("Exception: {}".format(str(e)))
            logging.exception(e)
            result.http_resp_code = -1
            result.exception = e

        # Overall status
        result.is_successful = result.check_success()
        return result

    def get_url(self, gb_cmd, arg):
        """
        Method construct API url base on endpoint to use and arguments
        Args:
            gb_cmd: Keys in GP_ENDPOINT_PARAM
            arg: Property variables to pass to the API command. Can be a dictionary
        Returns:
            URL that can be post via HTTP request.
        """
        logging.debug("In get_url")
        if "OC_SHOW_SYSTEM_INFO" == gb_cmd:
            param = GP_ENDPOINT_PARAM.get("OC_SHOW_SYSTEM_INFO")
        elif "OC_SHOW_IP_USER_MAPPING" == gb_cmd:
            param = GP_ENDPOINT_PARAM.get("OC_SHOW_IP_USER_MAPPING").format(arg)
        elif "OC_SHOW_USER_GATEWAY_INFO" == gb_cmd:
            param = GP_ENDPOINT_PARAM.get("OC_SHOW_USER_GATEWAY_INFO").format(arg)
        elif "OC_SHOW_GATEWAY" == gb_cmd:
            param = GP_ENDPOINT_PARAM.get("OC_SHOW_GATEWAY").format(arg)
        elif "XPATH_GET_GATEWAY" == gb_cmd:
            param = GP_ENDPOINT_PARAM.get("XPATH_GET_GATEWAY").format(arg)
        elif "OC_SHOW_CURRENT_USERS" == gb_cmd:
            param = GP_ENDPOINT_PARAM.get("OC_SHOW_CURRENT_USERS")
        elif "REQ_CLIENT_LOGOUT" == gb_cmd:
            param = self.get_param_request_client_logout(arg)
        elif "OC_SHOW_GET_GATEWAY" == gb_cmd:
            param = GP_ENDPOINT_PARAM.get("OC_SHOW_GET_GATEWAY")
        elif "OC_SHOW_CURRENT_USER_GATEWAY" == gb_cmd:
            param = self.get_param_show_current_user_gateway(arg)
        elif "OC_SHOW_HIP_REPORT" == gb_cmd:
            param = self.get_param_show_hip_report(arg)
        else:
            logging.warning("Invalid API requested: " + gb_cmd)
            return ""
        return self.get_uri(param)

    def get_param_show_hip_report(self, arg):
        computer = arg.get("computer", "")
        ip = arg.get("ip", "")
        user = arg.get("user", "")
        param = GP_ENDPOINT_PARAM.get("OC_SHOW_HIP_REPORT").format(computer, ip, user)
        return param

    def get_param_request_client_logout(self, arg):
        user = arg.get("user", "")
        domain = arg.get("domain", "")
        computer = arg.get("computer", "")
        gateway = arg.get("gateway", "")
        if domain == "":
            param = GP_ENDPOINT_PARAM.get("REQ_CLIENT_LOGOUT_NO_DOMAIN").format(gateway, user, computer)
        else:
            param = GP_ENDPOINT_PARAM.get("REQ_CLIENT_LOGOUT").format(gateway, user, domain, computer)
        return param

    def get_param_show_current_user_gateway(self, arg):
        user = arg.get("user", "")
        gateway = arg.get("gateway", "")
        domain = arg.get("domain", "")
        if domain:
            param = GP_ENDPOINT_PARAM.get("OC_SHOW_CURRENT_USER_GATEWAY").format(gateway, user, domain)
        else:
            param = GP_ENDPOINT_PARAM.get("OC_SHOW_CURRENT_USER_GATEWAY_NO_DOMAIN").format(gateway, user)
        return param

    def get_uri(self, param):
        """
        Method construct API url base on endpoint to use and arguments
        Args:
            param: Param used to put in to the endpoint format
        Returns:
            URL that can be post via HTTP request.
        """
        url = GP_ENDPOINT_FORMAT.format(self.server, param, self.token.token)
        safe_url = GP_ENDPOINT_FORMAT.format(self.server, param, "******")
        logging.debug("API URL = " + safe_url)
        return url

    @staticmethod
    def parse_xml_content(content):
        """
        Parse string to ElementTree
        Args:
            content: string that is well-formed XML
        Returns:
            ElementTree
        """
        return ElementTree.fromstring(content)

    @staticmethod
    def parse_status_with_error_ele(response_tree):
        """
        Method is specifically to parse disconnect user api which returns another layer of response and status
        Mainly parsing status attribute and error element in it.
        ## Error case
        # <response status="success">
        # <result>
        # <response status="error">
        # <gateway>GatewayName</gateway>
        # <user>User1</user>
        # <computer>ComputerName</computer>
        # <error>Invalid user name</error>
        # </response>
        # </result>
        # </response>
        ## Success case
        # <response status="success">
        # <result>
        # <response status="success">
        # <gateway>GatewayName</gateway>
        # <user>User1</user>
        # <computer>ComputerName</computer>
        # <saml-session-index/>
        # <saml-name-id/>
        # </response>
        # </result>
        # </response>
        Args:
            response_tree: ElementTree on second level response node, in this case, as the following
            # <response status="error">
            # <gateway>GatewayName</gateway>
            # <user>User1</user>
            # <computer>ComputerName</computer>
            # <error>Invalid user name</error>
            # </response>
        Returns:
            ResponseStatus:
                status: status attribute
                error_msg: content of error tag or empty string
        """
        response_status = ResponseStatus()
        # Content is ElementTree that has response as the first level node
        response_status.status = response_tree.find('response').get('status')
        # Only on error status, there is error message
        response_status.error_msg = FSConnectGP.get_element(response_tree, 'response/error')
        return response_status

    '''Parse status of the response. If status is not "success", an error attribute might contains the info
       however, the error format return is not consistent through out APIs. Sometimes, it has msg as error meg
       sometimes, it has an error code. Here we only get the attribute error. If none, then msg return empty string  
    '''
    @staticmethod
    def parse_response_status(response_tree):
        """
        Parse API response and get status or error. Both are from attributes.
        <response status="success"><result>content</result></response>
        <response status="error" error="User not found"><result>content</result></response>
        Args:
            response_tree: http response content
        Returns:
            ResponseStatus :
                status: status from attribute 'status'.
                error_msg: attribute from 'error'.
        """
        # Content is ElementTree that has response as the first level node
        status = response_tree.attrib.get('status')
        # Only on error status, there is error message
        msg = response_tree.attrib.get('error', "")
        response_status = ResponseStatus()
        response_status.set_init(status, msg)
        return response_status

    @staticmethod
    def parse_api_response(response):
        """
        Parse API response from GlobalProtect server. This is call after HTTP call to the server is successful.
        HTTP response code is saved in http_resp_code, data is
        Args:
            response: http response content
        Returns:
            APIResponse :
                http_resp_code: http request response code
                api_status: ResponseStatus,
                xml_content: content in ElementTree after result tag for success, otherwise None.
                is_successful: False by default, the calling method will set this base on the overall status.
        """
        api_resp = APIResponse()
        api_resp.is_successful = False
        api_resp.http_resp_code = response.getcode()
        logging.debug("Response code is: {}".format(api_resp.http_resp_code))
        if RESPONSE_CODE_SUCCESS == api_resp.http_resp_code:
            data = ""
            while True:
                # There is pagination on the response data
                content = response.read().decode("utf-8")
                if content is None or content == "":
                    break
                data += content
            logging.debug("Data is: {}".format(data))
            root = FSConnectGP.parse_xml_content(data)
            api_resp.api_status = FSConnectGP.parse_response_status(root)
            logging.debug("Return status: {}".format(api_resp.api_status.status))
            logging.debug("Return error: {}".format(api_resp.api_status.error_msg))
            if 'success' == api_resp.api_status.status:
                result_tree = root.find('result')
                api_resp.xml_content = result_tree
            else:
                if api_resp.api_status.error_msg:
                    logging.debug("API call returned error: {}".format(api_resp.api_status.error_msg))
        else:
            if api_resp.http_resp_code:
                logging.error("API call returned error: {}".format(api_resp.http_resp_code))

        return api_resp

    @staticmethod
    def get_element(tree, ele_to_find):
        """
        Find element and get its text
        Args:
            tree: ElementTree
            ele_to_find: string of element path from the root, such as 'entry/gateway' for example
        Returns:
            element text if found otherwise, empty string
        """
        element_text = ""
        element = tree.find(ele_to_find)
        if element is not None:
            element_text = element.text
        return element_text

    @staticmethod
    def get_error_msg(ori_msg, msg_to_add):
        """
        Concat message in a certain format: original message + Error: 'new message'
        Args:
            ori_msg: Original message
            msg_to_add: message to add to as error.
        Returns:
            original message + Error: 'message to add'
        """
        if msg_to_add:
            ori_msg += " Error: '{}'".format(str(msg_to_add))
        return ori_msg

    def get_server(self, connection):
        """
        Get serer string. Check if use syslog is true, use serer_from_syslog. Otherwise,
        or if server_from_syslog is empty, server provided in the panel is used.
        :param connection: Server provided in the panel.
        :return: GP server name in "https://<server> format
        """
        logging.debug("Use Syslog: {}".format(connection.use_syslog))
        if connection.use_syslog and connection.server_from_syslog:
            return GP_HTTPS_FORMAT.format(connection.server_from_syslog)
        return connection.server


class APIResponse:
    """
    API Response class that holds ElementTree and response status
    Returns:
        APIResponse:
            http_resp_code: http request response code
            api_status: ResponseStatus,
            xml_content: content in ElementTree after result tag for success, otherwise None.
            is_successful: Overall status that is successful or not. Use check_success to update.
    """
    def set_init(self, http_resp_code, result, exp):
        # This is the http response code, 200 or 403, etc
        self.http_resp_code = http_resp_code
        self.xml_content = result
        self.exception = exp
        # This is the api response status, successful or not, since http can be successful but api return error
        self.api_status = FSConnectGP.parse_response_status(result)
        self.is_successful = self.check_success()

    def check_success(self):
        """
        Method to check if response is a success
        Returns:
            True if no exception and response from API is successful. Otherwise, False.
        """
        return (self.http_resp_code is not None) and (RESPONSE_CODE_SUCCESS == self.http_resp_code) and \
               (self.api_status is not None) and (self.api_status.status is not None) and \
               ('success' == self.api_status.status)


class ResponseStatus:
    """
    ResponseStatus class that holds status and error message
    Returns:
        ResponseStatus:
            status: status
            error_msg: error message
    """
    def set_init(self, status, error_msg):
        self.status = status
        self.error_msg = error_msg


class GPToken:
    """
    GPToken class that holds token and error message
    Returns:
        GPToken:
            token: token use for API calls.
            error_msg: error message.
    """
    def set_init(self, token, error_msg):
        self.token = token
        self.error_msg = error_msg


class GPInfo:
    """
    GPInfo class holds GP info for resolve
    Returns:
        GPInfo:
            username,
            computer,
            client type,
            domain,
            public_ip,
            virtual_ip
    """
    username = ""
    computer = ""
    client_type = ""
    domain = ""
    public_ip = ""
    virtual_ip = ""

    def set_init(self, username, computer, client_type, domain, public_ip, virtual_ip):
        self.username = username
        self.computer = computer
        self.client_type = client_type
        self.domain = domain
        self.public_ip = public_ip
        self.virtual_ip = virtual_ip


class Connection:
    server = ""
    username = ""
    ssl_context = ""
    use_syslog = False
    server_from_syslog = None
    password = ""

    def set_init(self, server, server_from_syslog, username, password, ssl_context, use_syslog):
        self.server = server
        self.username = username
        self.ssl_context = ssl_context
        self.use_syslog = use_syslog
        self.server_from_syslog = server_from_syslog
        self.password = password


class GPHipReport:
    """
    GPHipReport class holds GP hip information for resolve
    Returns:
        GPHipReport:
            anti_malware:
                list(
                {
                    vendor
                    name
                    version
                    rtp
                    last_full_scan_time
                })
            disk_backup:
                list(
                {
                    vendor
                    name
                    version
                    last_backup_time
                })
            disk_encryption:
                list(
                {
                    vendor
                    name
                    version
                    drive
                    state
                })
            firewall:
                list(
                {
                    vendor
                    name
                    version
                    is_enabled
                })
            patch_mgmt:
                list(
                {
                    vendor
                    name
                    version
                    is_enabled
                })
            missing_patches:
                list(
                {
                    vendor
                    title
                    severity
                    category
                })
    """
    anti_malware = []
    disk_backup = []
    disk_encryption = []
    firewall = []
    patch_mgmt = []
    missing_patches = []

    def set_init(self, anti_malware, disk_backup, disk_encryption, firewall, patch_mgmt, missing_patches):
        self.anti_malware = anti_malware
        self.disk_backup = disk_backup
        self.disk_encryption = disk_encryption
        self.firewall = firewall
        self.patch_mgmt = patch_mgmt
        self.missing_patches = missing_patches


def get_ip_user_mapping(connect_gp, ip):
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
        # There is multiple entries or one entry
        user_from_ip = FSConnectGP.get_element(result_tree, 'entry/user')
        logging.debug("Get user: {}".format(user_from_ip))
        type_from_ip = FSConnectGP.get_element(result_tree, 'entry/type')
        logging.debug("Get IP type: {}".format(type_from_ip))
        vsys_from_ip = FSConnectGP.get_element(result_tree, 'entry/vsys')
        logging.debug("Get location: {}".format(vsys_from_ip))
        return user_from_ip, type_from_ip, vsys_from_ip
    else:
        return "", "", ""


def get_user_gateway_info(connect_gp, info_user):
    """
    Get user gateway information
    Returns: List of GPInfo in hash. Key is the public IP and value is the GP info which includes variables or None
        User name
        Computer name
        Client type
        User domain
        Public IP
    """
    logging.debug("In get_user_gateway_info")
    api_resp_user_info = connect_gp.call_api("OC_SHOW_USER_GATEWAY_INFO", info_user)

    # result should be a APIResponse
    if api_resp_user_info.is_successful:
        # <response status="success">
        # <result>
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
        # <login-time>Sep.25 12:29:46</login-time>
        # <login-time-utc>1601062186</login-time-utc>
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
        # <login-time>Sep.25 12:31:30</login-time>
        # <login-time-utc>1601062290</login-time-utc>
        # <lifetime>2592000</lifetime>
        # </entry>
        # </result>
        # </response>
        # Error case
        # <response status="error" code="17"><msg><line>
        # <![CDATA[ show -> global-protect-gateway -> current-user -> user is invalid]]></line></msg></response>
        result_tree = api_resp_user_info.xml_content
        gp_infos = {}
        # There are multiple entries or one entry
        for entry in result_tree.findall('entry'):
            gp_info = GPInfo()
            # logging.debug("Entry is: {}".format(entry.tostring()))
            gp_info.computer = FSConnectGP.get_element(entry, 'computer')
            logging.debug("Get computer: {}".format(gp_info.computer))
            gp_info.public_ip = FSConnectGP.get_element(entry, 'public-ip')
            logging.debug("Get public IP: {}".format(gp_info.public_ip))
            gp_info.client_type = FSConnectGP.get_element(entry, 'client')
            logging.debug("Get client type: {}".format(gp_info.client_type))
            gp_info.username = FSConnectGP.get_element(entry, 'username')
            logging.debug("Get user name: {}".format(gp_info.username))
            gp_info.domain = FSConnectGP.get_element(entry, 'domain')
            logging.debug("Get domain: {}".format(gp_info.domain))
            gp_info.virtual_ip = FSConnectGP.get_element(entry, 'virtual-ip')
            logging.debug("Get virtual IP: {}".format(gp_info.virtual_ip))
            # virtual ip is not None and has value. This match to the params["ip"]
            if gp_info.virtual_ip:
                gp_infos[gp_info.virtual_ip] = gp_info
                logging.debug("Assigning info to IP: {}".format(gp_info.virtual_ip))
            else:
                # Even assign the value, for disconnect user, virtual_ip is used.
                gp_infos[gp_info.public_ip] = gp_info
                logging.error("Virtual IP is empty.")
        return gp_infos
    else:
        return None


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


def get_prod_info(tree, attr):
    """
    Get attribute value of <Prod> element
    Args:
        tree: element where the attribute belongs to ('ProductInfo/Prod')
        attr: attribute name
    Returns:
        value of the attribute
    """
    return tree.find("ProductInfo/Prod").get(attr)


def convert_time_str_to_epoch_num(time_str):
    """
    Convert time from string type to epoch number
    Args: str
        time_str: time in string type
    Returns:
        epoch number in int type if the time string is in correct format (mm/dd/yyyy hh:mm:ss) else None
    """
    try:
        epoch = int(datetime.strptime(time_str, '%m/%d/%Y %H:%M:%S').timestamp())
        logging.debug('Time string "{}" converted to epoch successfully'.format(time_str))
        return epoch
    except ValueError as e:
        logging.info('Time string is: {}. {}'.format(time_str, e))
        return None


def get_hip_anti_malware_info(hip_anti_malware_list):
    """
    Args:
        hip_anti_malware_list: Element instance or None, path to the list of anti-malware products
    Returns:
        List of dictionaries. Each dictionary contains information about each anti-malware product such as name, vendor, version, rtp and last full scan time (optional)
        Return empty list if hip_anti_malware_list is None or no products found
    """
    # <entry name="anti-malware">
    # <list>
    # <entry>
    # <ProductInfo>
    # <Prod vendor="Malwarebytes Corporation" name="Malwarebytes Anti-Malware" version="4.1.2.73" defver="2020.04.08.28" engver="1.13.4.186" datemon="8" dateday="18" dateyear="2020" prodType="3" osType="1"/>
    # <real-time-protection>n/a</real-time-protection>
    # <last-full-scan-time>04/08/2020 10:25:15</last-full-scan-time>
    # </ProductInfo>
    # </entry>
    # <entry>
    # <ProductInfo>
    # <Prod vendor="CrowdStrike, Inc." name="CrowdStrike Falcon" version="5.36.11809.0" defver="2020.09.10" engver="5.36.11809.0" datemon="9" dateday="10" dateyear="2020" prodType="3" osType="1"/>
    # <real-time-protection>yes</real-time-protection>
    # <last-full-scan-time>n/a</last-full-scan-time>
    # </ProductInfo>
    # </entry>
    # </list>
    # </entry>
    anti_malware_list = []
    if hip_anti_malware_list:
        for entry in hip_anti_malware_list:
            product_info = dict()
            product_info['connect_globalprotect_HIP_anti_malware_name'] = get_prod_info(entry, 'name')
            product_info['connect_globalprotect_HIP_anti_malware_version'] = get_prod_info(entry, 'version')
            product_info['connect_globalprotect_HIP_anti_malware_vendor'] = get_prod_info(entry, 'vendor')
            product_info['connect_globalprotect_HIP_anti_malware_rtp'] = FSConnectGP.get_element(entry, 'ProductInfo/real-time-protection')
            scan_time_str = FSConnectGP.get_element(entry, 'ProductInfo/last-full-scan-time')
            scan_time_epoch = convert_time_str_to_epoch_num(scan_time_str)
            if scan_time_epoch:
                product_info['connect_globalprotect_HIP_anti_malware_scan_time'] = scan_time_epoch
            anti_malware_list.append(product_info)
            logging.debug("Get anti-malware product info: {}".format(anti_malware_list[-1]))
    return anti_malware_list


def get_hip_disk_backup_info(hip_disk_backup_list):
    """
    Args:
        hip_disk_backup_list: Element instance or None, path to the list of disk backup products
    Returns:
        List of dictionaries. Each dictionary contains information about each disk backup product such as name, version, vendor and last backup time (optional)
        Return empty list if hip_disk_backup_list is None or no products found
    """
    # <entry name="disk-backup">
    # <list>
    # <entry>
    # <ProductInfo>
    # <Prod vendor="Symantec Corporation" name="Norton 360" version="22.20.5.39"/>
    # <last-backup-time>n/a</last-backup-time>
    # </ProductInfo>
    # </entry>
    # <entry>
    # <ProductInfo>
    # <Prod vendor="Microsoft Corporation" name="Windows Backup and Restore" version="10.0.18362.1"/>
    # <last-backup-time>n/a</last-backup-time>
    # </ProductInfo>
    # </entry>
    # </list>
    # </entry>
    # </list>
    # </entry>
    disk_backup_list = []
    if hip_disk_backup_list:
        for entry in hip_disk_backup_list:
            product_info = dict()
            product_info['connect_globalprotect_HIP_disk_backup_name'] = get_prod_info(entry, 'name')
            product_info['connect_globalprotect_HIP_disk_backup_version'] = get_prod_info(entry, 'version')
            product_info['connect_globalprotect_HIP_disk_backup_vendor'] = get_prod_info(entry, 'vendor')
            backup_time_str = FSConnectGP.get_element(entry, 'ProductInfo/last-backup-time')
            backup_time_epoch = convert_time_str_to_epoch_num(backup_time_str)
            if backup_time_epoch:
                product_info['connect_globalprotect_HIP_disk_backup_time'] = backup_time_epoch
            disk_backup_list.append(product_info)
            logging.debug('Get disk-backup product info: {}'.format(disk_backup_list[-1]))
    return disk_backup_list


def get_hip_disk_encryption_info(hip_disk_encryption_list):
    """
    Args:
        hip_disk_encryption_list: Element instance or None, path to the list of disk encryption products
    Returns:
        List of dictionaries. Each dictionary contains information about each disk encryption product such as name, vendor, version and encryption drives(optional)
        Return empty list if hip_disk_encryption_list is None or no products found
    """
    # <entry name="disk-encryption">
    # <list>
    # <entry>
    # <ProductInfo>
    # <Prod vendor="Microsoft Corporation" name="Windows Device Encryption" version="10.0.18362.1"/>
    # <drives>
    # <entry>
    # <drive-name>C:\</drive-name>
    # <enc-state>unencrypted</enc-state>
    # </entry>
    # <entry>
    # <drive-name>D:\</drive-name>
    # <enc-state>unencrypted</enc-state>
    # </entry>
    # <entry>
    # <drive-name>E:\</drive-name>
    # <enc-state>unencrypted</enc-state>
    # </entry>
    # </drives>
    # </ProductInfo>
    # </entry>
    # </list>
    # </entry>
    disk_encryption_list = []
    if hip_disk_encryption_list:
        for entry in hip_disk_encryption_list:
            product_info = dict()
            product_info['connect_globalprotect_HIP_disk_encryption_vendor'] = get_prod_info(entry, 'vendor')
            product_info['connect_globalprotect_HIP_disk_encryption_name'] = get_prod_info(entry, 'name')
            product_info['connect_globalprotect_HIP_disk_encryption_version'] = get_prod_info(entry, 'version')
            drive_list = entry.findall('ProductInfo/drives/entry')
            if drive_list: #there is drive information
                for sub_entry in drive_list:
                    product_info['connect_globalprotect_HIP_disk_encryption_drive'] = FSConnectGP.get_element(sub_entry, 'drive-name')
                    product_info['connect_globalprotect_HIP_disk_encryption_state'] = FSConnectGP.get_element(sub_entry, 'enc-state')
                    #have to use a product_info copy here as there could be multiple drives or multiple (drive-name, enc-state) pairs
                    #these values of product_info will be overwritten if we
                    disk_encryption_list.append(product_info.copy())
                    logging.debug('Get disk-encryption product info: {}'.format(disk_encryption_list[-1]))
            else:
                disk_encryption_list.append(product_info)
                logging.debug('Get disk-encryption product info: {}'.format(disk_encryption_list[-1]))
    return disk_encryption_list


def get_hip_firewall_info(hip_firewall_list):
    """
    Args:
        hip_firewall_list: Element instance or None, path to the list of firewall products
    Returns:
        List of dictionaries. Each dictionary contains information about each firewall product such as name, vendor, version and is_enabled
        Return empty list if hip_per_category_list is None or no products found
    """
    # <entry name="firewall">
    # <list>
    # <entry>
    # <ProductInfo>
    # <Prod vendor="Microsoft Corporation" name="Windows Firewall" version="10.0.18362.1"/>
    # <is-enabled>no</is-enabled>
    # </ProductInfo>
    # </entry>
    # <entry>
    # <ProductInfo>
    # <Prod vendor="Symantec Corporation" name="Norton 360" version="22.20.5.39"/>
    # <is-enabled>yes</is-enabled>
    # </ProductInfo>
    # </entry>
    # </list>
    # </entry>
    firewall_list = []
    if hip_firewall_list:
        for entry in hip_firewall_list:
            product_info = dict()
            product_info['connect_globalprotect_HIP_firewall_vendor'] = get_prod_info(entry, 'vendor')
            product_info['connect_globalprotect_HIP_firewall_name'] = get_prod_info(entry, 'name')
            product_info['connect_globalprotect_HIP_firewall_version'] = get_prod_info(entry, 'version')
            product_info['connect_globalprotect_HIP_firewall_enabled'] = FSConnectGP.get_element(entry,'ProductInfo/is-enabled')
            firewall_list.append(product_info)
            logging.debug('Get firewall product info: {}'.format(firewall_list[-1]))
    return firewall_list


def get_hip_patch_management_info(hip_patch_mgmt_list):
    """
    Args:
        hip_patch_mgmt_list: Element instance or None, path to the list of patch management products
    Returns:
        List of dictionaries. Each dictionary contains information about each patch management product such as name, vendor, version and is_enabled
        Return empty list if hip_per_category_list is None or no products found
    """
    # <entry name="patch-management">
    # <list>
    # <entry>
    # <ProductInfo>
    # <Prod vendor="Microsoft Corporation" name="Windows Update Agent" version="10.0.18362.836"/>
    # <is-enabled>yes</is-enabled>
    # </ProductInfo>
    # </entry>
    # </list>
    # </entry>
    patch_mgmt_list = []
    if hip_patch_mgmt_list:
        for entry in hip_patch_mgmt_list:
            product_info = dict()
            product_info['connect_globalprotect_HIP_patch_mgmt_vendor'] = get_prod_info(entry, 'vendor')
            product_info['connect_globalprotect_HIP_patch_mgmt_name'] = get_prod_info(entry, 'name')
            product_info['connect_globalprotect_HIP_patch_mgmt_version'] = get_prod_info(entry, 'version')
            product_info['connect_globalprotect_HIP_patch_mgmt_enabled'] = FSConnectGP.get_element(entry, 'ProductInfo/is-enabled')
            patch_mgmt_list.append(product_info)
            logging.debug('Get patch-management product info: {}'.format(patch_mgmt_list[-1]))
    return patch_mgmt_list


def get_hip_missing_patches_info(hip_mp_list):
    """
    Args:
        hip_mp_list: Element instance or None, path to the list of missing patches
    Returns:
        List of dictionaries. Each dictionary contains information about each missing patch such as vendor, title, severity and category
        Return empty list if hip_mp_list is None or no missing patches found
    """
    # <entry name="patch-management">
    # <missing-patches>
    # <entry>
    # <title>2020-09 Cumulative Update for Windows 10 Version 1903 for x64-based Systems (KB4574727)</title>
    # <description>Install this update to resolve issues in Windows...</description>
    # <product></product>
    # <vendor>Microsoft Corporation</vendor>
    # <info-url></info-url>
    # <kb-article-id>4574727</kb-article-id>
    # <security-bulletin-id></security-bulletin-id>
    # <severity>2</severity>
    # <category>security_update</category>
    # <is-installed>no</is-installed>
    # </entry>
    # </missing-patches>
    # </entry>
    missing_patches_list = []
    if hip_mp_list:
        for entry in hip_mp_list:
            product_info = dict()
            product_info['connect_globalprotect_HIP_mp_vendor'] = FSConnectGP.get_element(entry, 'vendor')
            product_info['connect_globalprotect_HIP_mp_title'] = FSConnectGP.get_element(entry, 'title')
            product_info['connect_globalprotect_HIP_mp_severity'] = FSConnectGP.get_element(entry, 'severity')
            product_info['connect_globalprotect_HIP_mp_category'] = FSConnectGP.get_element(entry, 'category')
            missing_patches_list.append(product_info)
            logging.debug('Get missing patches product info: {}'.format(missing_patches_list[-1]))
    return missing_patches_list
