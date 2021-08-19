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

from connectproxyserver import ConnectProxyServer, ProxyProtocol
from urllib import request
from urllib.request import HTTPError, URLError
import logging
import json

server_url = params.get("connect_symantec_server_url")
port = params.get("connect_symantec_server_port")
username = params.get("connect_symantec_username")
password = params.get("connect_symantec_password")
domain = params.get("connect_symantec_domain")
protocol = "https://"

response = {}

url = "{}{}:{}/sepm/api/v1/identity/authenticate".format(protocol, server_url, port)
logging.debug("Test URL: {}".format(url))
payload = {
    "username" : username,
    "password" : password,
    "domain" : domain,
}
headers = { "Content-Type" : "application/json; charset=utf-8" }

try:
    # Create proxy server
    proxy_server = ConnectProxyServer(params)
    # Pass to use what HTTPS or HTTP or both in the protocol, pass down the ssl_context
    opener = proxy_server.get_urllib_request_https_opener(ProxyProtocol.all, ssl_context)
    test_request = request.Request(url, headers=headers, data =json.dumps(payload).encode())
    test_response = opener.open(test_request)

    if test_response.getcode() == 200:
        response["succeeded"] = True
        response["result_msg"] = "Successfully connected to Symantec Server"
        logging.debug("Successfully connected to Symantec Server")
    else:
        response["succeeded"] = False
        response["result_msg"] = f"Could not connect to Symantec Server. Error code {test_response.getcode()}"
        logging.debug(f"Could not connect to Symantec server. Error code: {test_response.getcode()}")
except HTTPError as e:
    response["succeeded"] = False
    response["result_msg"] = f"HTTP Error : Could not connect to Symantec server. Error code: {e.code}"
    logging.debug(f"HTTP Error : Could not connect to Symantec server. Error code: {e.code}")
except URLError as e:
    response["succeeded"] = False
    response["result_msg"] = f"URL Error : Could not connect to Symantec server. {e.reason}"
    logging.debug(f"URL Error : Could not connect to Symantec server. {e.reason}")
except Exception as e:
    response["succeeded"] = False
    response["result_msg"] = f"Could not connect to Symantec server. {e}"
    logging.debug( f"Could not connect to Symantec server. {e}")