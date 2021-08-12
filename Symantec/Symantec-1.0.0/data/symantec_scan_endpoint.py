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

group_id = params["connect_symantec_group_id"]
computer_id = params["connect_symantec_computer_id"]
scan_mode = params["symantec_scan_mode"]
server_url = params.get("connect_symantec_server_url")
port = params.get("connect_symantec_server_port")
protocol = "https://"
error_msg = ""
response = {}

scan_base_url = f"{protocol}{server_url}:{port}/sepm/api/v1/command-queue/{scan_mode}"
scan_filter= f"?group_ids={group_id}&computer_ids={computer_id}"
scan_url = f"{scan_base_url}{scan_filter}"
logging.debug(f"Scan URL: {scan_url}")

bearer_token = params.get("connect_authorization_token")
if bearer_token:
    try:
        #create proxy server
        proxy_server = ConnectProxyServer(params)
        opener = proxy_server.get_urllib_request_https_opener(ProxyProtocol.all, ssl_context)
        headers = { "Content-Type" : "application/json; charset=utf-8", "Authorization": "Bearer " + str(bearer_token) }
        scan_request = request.Request(scan_url, headers=headers, method="POST")
        scan_response = opener.open(scan_request)
        if scan_response.getcode() == 200:
            response["succeeded"] = True
            logging.debug("Scan endpoint action is successfully executed.")
        else:
            response["succeeded"] = False
            response["troubleshooting"] = "Failed to connect to Symantec Server."
    except HTTPError as e:
        response["succeeded"] = False
        http_error_msg = f"HTTP Error : Could not connect to Symantec server. Error code: {e.code}"
        response["troubleshooting"] = http_error_msg
        logging.debug(http_error_msg)
    except URLError as e:
        response["succeeded"] = False
        url_error_msg = f"URL Error : Could not connect to Symantec server. Reason: {e.reason}"
        response["troubleshooting"] = url_error_msg
        logging.debug(url_error_msg)
    except Exception as e:
        response["succeeded"] = False
        exp_error_msg = f"Could not connect to Symantec server. Exception: {e}"
        response["troubleshooting"] = exp_error_msg
        logging.debug(exp_error_msg)
else:
    response["succeeded"] = False
    error_msg = "No Bearer Token or No mac address to query the endpoint for."
    response["troubleshooting"] = error_msg
    logging.debug(error_msg)
