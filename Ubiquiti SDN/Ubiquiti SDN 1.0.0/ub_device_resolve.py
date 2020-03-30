"""
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
"""

import logging

# from UnifiAPI import API as Unifi_API
credentials = {}
controller_details = {}
response = {}

credentials["username"] = params["connect_ubiquitisdn_username"]
credentials["password"] = params["connect_ubiquitisdn_password"]

controller_details["address"] = params["connect_ubiquitisdn_controller_address"]
controller_details["port"] = params["connect_ubiquitisdn_controller_port"]
controller_details["site"] = params["connect_ubiquitisdn_site_name"]

code, client = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)

ubiquiti_property_map = {
    "model": "connect_ubiquitisdn_device_model",
    "serial": "connect_ubiquitisdn_device_serial",
    "type": "connect_ubiquitisdn_device_type",
    "name": "connect_ubiquitisdn_device_name"
}

logging.debug("Login to Ubiquiti Controller [{}] returned code [{}]".format(controller_details["address"], code))
if code == 200:
    properties = []
    if "mac" in params:
        if "connect_ubiquitisdn_role" in params:
            if params["connect_ubiquitisdn_role"] == "Device":
                mac = ':'.join(params["mac"][i:i + 2] for i in range(0, 12, 2))
                logging.debug("Attempting API Query for MAC [{}]".format(mac))
                query_code, query_results = UB_API_NONOO.UB_QUERY_DEVICE(client, controller_details, mac)
                if not len(query_results) == 0:
                    device_details = query_results["data"][0]
                    logging.debug("API Query returned code [{}] and response [{}]".format(query_code, query_results))

                    properties = {}
                    for key, value in device_details.items():
                        if key in ubiquiti_property_map:
                            properties[ubiquiti_property_map[key]] = value
                    response["properties"] = properties
                else:
                    response["error"] = "Could not find this endpoint in the Unifi SDN Controller."
            else:
                response["error"] = "This property only applies to Ubiquiti SDN Discovered Devices."
        else:
            response["error"] = "Ubiquiti SDN Role determination is required to resolve this property."
    else:
        response["error"] = "No mac address to query the device."
else:
    response["error"] = "API Connection Failed, check configuration."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
