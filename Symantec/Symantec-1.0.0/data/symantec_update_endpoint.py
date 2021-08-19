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
server_url = params.get("connect_symantec_server_url")
port = params.get("connect_symantec_server_port")
protocol = "https://"
response = {}

update_base_url = f"{protocol}{server_url}:{port}/sepm/api/v1/command-queue/updatecontent"
update_filter = f"?computer_ids={computer_id}&group_ids={group_id}"
update_url = f"{update_base_url}{update_filter}"
logging.debug(f"Update URL: {update_url}")
payload = {
    "computer_ids" : computer_id,
    "group_ids" : group_id
}
bearer_token = params.get("connect_authorization_token")

if bearer_token:
    try:
        #create proxy server
        proxy_server = ConnectProxyServer(params)
        opener = proxy_server.get_urllib_request_https_opener(ProxyProtocol.all, ssl_context)
        headers = { "Content-Type" : "application/json; charset=utf-8", "Authorization": "Bearer " + str(bearer_token) }
        update_request = request.Request(update_url, headers=headers, method="POST")
        update_response = opener.open(update_request)
        if update_response.getcode() == 200:
            response["succeeded"] = True
            logging.debug("Update endpoint action is successfully executed.")
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
        url_error_msg = f"URL Error : Could not connect to Symantec server. {e.reason}"
        response["troubleshooting"] = url_error_msg
        logging.debug(url_error_msg)
    except Exception as e:
        response["succeeded"] = False
        exp_error_msg = f"Could not connect to Symantec server. {e}"
        response["troubleshooting"] = exp_error_msg
        logging.debug(exp_error_msg)
else:
    response["succeeded"] = False
    error_msg = "No Bearer Token or No mac address to query the endpoint for."
    response["troubleshooting"] = error_msg
    logging.debug(error_msg)
