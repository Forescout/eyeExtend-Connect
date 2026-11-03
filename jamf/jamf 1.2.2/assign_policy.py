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
policy_name = urllib.parse.quote(params["jamf_policy"])
assign_policy_url = f"{url}/JSSResource/policies/name/{policy_name}"

logging.debug("The URL is: {assign_policy_url}")
username = params["connect_jamf_username"]
password = params["connect_jamf_password"]

# Proxy support
jamf_proxy_enabled = params.get("connect_proxy_enable")
jamf_proxy_basic_auth_ip = params.get("connect_proxy_ip")
jamf_proxy_port = params.get("connect_proxy_port")
jamf_proxy_username = params.get("connect_proxy_username")
jamf_proxy_password = params.get("connect_proxy_password")
opener = jamf_lib.handle_proxy_configuration(jamf_proxy_enabled,*-/+
                                             jamf_proxy_basic_auth_ip,
                                             jamf_proxy_port,
                                             jamf_proxy_username,
                                             jamf_proxy_password, ssl_context)

response = {}

if "dhcp_hostname_v2" in params:
    xml_body = '<policy><name>' + \
        params["jamf_policy"] + '</name><scope><computer_additions><computer>'
    computer = '<name>' + params["dhcp_hostname_v2"] + '</name>'
    xml_body += computer + '</computer></computer_additions></scope></policy>'
    logging.debug(f"Content of xml body: {xml_body}")
    xml_body = xml_body.encode("utf-8")

    try:
        request = urllib.request.Request(url, data=xml_body, method='PUT')
        token = params.get('connect_authorization_token')
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("Content-Type", "application/xml")

        # resp = urllib.request.urlopen(request, context=ssl_context)

        assign_policy_handle = opener.open(request)

        logging.info(f"Response code is {assign_policy_handle.getcode()}")
        if assign_policy_handle.getcode() >= 200 and assign_policy_handle.getcode() < 300:
            response["succeeded"] = True

    except HTTPError as e:
        response["succeeded"] = False
        response["troubleshooting"] = f"Failed action. Response code: {e.code}"
    except URLError as e:
        response["succeeded"] = False
        response["troubleshooting"] = f"Failed action. {e.reason}"
    except Exception as e:
        logging.exception(e)
        response["succeeded"] = False
        response["troubleshooting"] = f"Failed action. {str(e)}"
else:
    logging.error(
        "Adding the endpoint to the scope of the policy requires a hostname.")
    response["succeeded"] = False
    response["troubleshooting"] = "Failed action. Endpoint does not have a hostname."
