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

# Mapping between Vectra API response fields to Forescout properties
VECTRA_TO_PROPS_MAP = {
    "last_source": "connect_vectra_ip",
    "threat": "connect_vectra_threat",
    "certainty": "connect_vectra_certainty",
    "tags": "connect_vectra_tags",
    "sensor": "connect_vectra_sensor",
    "sensor_name": "connect_vectra_sensor_name",
    "severity": "connect_vectra_severity",
    "state": "connect_vectra_state",
    "id": "connect_vectra_id"
    }

VECTRA_DETECTION_TO_PROPS_MAP = {
    "detection_category": "category",
    "detection_type": "type",
    "certainty": "certainty",
    "threat": "threat"
}

# Import Param
#All server configuration fields will be available in the 'params' dictionary.
URL = params["connect_vectra_url"] # Server URL
TOKEN = params["connect_vectra_token_id"]  # Token ID

# Prepare request
GET_URL = URL + '/search/hosts/?page_size=1000&query_string=host.state:"active"'
DEVICE_HEADER = {"Content-Type": "application/json", "Authorization": "Token " + str(TOKEN)}
REQUEST = urllib.request.Request(GET_URL, headers=DEVICE_HEADER)

# Get data
R = urllib.request.urlopen(REQUEST, context=ssl_context)
REQUEST_RESPONSE = json.loads(R.read())

# For polling, the response dictionary must contain a list called "endpoints", which will contain
# new endpoint information. Each endpoint must have a field named either "mac" or "ip". The
# endpoint object/dictionary may also have a "properties" field, which contains property
#information in the format
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
# For each endpoint
for endpoint_data in REQUEST_RESPONSE["results"]:
    endpoint = {}
    user_ip = endpoint_data["last_source"]
    endpoint["ip"] = user_ip
    list_property_detection = []

    # for each threat detection, output will be a list of endpoint threat detection
    for all_detections in endpoint_data["detection_summaries"]:
        property_detection = {}
        subfields = {}
        for key, value in all_detections.items():
            if key in VECTRA_DETECTION_TO_PROPS_MAP:
                subfields[VECTRA_DETECTION_TO_PROPS_MAP[key]] = value
        property_detection = subfields
        list_property_detection.append(property_detection)

    # For each properties
    properties = {}
    for key, value in endpoint_data.items():
        if key in VECTRA_TO_PROPS_MAP and key != "last_source":
            properties[VECTRA_TO_PROPS_MAP[key]] = value

    # Put the list of endpoint threat detection into the composite properties
    properties["connect_vectra_detection"] = list_property_detection

    endpoint["properties"] = properties
    ENDPOINTS.append(endpoint)
response = {}
response["endpoints"] = ENDPOINTS
