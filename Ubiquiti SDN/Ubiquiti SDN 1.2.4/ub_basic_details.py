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

credentials["username"] = params["connect_ubiquitisdn_username"]
credentials["password"] = params["connect_ubiquitisdn_password"]

controller_details["type"] = params["connect_ubiquitisdn_platform"]
controller_details["address"] = params["connect_ubiquitisdn_controller_address"]
controller_details["port"] = params["connect_ubiquitisdn_controller_port"]
controller_details["site"] = params["connect_ubiquitisdn_site_name"]
controller_details["all_sites"] = params.get("connect_ubiquitisdn_discover_all_sites", "false")
controller_details["ssl_context"] = ssl_context

code, client, headers = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)

logging.debug("Login to Ubiquiti Controller [{}] returned code [{}]".format(controller_details["address"], code))
if code == 200:
    if "mac" in params:
        # Add if no connect_ubiquitisdn_site defined then set site to default
        # TODO: if discovery is not enabled there is no way to learn connect_ubiquitisdn_site
        #       Need to create a resolve script
        controller_details["site"] = params.get("connect_ubiquitisdn_site", "default")
        mac = ':'.join(params["mac"][i:i + 2] for i in range(0, 12, 2))
        logging.debug("Attempting API Query for MAC [{}]".format(mac))
        clients_query_results = []
        device_query_results = []
        try:
            clients_query_code, clients_query_results = UB_API_NONOO.UB_QUERY_CLIENT(client, controller_details, mac, headers)
            logging.debug("Client API Query returned code [{}] and response [{}]".format(clients_query_code,
                                                                                         clients_query_results))
        except:
            pass

        try:
            device_query_code, device_query_results = UB_API_NONOO.UB_QUERY_DEVICE(client, controller_details, mac, headers)
            logging.debug(
                "Device API Query returned code [{}] and response [{}]".format(device_query_code, device_query_results))
        except:
            pass

        if not len(clients_query_results) == 0:
            device_details = clients_query_results["data"][0]

            properties = {}
            ip = device_details.get("ip")
            if ip == controller_details["address"]:
                properties["connect_ubiquitisdn_role"] = "Controller"
            else:
                properties["connect_ubiquitisdn_role"] = "Client"
            properties["connect_ubiquitisdn_controller_ip"] = controller_details["address"]
            properties["connect_ubiquitisdn_site"] = controller_details["site"]
            response["properties"] = properties
        elif not len(device_query_results) == 0:
            device_details = device_query_results["data"][0]

            properties = {}
            properties["connect_ubiquitisdn_role"] = "Device"
            properties["connect_ubiquitisdn_controller_ip"] = controller_details["address"]
            properties["connect_ubiquitisdn_site"] = controller_details["site"]
            response["properties"] = properties
        else:
            response["error"] = "Could not find this MAC in the Unifi SDN Controller."

    else:
        response["error"] = "A MAC address is required to resolve this property. Try enabling discovery."
else:
    response["error"] = "API Connection Failed, check configuration parameters."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
