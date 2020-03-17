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
import json
import urllib.request
from base64 import b64encode

# Mapping between efficientip API response fields to Forescout properties
EFFICIENTIP_TO_PROPS_MAP = {
    "site_name": "connect_efficientip_ipam_company",
    "ip_class_name": "connect_efficientip_ipam_class",
    "parent_subnet_name": "connect_efficientip_ipam_parent_network",
    "subnet_name": "connect_efficientip_ipam_network",
    "name": "connect_efficientip_ipam_name",
    "dhcpscope_name": "connect_efficientip_dhcp_scope",
    "dhcp_name": "connect_efficientip_dhcp_server",
    "dhcp_type": "connect_efficientip_dhcp_type",
    "dhcp_version":"connect_efficientip_dhcp_version"
}

# All server configuration fields will be available in the 'params' dictionary.
URL = params["connect_efficientip_url"] # Server URL
LOGIN = params["connect_efficientip_login"]  # login
PASSWORD = params["connect_efficientip_password"]  # password
B64_LOG_PASS = b64encode(bytes('%s:%s' % (LOGIN, PASSWORD), 'ascii')) # base64(Login and password) needed for Authorization

#All url suffix that we need to retrieve properties (DHCP and IPAM)
URL_REST_API = {
    "/rest/dhcp_range_lease_list?WHERE=dhcplease_mac_addr='01:", # DHCP
    "/rest/ip_address_list?WHERE=mac_addr='" # IPAM
}

# For properties and actions defined in the 'property.conf' file, Forescout properties can be added as dependencies. These values will be
# found in the params dictionary if Forescout was able to resolve the properties. If not, they will not be found in the params dictionary.
if "mac" in params:
    # Change mac address format, xxyyzz....(FS format) to xx:yy:zz:.... (EIP format)
    MAC = ""
    MAC = ':'.join(params["mac"][i:i+2] for i in range(0, 12, 2))

    response = {}
    properties = {}
    #for each URL REST API
    for suffixe in URL_REST_API: # For run multiple URL and retrieve information to EfficientIP Server
        # Prepare API
        GET_URL = URL + suffixe + MAC + "'"
        DEVICE_HEADER = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Basic " + B64_LOG_PASS.decode('utf-8')}
        request = urllib.request.Request(GET_URL, headers=DEVICE_HEADER)
        # Call API
        r = urllib.request.urlopen(request, context=ssl_context)
        request_response = json.loads(r.read())

        # All responses from scripts must contain the JSON object 'response'. Host property resolve scripts will need to populate a
        # 'properties' JSON object within the JSON object 'response'. The 'properties' object will be a key, value mapping between the
        # Forescout property name and the value of the property.
        if request_response:
            return_values = request_response[0]
            # for each properties
            for key, value in return_values.items():
                if key in EFFICIENTIP_TO_PROPS_MAP:
                    properties[EFFICIENTIP_TO_PROPS_MAP[key]] = value
    response["properties"] = properties
else:
    response = {}
    response["error"] = "No mac address to query the endpoint"
