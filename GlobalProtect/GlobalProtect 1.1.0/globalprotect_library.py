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

GP_ENDPOINT_PARAM = {
    "GET_TOKEN": "?type=keygen&user={}&password={}",
    "OC_SHOW_IP_USER_MAPPING":
        "?type=op&cmd=<show><user><ip-user-mapping><ip>{}</ip></ip-user-mapping></user></show>",
    "OC_SHOW_USER_GATEWAY_INFO":
        "?type=op&cmd=<show><global-protect-gateway><current-user><user>{}</user></current-user>"
        "</global-protect-gateway></show>",
    "OC_SHOW_CURRENT_USERS":
        "?type=op&cmd=<show><global-protect-gateway><current-user></current-user></global-protect-gateway></show>",
    "OC_SHOW_CURRENT_USER_GATEWAY":
        "?type=op&cmd=<show><global-protect-gateway><gateway></gateway></global-protect-gateway></show>",
    "XPATH_GET_GATEWAY":
        "?type=config&action=get&xpath=/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='{}']"
        "/global-protect/global-protect-gateway/entry/@name",
    "OC_SHOW_GATEWAY":
        "?type=op&cmd=<show><global-protect-gateway><gateway><name>{}</name></gateway></global-protect-gateway></show>",
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
        request = urllib.request.Request(url)
        result = APIResponse()
        try:
            resp = urllib.request.urlopen(request, context=self.ssl_context)
            result = FSConnectGP.parse_api_response(resp)
        except Exception as e:
            logging.error("Exception: {}".format(str(e)))
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
            user = arg.get("user", "")
            domain = arg.get("domain", "")
            computer = arg.get("computer", "")
            gateway = arg.get("gateway", "")
            if domain == "":
                param = GP_ENDPOINT_PARAM.get("REQ_CLIENT_LOGOUT_NO_DOMAIN").format(gateway, user, computer)
            else:
                param = GP_ENDPOINT_PARAM.get("REQ_CLIENT_LOGOUT").format(gateway, user, domain, computer)
        else:
            logging.warning("Invalid API requested: " + gb_cmd)
            return ""
        return self.get_uri(param)

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
            public_ip
    """
    username = ""
    computer = ""
    client_type = ""
    domain = ""
    public_ip = ""

    def set_init(self, username, computer, client_type, domain, public_ip):
        self.username = username
        self.computer = computer
        self.client_type = client_type
        self.domain = domain
        self.public_ip = public_ip


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
