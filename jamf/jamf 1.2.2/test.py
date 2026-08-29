'''
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
'''

import urllib.request
from urllib.request import HTTPError, URLError
import logging

url = params["connect_jamf_url"]
username = params["connect_jamf_username"]
password = params["connect_jamf_password"]

# Proxy support
jamf_proxy_enabled = params.get("connect_proxy_enable")
jamf_proxy_basic_auth_ip = params.get("connect_proxy_ip")
jamf_proxy_port = params.get("connect_proxy_port")
jamf_proxy_username = params.get("connect_proxy_username")
jamf_proxy_password = params.get("connect_proxy_password")

test_url = f'{url}/JSSResource/computers'
response = {}

try:
    token = params.get('connect_authorization_token')
    
    if token is not "" and token is not None:
        response["succeeded"] = True
        response["result_msg"] = "Successfully connected to Jamf."
    else:
        response["succeeded"] = False
        response["error"] = "Unable to obtain Token.\n See logs for details:\n /usr/local/forescout/plugin/connect_module/python_logs/python_server.log"
except HTTPError as e:
    response["succeeded"] = False
    response["error"] = f"Could not connect to Jamf. Response code: {e.code}"
except URLError as e:
    response["succeeded"] = False
    response["error"] = f"Could not connect to Jamf. {e.reason}"
except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["error"] = f"Could not connect to Jamf. {str(e)}"
