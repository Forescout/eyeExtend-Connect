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
import json

url = params["connect_jamf_url"]
resolve_p_url = f"{url}/JSSResource/computermanagement/"
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

response = {}
if "dhcp_hostname_v2" in params:
    resolve_p_url = resolve_p_url + "name/" + params["dhcp_hostname_v2"]
elif "connect_globalprotect_computer_name" in params:
    resolve_p_url = resolve_p_url + "name/" + \
        params["connect_globalprotect_computer_name"]
elif "mac" in params:
    uppercase_mac = params["mac"].upper()
    colon_mac = ":".join(uppercase_mac[i:i+2] for i in range(0, 12, 2))
    resolve_p_url = resolve_p_url + "macaddress/" + colon_mac
else:
    logging.error("Insufficient information to query.")

logging.info(f"The URL is: {resolve_p_url}")

# request = urllib.request.Request(resolve_p_url)
# request.add_header("Authorization", "Basic %s" % jamf_lib.create_auth(username, password))
# request.add_header("Accept", "application/json")

try:
    # Build Request
    resolve_p_request = urllib.request.Request(resolve_p_url)
    # Add Headers
    resolve_p_request.add_header(
        "Authorization", "Basic %s" % jamf_lib.create_auth(username, password))
    resolve_p_request.add_header("Accept", "application/json")

    resolve_p_response_handle = opener.open(resolve_p_request)
    resolve_p_response = resolve_p_response_handle.read().decode("utf-8")

    request_p_object = json.loads(resolve_p_response)
    logging.debug(f"The response from Jamf is {request_p_object}")
    properties = {}
    general = request_p_object["computer_management"]
    policies = general["policies"]
    policy_list = []

    for policy in policies:
        policy_list.append(policy["name"])
        properties["connect_jamf_policies"] = policy_list
        response["properties"] = properties

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
