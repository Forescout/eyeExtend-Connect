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

url = params["connect_jamf_url"]
username = params["connect_jamf_username"]
password = params["connect_jamf_password"]

# Proxy support
jamf_proxy_enabled = params.get("connect_proxy_enable")
jamf_proxy_basic_auth_ip = params.get("connect_proxy_ip")
jamf_proxy_port = params.get("connect_proxy_port")
jamf_proxy_username = params.get("connect_proxy_username")
jamf_proxy_password = params.get("connect_proxy_password")
opener = jamf_lib.handle_proxy_configuration(jamf_proxy_enabled,
                                             jamf_proxy_basic_auth_ip,
                                             jamf_proxy_port,
                                             jamf_proxy_username,
                                             jamf_proxy_password, ssl_context)

test_url = f'{url}/JSSResource/computers'
response = {}

try:
    # Build Request
    test_request = urllib.request.Request(test_url)
    # Add Headers
    test_request.add_header("Authorization", "Basic %s" %
                            jamf_lib.create_auth(username, password))
    test_request.add_header("Accept", "application/json")

    test_response_handle = opener.open(test_request)

    test_response = test_response_handle.read().decode("utf-8")
    logging.debug("JAMF Test response: " + test_response)

    response["succeeded"] = True
    response["result_msg"] = f"Successfully connected to Jamf.\n{test_response}"
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
