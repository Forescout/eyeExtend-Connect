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

url = f"{protocol}{server_url}:{port}/sepm/api/v1/identity/authenticate"
logging.debug(f"Get authentication URL: {url}")
payload = {
    "username" : username,
    "password" : password,
    "domain" : domain
}
headers = { "Content-Type" : "application/json; charset=utf-8" }

logging.debug("Starting authentication for Symantec Server")

try:
    # Create proxy server
    proxy_server = ConnectProxyServer(params)
    # Pass to use what HTTPS or HTTP or both in the protocol, pass down the ssl_context
    opener = proxy_server.get_urllib_request_https_opener(ProxyProtocol.all, ssl_context)
    auth_request = request.Request(url, headers=headers, data =json.dumps(payload).encode())
    auth_response = opener.open(auth_request)

    logging.debug("response code  : [%s]", auth_response.getcode())
    if auth_response.getcode() == 200:
        auth_response_dict = json.loads(auth_response.read())
        if auth_response_dict.get("token"):
            response["token"] = auth_response_dict["token"]
            logging.debug("Successfully retrieved Bearer token!")
        else:
            response["token"] = ""
            logging.debug("No Bearer token is available or the token is empty")
    else:
        response["token"] = ""
        logging.debug(f"Failed to get Bearer token. Could not connect to Symantec server. Error code: {auth_response.getcode()}")
except HTTPError as e:
    response["error"] = f"HTTP Error : Could not connect to Symantec server. Error code: {e.code}"
    logging.debug(f"HTTP Error : Could not connect to Symantec server. Error code: {e.code}")
except URLError as e:
    response["error"] = f"URL Error : Could not connect to Symantec server. {e.reason}"
    logging.debug(f"URL Error : Could not connect to Symantec server. {e.reason}")
except Exception as e:
    response["error"] = f"Could not connect to Symantec server. {e}"
    logging.debug( f"Could not connect to Symantec server. {e}")