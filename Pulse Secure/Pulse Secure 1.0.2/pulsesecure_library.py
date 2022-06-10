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

import base64
import json
import logging
import urllib.request
from datetime import datetime

PS_URL = {
    "GET_API_KEY":
        "{}/api/v1/auth",
    "GET_ALL_ACTIVE_SESSIONS":
        "{}/api/v1/system/active-users",
    "GET_A_PARTICULAR_ACTIVE_SESSION":
        "{}/api/v1/system/active-users?name={}",
    "END_ACTIVE_SESSION":
        "{}/api/v1/system/active-users/session/{}"
}

PROTOCOL = "https"
RESPONSE_CODE_SUCCESS = 200
RESPONSE_CODE_NO_CONTENT = 204

class FSConnectPS:
    """Pulse Secure class to construct API calls and parse info methods for actions and features"""
    def set_init(self, server, username, password, ssl_context, proxy_params=None):
        """ This was intended for _init_ """
        self.server = PROTOCOL + "://" + server
        self.username = username
        self.ssl_context = ssl_context
        self.url_opener = self.build_url_opener(proxy_params)
        self.api_key = self.get_api_key(username, password)

    def get_api_key(self, username, password):
        """
        All Pulse Connect Secure requires an API key. Get the api key in this method and use it for API calls.
        Args:
            username: admin user name
            password: admin password
        Returns:
            PSAPIKey:
                api_key: Valid API Key or None
                error_msg: error message or None
        """
        url = PS_URL.get("GET_API_KEY").format(self.server)

        # As per the Pulse Secure REST API docs, set the HTTP authorization header with basic authentication using
        # the admin username/password to generate an api_key
        # JSON Response: { "api_key" : api_key_value }
        request = urllib.request.Request(url)
        request.add_header("Authorization", "Basic %s" % self.create_auth(username, password))
        request.add_header("Accept", "application/json")

        # Initialize a PSAPIKey instance to be returned
        api_key_info = PSAPIKey()
        try:
            # Try to open the request
            response = self.url_opener.open(request)

            # Extract the response code and url
            response_code = response.getcode()
            response_url = response.geturl()

            # If the response code is 200, then load the JSON response and get the value from key "api_key"
            if response_code == RESPONSE_CODE_SUCCESS:
                api_key_info.key = json.loads(response.read().decode("utf-8"))["api_key"]
                api_key_info.error_msg = None
            else:
                # Otherwise, the request failed to get a valid API key. Show response code and url for troubleshooting
                api_key_info.key = None
                api_key_info.error_msg = f"Please check credentials and URL.\nResponse Code: {response_code}\nResponse URL: {response_url}"
        except Exception as e:
            # Something went wrong with opening the request, likely due to invalid credentials
            # Set the error_msg with the exception details
            api_key_info.key = None
            api_key_info.error_msg = str(e)
            logging.error(f"Exception getting API Key: {api_key_info.error_msg}")

        # Return the API Key info
        return api_key_info

    def call_api(self, ps_cmd, arg, method):
        """
        Method makes http api calls to the Pulse Secure server and get response back
        Args:
            ps_cmd: Keys in PS_URL
            arg: Property variables to pass to the API command. Can be a dictionary
            method: The method used to make the request (GET, DELETE, etc.)
        Returns:
            APIResponse :
                http_resp_code: http request response code
                json: content in json after successful API call, otherwise None.
                exception: error details in the case of an unsuccessful API call
                is_successful: Overall status that is successful or not. Use check_success to update.
        """
        # Get the appropriate url given the ps_cmd and make a request to the url
        url = self.get_url(ps_cmd, arg)
        logging.debug(f"Making {method} request to url: {url}")

        # As per the Pulse Secure REST API docs, use the api_key value as username and password as empty
        # in the Authorization header for further access to the API
        request = urllib.request.Request(url, method=method)
        request.add_header("Authorization", "Basic %s" % self.create_auth(self.api_key.key, ""))
        request.add_header("Accept", "application/json")

        # Initialize an APIResponse instance to be returned
        api_resp = APIResponse()
        try:
            # Try to open the request
            response = self.url_opener.open(request)

            # Set the APIResponse's is_successful attribute to False first, and check again later
            api_resp.is_successful = False

            # Set the APIResponse's http_resp_code attribute
            api_resp.http_resp_code = response.getcode()

            # If the response code is 200, then load the JSON response and set the json attribute
            if api_resp.http_resp_code == RESPONSE_CODE_SUCCESS:
                json_object = json.loads(response.read().decode("utf-8"))
                api_resp.json = json_object
                # logging.debug(f"JSON: {json_object}")
            elif api_resp.http_resp_code == RESPONSE_CODE_NO_CONTENT:
                # If the response code is 204, then there will be no content (expected response for DELETE request)
                logging.info(f"No Content. Response code {api_resp.http_resp_code}")
            else:
                # Otherwise, log the response code and url for troubleshooting
                logging.error(f"Failed to get response.\nResponse Code: {api_resp.http_resp_code}\nResponse URL: {response.geturl()}")
        except Exception as e:
            # Something went wrong with opening the request
            # Set the http_resp_code to -1 to represent an error, and set the exception
            api_resp.http_resp_code = -1
            api_resp.exception = e
            logging.error(f"Exception: {e}")

        # Validate that the response was successful and then return
        api_resp.is_successful = api_resp.check_success()
        return api_resp

    def get_url(self, ps_cmd, arg):
        """
        Method construct API url base on endpoint to use and arguments
        Args:
            ps_cmd: Keys in PS_URL
            arg: Property variables to pass to the API command. vpnuser or session_id
        Returns:
            URL that can be post via HTTP request.
        """
        if ps_cmd == "GET_ALL_ACTIVE_SESSIONS":
            url = PS_URL.get("GET_ALL_ACTIVE_SESSIONS").format(self.server)
        elif ps_cmd == "GET_A_PARTICULAR_ACTIVE_SESSION":
            url = PS_URL.get("GET_A_PARTICULAR_ACTIVE_SESSION").format(self.server, arg)
        elif ps_cmd == "END_ACTIVE_SESSION":
            url = PS_URL.get("END_ACTIVE_SESSION").format(self.server, arg)
        else:
            logging.error("Invalid action getting url: " + ps_cmd)
            return ""
        return url

    def build_url_opener(self, proxy_params):
        """
        Builds a url request opener with HTTPS support, and with or without proxy server configuration
        Returns:
            OpenerDirector object with HTTPSHandler built in and ProxyHandler if there are proxy parameters to configure
        """
        # Initialize an HTTPSHandler to make all requests with ssl_context
        https_handler = urllib.request.HTTPSHandler(context=self.ssl_context)

        # If there are proxy parameters, then configure them with a ProxyHandler object
        if proxy_params is not None and proxy_params["proxy_enabled"] == "true":
            proxy_basic_auth_ip = proxy_params["proxy_basic_auth_ip"]
            proxy_port = proxy_params["proxy_port"]
            proxy_username = proxy_params["proxy_username"]
            proxy_password = proxy_params["proxy_password"]

            # If proxy_username and proxy_password are not empty, then the proxy urls will include proxy auth info
            # http://<proxy_username>:<proxy_password>@<proxy_ip>:<proxy_port>
            if proxy_username != "" and proxy_password != "":
                proxy_dict = {
                    "http": f"http://{proxy_username}:{proxy_password}@{proxy_basic_auth_ip}:{proxy_port}",
                    "https": f"https://{proxy_username}:{proxy_password}@{proxy_basic_auth_ip}:{proxy_port}"
                }
            else:
                # Otherwise, the proxy will be no-auth
                # http://<proxy_ip>:<proxy_port>
                proxy_dict = {
                    "http": f"http://{proxy_basic_auth_ip}:{proxy_port}",
                    "https": f"https://{proxy_basic_auth_ip}:{proxy_port}"
                }

            # Add the proxy_dict to a ProxyHandler object
            proxy_handler = urllib.request.ProxyHandler(proxy_dict)

            # Build the opener using the ProxyHandler and then the HTTPSHandler
            opener = urllib.request.build_opener(proxy_handler, https_handler)
            logging.debug("Built the proxy opener")
        else:
            # Otherwise build the opener without proxy configuration
            opener = urllib.request.build_opener(https_handler)
            logging.debug("Built the non-proxy opener")

        return opener

    @staticmethod
    def create_auth(username, password):
        """
        Calculate the basic authentication given the username and the password
        Args:
            username: the username (or the api_key)
            password: the password
        Returns:
            the base64 encoding of id and password
        """
        basic_auth_string = base64.b64encode(bytes('%s:%s' % (username, password), 'ascii'))
        return basic_auth_string.decode('utf-8')

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
            ori_msg += f" Error: '{msg_to_add}'"
        return ori_msg

    @staticmethod
    def convert_time_str_to_epoch_num(time_str):
        """
        Convert a time string into an epoch number that CounterACT can understand
        Args:
            time_str: string representation of a time
        Returns:
            epoch number in int type if the time string is in correct format (yyyy/mm/dd hh:mm:ss), otherwise None
        """
        try:
            epoch = int(datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S").timestamp())
            logging.debug(f"Time string '{time_str}' converted to epoch successfully. Epoch is {epoch}")
            return epoch
        except ValueError as e:
            logging.debug(f"Time string is: {time_str}. {e}")
            return None


class APIResponse:
    """
    API Response class that holds a JSON response if successful
    Returns:
        APIResponse:
            http_resp_code: http response code (200, 204, 403, etc)
            json: content in json after successful API call, otherwise None.
            exception: error details in the case of an unsuccessful API call
            is_successful: Overall status that is successful or not. Use check_success to update.
    """
    def set_init(self, http_resp_code, json, exp):
        self.http_resp_code = http_resp_code
        self.json = json
        self.exception = exp
        self.is_successful = self.check_success()

    def check_success(self):
        """
        Method to check if the response was successful
        Returns:
            True if no exception and response from API is successful. Otherwise, False.
        """
        return (self.http_resp_code is not None) and (self.http_resp_code == RESPONSE_CODE_SUCCESS or
                                                      self.http_resp_code == RESPONSE_CODE_NO_CONTENT)


class PSAPIKey:
    """
    PSAPIKey class that holds API key and error message
    Returns:
        PSAPIKey:
            key: key use for API calls.
            error_msg: error message.
    """
    def set_init(self, key, error_msg):
        self.key = key
        self.error_msg = error_msg
