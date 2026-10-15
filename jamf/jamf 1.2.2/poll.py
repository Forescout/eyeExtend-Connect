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
import logging

jamf_to_ct_props_map = {
    "id": "connect_jamf_id",
    "managed": "connect_jamf_managed"
}

jamf_to_ct_props_mobile_map = {
    "id": "connect_jamf_mobile_id",
    "managed": "connect_jamf_mobile_managed"
}

url = params["connect_jamf_url"]

username = params["connect_jamf_username"]
password = params["connect_jamf_password"]

P_COMPUTER_POLL = params.get("connect_jamf_computer_poll", "")
logging.info(f"Computer polling is {P_COMPUTER_POLL}")
P_MOBILE_POLL = params.get("connect_jamf_mobiledevice_poll", "")
logging.info(f"Mobile polling is {P_MOBILE_POLL}")

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
endpoints = []

try:
    if P_COMPUTER_POLL == 'true':
        computer_poll_url = f"{url}/JSSResource/computers/subset/basic"
        logging.info(f"The computer URL is: {computer_poll_url}")

        # Build Request
        poll_request = urllib.request.Request(computer_poll_url)
        # Add Headers
        token = params.get('connect_authorization_token')
        poll_request.add_header("Authorization", f"Bearer {token}" )
        poll_request.add_header("Accept", "application/json")

        resolve_response_handle = opener.open(poll_request)
        logging.debug(f"The status code {resolve_response_handle.getcode()}")
        poll_response = resolve_response_handle.read().decode("utf-8")
        logging.debug(f"The poll_response {poll_response}")

        endpoint_data = json.loads(poll_response)["computers"]
        logging.debug(f"The computer devices from Jamf {endpoint_data}")

        properties = {}

        for endpoint in endpoint_data:
            new_endpoint = {}
            mac = endpoint["mac_address"]
            mac = mac.replace(":", "").lower()
            new_endpoint["mac"] = mac
            properties = {}
            for key, value in jamf_to_ct_props_map.items():
                if key in endpoint:
                    properties[value] = endpoint[key]
            new_endpoint["properties"] = properties
            endpoints.append(new_endpoint)
        logging.debug(f"computer endpoints : {endpoints}")
        # response["endpoints"] = endpoints

    # If we are polling mobile devices
    if P_MOBILE_POLL == 'true':
        mobile_poll_url = f"{url}/JSSResource/mobiledevices/subset/basic"
        logging.info(f"The mobile URL is: {mobile_poll_url}")

        # Build Request
        poll_request = urllib.request.Request(mobile_poll_url)
        # Add Headers
        token = params.get('connect_authorization_token')
        poll_request.add_header("Authorization", f"Bearer {token}" )
        poll_request.add_header("Accept", "application/json")

        resolve_response_handle = opener.open(poll_request)
        logging.debug(f"The status code {resolve_response_handle.getcode()}")
        poll_response = resolve_response_handle.read().decode("utf-8")
        logging.debug(f"The poll_response {poll_response}")

        endpoint_data = json.loads(poll_response)["mobile_devices"]
        logging.debug(f"The mobile devices from Jamf {endpoint_data}")

        properties = {}
        # endpoints = []

        for endpoint in endpoint_data:
            new_endpoint = {}
            mac = endpoint["wifi_mac_address"]
            mac = mac.replace(":", "").lower()
            new_endpoint["mac"] = mac
            properties = {}
            for key, value in jamf_to_ct_props_mobile_map.items():
                if key in endpoint:
                    properties[value] = endpoint[key]
                    # logging.debug(f"mobile value {value} : key {key}")
            new_endpoint["properties"] = properties
            endpoints.append(new_endpoint)
        logging.debug(f"mobile endpoints : {endpoints}")

    response["endpoints"] = endpoints

except HTTPError as e:
    response["succeeded"] = False
    response["error"] = f"HTTP Error : {e.code}"
except URLError as e:
    response["succeeded"] = False
    response["error"] = f"URL Error : Reason : {e.reason}"
except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["error"] = f"Exception Error : {str(e)}"
