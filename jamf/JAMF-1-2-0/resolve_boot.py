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


from xml.etree import ElementTree
boot_properties = ["filevault_status", "name",
                   "size", "filevault_percent", "percentage_full"]

url = params["connect_jamf_url"]
resolve_boot_url = f"{url}/JSSResource/computers/"
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
    resolve_boot_url = resolve_boot_url + "name/" + params["dhcp_hostname_v2"]
elif "connect_globalprotect_computer_name" in params:
    resolve_boot_url = resolve_boot_url + "name/" + \
        params["connect_globalprotect_computer_name"]
elif "mac" in params:
    uppercase_mac = params["mac"].upper()
    colon_mac = ":".join(uppercase_mac[i:i+2] for i in range(0, 12, 2))
    resolve_boot_url = resolve_boot_url + "macaddress/" + colon_mac
else:
    logging.error("Insufficient information to query.")

logging.info(
    "The resolve_boot_url is: {resolve_boot_url}")

# request = urllib.request.Request(resolve_boot_url)
# request.add_header("Authorization", "Basic %s" %
#                    jamf_lib.create_auth(username, password))
# request.add_header("Accept", "application/xml")

try:
    # resp = urllib.request.urlopen(request, context=ssl_context)
    properties = {}

    # Build Request
    resolve_boot_request = urllib.request.Request(resolve_boot_url)
    # Add Headers
    resolve_boot_request.add_header("Authorization", "Basic %s" %
                                    jamf_lib.create_auth(username, password))
    resolve_boot_request.add_header("Accept", "application/xml")

    resolve_response_handle = opener.open(resolve_boot_request)
    resolve_boot_object = resolve_response_handle.read().decode("utf-8")

    tree = ElementTree.fromstring(resolve_boot_object)
    logging.debug(f"The response from Jamf is {str(tree)}")
    boot = {}

    for partition in tree.findall("hardware/storage/device/partitions/partition"):
        if partition.find("type").text == "boot":
            for prop in boot_properties:
                prop_value = partition.find(prop)
                if prop_value is not None:
                    boot[prop] = prop_value.text
    properties["connect_jamf_boot_device"] = boot
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
