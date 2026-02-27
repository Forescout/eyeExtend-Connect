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

credentials = {}
controller_details = {}
response = {}

credentials["api_key"] = params["connect_controller_api_key_tag"]

controller_details["address"] = params["connect_controller_ip_tag"]
controller_details["port"] = params["connect_ubiquitisdn_controller_port"]
controller_details["site"] = params["connect_ubiquitisdn_site_name"]
controller_details["all_sites"] = params.get("connect_ubiquitisdn_discover_all_sites", "false")
controller_details["ssl_context"] = ssl_context

code, client, headers = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)

ubiquiti_property_map = {
    "network": "connect_ubiquitisdn_network_binding",
    "name": "connect_ubiquitisdn_client_alias",
    "is_guest": "connect_ubiquitisdn_client_guest"
}

logging.debug("Login to Ubiquiti Controller [{}] returned code [{}]".format(controller_details["address"], code))
if code == 200:
    if "mac" in params:
        if "connect_ubiquitisdn_role" in params:
            if params["connect_ubiquitisdn_role"] == "Client":
                # Add if no connect_ubiquitisdn_site defined then set site to default
                # TODO: if discovery is not enabled there is no way to learn connect_ubiquitisdn_site
                #       Need to create a resolve script
                controller_details["site"] = params.get("connect_ubiquitisdn_site", "default")
                mac = ':'.join(params["mac"][i:i + 2] for i in range(0, 12, 2))
                logging.debug("Attempting API Query for MAC [{}]".format(mac))
                try:
                    query_code, query_results = UB_API_NONOO.UB_QUERY_CLIENT(client, controller_details, mac, headers)
                    if not len(query_results) == 0:
                        device_details = query_results["data"][0]
                        logging.debug("API Query returned code [{}] and response [{}]".format(query_code, query_results))

                        properties = {}
                        for key, value in device_details.items():
                            if key in ubiquiti_property_map:
                                if value != "":
                                    properties[ubiquiti_property_map[key]] = str(value)
                                else:
                                    properties[ubiquiti_property_map[key]] = "None"
                        properties["connect_ubiquitisdn_connectivity_type"] = "Wired" \
                            if device_details["is_wired"] is True else "Wireless"
                        response["properties"] = properties
                    else:
                        response["error"] = "Could not find this endpoint in the Unifi SDN Controller."
                except Exception as e:
                    response["error"] = "Query client failed: {}".format(str(e))
            else:
                response["error"] = "This property only applies to Ubiquiti SDN Discovered Clients"
        else:
            response["error"] = "Ubiquiti SDN Role determination is required to resolve this property."
    else:
        response["error"] = "No MAC address to query the endpoint."
else:
    response["error"] = "API Connection Failed, check configuration."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
