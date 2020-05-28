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
sites = []

credentials["username"] = params["connect_ubiquitisdn_username"]
credentials["password"] = params["connect_ubiquitisdn_password"]

controller_details["address"] = params["connect_ubiquitisdn_controller_address"]
controller_details["port"] = params["connect_ubiquitisdn_controller_port"]
controller_details["site"] = params["connect_ubiquitisdn_site_name"]
controller_details["all_sites"] = params.get("connect_ubiquitisdn_discover_all_sites", "false")
controller_details["ssl_context"] = ssl_context

logging.debug(
    "Attempting to test Ubiquiti SDN with the following parameters: address={} port={} sites={} username={} password=*****".format(
        controller_details["address"], controller_details["port"], controller_details["site"], credentials["username"]))

code, client = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)

logging.debug("Login to Ubiquiti Controller [{}] returned code [{}]".format(controller_details["address"], code))

if code == 200:
    endpoints = []

    try:

        if controller_details["all_sites"] == "true":
            logging.debug("Querying controller for all configured sites")
            sites_code, query_results = UB_API_NONOO.UB_LIST_SITES(client, controller_details)
            sites_detail = query_results["data"]
            for site in sites_detail:
                sites.append(site["name"])
        else:
            sites_config = controller_details["site"]
            logging.debug("Querying controller for the following configured sites: {}".format(sites_config))
            sites_list = sites_config.split(",")
            for site in sites_list:
                sites.append(site)

        for site in sites:
            controller_details["site"] = site
            client_code, connected_clients = UB_API_NONOO.UB_LIST_CLIENTS(client, controller_details)
            logging.debug("API Client Query returned code [{}] and response [{}]".format(client_code, connected_clients))
            device_code, connected_devices = UB_API_NONOO.UB_LIST_DEVICES(client, controller_details)
            logging.debug("API Device Query returned code [{}] and response [{}]".format(device_code, connected_devices))

            # Query the clients table from the controller
            for endpoint_data in connected_clients["data"]:
                endpoint = {}

                mac_with_dash = endpoint_data.get("mac")
                mac = "".join(mac_with_dash.split(":"))

                ip = endpoint_data.get("ip")
                is_wired = endpoint_data["is_wired"]

                props = {}
                props["connect_ubiquitisdn_controller_ip"] = controller_details["address"]
                props["connect_ubiquitisdn_site"] = controller_details["site"]
                try:
                    if mac is not None:
                        endpoint["mac"] = mac
                        props["connect_ubiquitisdn_connectivity_type"] = "Wired" if is_wired is True else "Wireless"

                        if ip == controller_details["address"]:
                            props["connect_ubiquitisdn_role"] = "Controller"
                        else:
                            props["connect_ubiquitisdn_role"] = "Client"

                        endpoint["properties"] = props
                        endpoints.append(endpoint)
                except KeyError:
                    logging.error("No MAC")

            # Query the devices table from the controller
            for endpoint_data in connected_devices["data"]:
                endpoint = {}

                mac_with_dash = endpoint_data.get("mac")
                mac = "".join(mac_with_dash.split(":"))

                ip = endpoint_data.get("ip")

                props = {}
                props["connect_ubiquitisdn_controller_ip"] = controller_details["address"]
                props["connect_ubiquitisdn_site"] = controller_details["site"]
                try:
                    if mac is not None:
                        endpoint["mac"] = mac
                        props["connect_ubiquitisdn_role"] = "Device"
                        endpoint["properties"] = props
                        endpoints.append(endpoint)
                except KeyError:
                    logging.error("No MAC")
            response["endpoints"] = endpoints
    except Exception as e:
        response["error"] = "Polling failed: {}".format(str(e))

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
