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

general_map = {
    "name": "connect_jamf_mobile_deviceName",
    "id": "connect_jamf_mobile_id"
}

composite_map = {
    "general": ["capacity", "os_type", "serial_number", "phone_number", "udid", "model", "os_version", "model_number", "os_build", "model_identifier"],
    "location": ["real_name", "email_address", "username", "phone_number", "position"],
    "purchasing": ["is_leased", "is_purchased"],
    "security": ["data_protection", "passcode_present", "passcode_compliant", "hardware_encryption", "activation_lock_enabled", "lost_mode_enabled", "lost_mode_enforced", "lost_mode_enable_issued_epoch", "jailbreak_detected"]
}


def getSubFields(json_data, prop_name):
    sub_fields_response = {}
    for property in composite_map[prop_name]:
        try:
            sub_fields_response[property] = json_data[prop_name][property]
        except:
            logging.debug(f"{property} does not exist.")
    return sub_fields_response


url = params["connect_jamf_url"]
mobile_url = f"{url}/JSSResource/mobiledevices/"
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
if "mac" in params:
    uppercase_mac = params["mac"].upper()
    colon_mac = ":".join(uppercase_mac[i:i+2] for i in range(0, 12, 2))
    mobile_url = mobile_url + "macaddress/" + colon_mac
elif "dhcp_hostname_v2" in params:
    mobile_url = mobile_url + "name/" + params["dhcp_hostname_v2"]
elif "connect_globalprotect_computer_name" in params:
    mobile_url = mobile_url + "name/" + \
        params["connect_globalprotect_computer_name"]
else:
    logging.error("Insufficient information to query.")


logging.info(f"The resolve_mobiledevices URL is: {mobile_url}")


try:
    # Build Request
    mobile_request = urllib.request.Request(mobile_url)
    # Add Headers
    token = params.get('connect_authorization_token')
    mobile_request.add_header("Authorization", f"Bearer {token}" )
    mobile_request.add_header("Accept", "application/json")

    mobile_response_handle = opener.open(mobile_request)
    mobile_response = mobile_response_handle.read().decode("utf-8")
    logging.debug(f"The response from Jamf is {mobile_response}")

    mobile_response_object = json.loads(mobile_response)["mobile_device"]

    properties = {}

    general = mobile_response_object["general"]
    for key in general_map:
        properties[general_map[key]] = general[key]
        properties["connect_jamf_mobile_asset_purchasing"] = getSubFields(
            mobile_response_object, "purchasing")
        properties["connect_jamf_mobile_user_information"] = getSubFields(
            mobile_response_object, "location")
        properties["connect_jamf_mobile_security"] = getSubFields(
            mobile_response_object, "security")

    general_subfields = getSubFields(mobile_response_object, "general")
    properties["connect_jamf_mobile_device_details"] = general_subfields
    general_subfields["serial_number"] = mobile_response_object["general"]["serial_number"]
    software_installed = []

    for application in mobile_response_object["applications"]:
        software_installed.append(application["application_name"])

    properties["connect_jamf_mobile_software_installed"] = software_installed
    properties["connect_jamf_mobile_managed"] = mobile_response_object["general"]["managed"]
    logging.debug(f"properties {properties}")
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
