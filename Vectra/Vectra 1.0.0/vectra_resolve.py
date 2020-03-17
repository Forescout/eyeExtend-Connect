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
    "threat": "connect_vectra_threat",
    "certainty": "connect_vectra_certainty",
    "tags": "connect_vectra_tags",
    "sensor": "connect_vectra_sensor",
    "sensor_name": "connect_vectra_sensor_name",
    "severity": "connect_vectra_severity",
    "state": "connect_vectra_state"
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

# For properties and actions defined in the 'property.conf' file, Forescout properties can be added
# as dependencies. These values will be found in the params dictionary if Forescout was able to
#resolve the properties. If not, they will not be found in the params dictionary.
if "ip" in params:
        # Prepare request
        GET_URL = URL + "/search/hosts/?page_size=1000&query_string=host.state:\"active\"%20and%20host.last_source:\"" + params["ip"] +"\""
        DEVICE_HEADER = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Token " + str(TOKEN)}
        # Get HOST data
        REQUEST = urllib.request.Request(GET_URL, headers=DEVICE_HEADER)
        R = urllib.request.urlopen(REQUEST, context=ssl_context)
        REQUEST_RESPONSE = json.loads(R.read())

        if REQUEST_RESPONSE:
            # Create the composite list format "connect_vectra_detection"
            REQUEST_RESPONSE = REQUEST_RESPONSE["results"][0]
            list_property_detection = []
            for all_detections in REQUEST_RESPONSE["detection_summaries"]:
                property_detection = {}
                subfields = {}
                for key, value in all_detections.items():
                    if key in VECTRA_DETECTION_TO_PROPS_MAP:
                        subfields[VECTRA_DETECTION_TO_PROPS_MAP[key]] = value
                property_detection = subfields
                list_property_detection.append(property_detection)

            # All responses from scripts must contain the JSON object 'response'. Host property resolve
            # scripts will need to populate a 'properties' JSON object within the JSON object
            # 'response'. The 'properties' object will be a key, value mapping between the Forescout
            # property name and the value of the property.
            properties = {}
            for key, value in REQUEST_RESPONSE.items():
                if key in VECTRA_TO_PROPS_MAP:
                    properties[VECTRA_TO_PROPS_MAP[key]] = value

            # Put our custom made connect_vectra_detection property into properties
            properties["connect_vectra_detection"] = list_property_detection
        response = {}
        response["properties"] = properties
else:
    response = {}
    response["error"] = "Error: No IP to query the endpoint"
