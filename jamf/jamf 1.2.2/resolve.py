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

general_map = {
    "name": "connect_jamf_deviceName",
    "id": "connect_jamf_id"
}

composite_map = {
    "hardware": ["total_ram", "os_name", "make", "battery_capacity", "processor_speed", "model", "os_version", "processor_type", "os_build", "number_cores", "processor_architecture", "number_processors"],
    "location": ["real_name", "email_address", "username", "phone_number", "position"],
    "purchasing": ["is_leased", "is_purchased"],
    "general": ["jamf_version", "initial_entry_date_epoch", "last_contact_time_epoch"],
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
resolve_url = f'{url}/JSSResource/computers/'
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
    resolve_url = resolve_url + "macaddress/" + colon_mac
elif "dhcp_hostname_v2" in params:
    resolve_url = resolve_url + "name/" + params["dhcp_hostname_v2"]
elif "connect_globalprotect_computer_name" in params:
    resolve_url = resolve_url + "name/" + \
        params["connect_globalprotect_computer_name"]
else:
    logging.error("Insufficient information to query.")

logging.info(f"The URL is: {resolve_url}")

try:
    # Build Request
    resolve_request = urllib.request.Request(resolve_url)
    # Add Headers
    token = params.get('connect_authorization_token')
    resolve_request.add_header("Authorization", f"Bearer {token}" )
    resolve_request.add_header("Accept", "application/json")

    resolve_response_handle = opener.open(resolve_request)
    resolve_response = resolve_response_handle.read().decode("utf-8")
    logging.debug(f"The response from Jamf is {resolve_response}")

    resolve_response_object = json.loads(resolve_response)["computer"]

    # Build Properties
    properties = {}
    general = resolve_response_object["general"]
    for key in general_map:
        properties[general_map[key]] = general[key]
        properties["connect_jamf_asset_purchasing"] = getSubFields(
            resolve_response_object, "purchasing")
        properties["connect_jamf_user_information"] = getSubFields(
            resolve_response, "location")
        general_subfields = getSubFields(resolve_response_object, "general")
        try:
            general_subfields["initial_entry_date_epoch"] //= 1000
            general_subfields["last_contact_time_epoch"] //= 1000
        except:
            logging.debug("Response does not have epoch fields.")

        properties["connect_jamf_agent_information"] = general_subfields
        hardware_subfields = getSubFields(resolve_response_object, "hardware")
        hardware_subfields["serial_number"] = resolve_response_object["general"]["serial_number"]
        properties["connect_jamf_device_details"] = hardware_subfields
        software_installed = []
        for application in resolve_response_object["software"]["applications"]:
            software_installed.append(application["name"])

        properties["connect_jamf_software_installed"] = software_installed
        properties["connect_jamf_managed"] = resolve_response_object["general"]["remote_management"]["managed"]
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
