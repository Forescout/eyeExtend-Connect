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
import re

# Mapping between efficientip API response fields to Forescout properties
EFFICIENTIP_TO_PROPS_MAP = {
    "site_name": "connect_efficientip_ipam_company",
    "ip_class_name": "connect_efficientip_ipam_class",
    "parent_subnet_name": "connect_efficientip_ipam_parent_network",
    "subnet_name": "connect_efficientip_ipam_network",
    "mac_addr": "connect_efficientip_ipam_mac",
    "name": "connect_efficientip_ipam_name",
    "tree_path":"connect_efficientip_ipam_tree_path",
    "pool_name": "connect_efficientip_ipam_pool_name"
}

# All server configuration fields will be available in the 'params' dictionary.
URL = params["connect_efficientip_url"] # Server URL
LOGIN = params["connect_efficientip_login"]  # login
PASSWORD = params["connect_efficientip_password"]  # password
B64_LOG_PASS = b64encode(bytes('%s:%s' % (LOGIN, PASSWORD), 'ascii')) # base64(Login and password) needed for Authorization

# Prepare API
GET_URL = URL + "/rest/ip_address_list?WHERE=type='ip'" #  URL retrieve all endpoint (except free space, gtw, network)
DEVICE_HEADER = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Basic " + B64_LOG_PASS.decode('utf-8')}
REQUEST = urllib.request.Request(GET_URL, headers=DEVICE_HEADER)

# Call API
R = urllib.request.urlopen(REQUEST, context=ssl_context)
REQUEST_RESPONSE = json.loads(R.read())

# For polling, the response dictionary must contain a list called "endpoints", which will contain new endpoint information. Each endpoint
# must have a field named either "mac" or "ip". The endpoint object/dictionary may also have a "properties" field, which contains property information in the format
# {"propert_name": "property_value"}. The full response object, for example would be:
# {"endpoints":
#    [
#       {"mac": "001122334455",
#        "properties":
#           {"property1": "property_value", "property2": "property_value2"}
#       }
#    ]
#}
ENDPOINTS = []
# for each endpoint
for endpoint_data in REQUEST_RESPONSE:
    endpoint = {}
    mac_with = endpoint_data["mac_addr"]
    # Insert Device only if mac_with match pattern xx:xx:xx:xx:xx:xx
    if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_with.lower()):
        mac = "".join(mac_with.split(":"))
        endpoint["mac"] = mac
        properties = {}
        # for each properties
        for key, value in endpoint_data.items():
            if key in EFFICIENTIP_TO_PROPS_MAP and key != "mac_addr":
                properties[EFFICIENTIP_TO_PROPS_MAP[key]] = value
        endpoint["properties"] = properties
        ENDPOINTS.append(endpoint)

response = {}
response["endpoints"] = ENDPOINTS
