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

controller_details["type"] = params["connect_ubiquitisdn_platform"]
controller_details["address"] = params["connect_ubiquitisdn_controller_address"]
controller_details["port"] = params["connect_ubiquitisdn_controller_port"]
controller_details["site"] = params["connect_ubiquitisdn_site_name"]
controller_details["all_sites"] = params.get("connect_ubiquitisdn_discover_all_sites", "false")
controller_details["ssl_context"] = ssl_context

logging.debug(
    "Attempting to test Ubiquiti SDN with the following parameters: address={} port={} sites={} username={} password=*****".format(
        controller_details["address"], controller_details["port"], controller_details["site"], credentials["username"]))

code, client, headers = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)

logging.debug("Login to Ubiquiti Controller [{}] returned code [{}]".format(controller_details["address"], code))

if code == 200:
    endpoints = []

    try:

        if controller_details["all_sites"] == "true":
            logging.debug("Querying controller for all configured sites")
            sites_code, query_results = UB_API_NONOO.UB_LIST_SITES(client, controller_details, headers)
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
            client_code, connected_clients = UB_API_NONOO.UB_LIST_CLIENTS(client, controller_details, headers)
            logging.debug("API Client Query returned code [{}] and response [{}]".format(client_code, connected_clients))
            device_code, connected_devices = UB_API_NONOO.UB_LIST_DEVICES(client, controller_details, headers)
            logging.debug("API Device Query returned code [{}] and response [{}]".format(device_code, connected_devices))

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

            # Query the clients table from the controller
            for endpoint_data in connected_clients["data"]:
                endpoint = {}
                mac_with_dash = endpoint_data.get("mac")
                mac = "".join(mac_with_dash.split(":"))
                gw_seen = False
                sw_seen = False
                ap_seen = False
                ip = endpoint_data.get("ip","")
                is_wired = endpoint_data["is_wired"]
                composite_entry = {}
                props = {}
                props["connect_ubiquitisdn_controller_ip"] = controller_details["address"]
                props["connect_ubiquitisdn_site"] = controller_details["site"]
                try:
                    if mac is not None:
                        endpoint["mac"] = mac
                        endpoint["ip"] = ip
                        sw_ip = ""
                        sw_name = ""
                        sw_kernel_ver = ""
                        ap_ip = ""
                        ap_name = ""
                        ap_kernel_ver = ""
                        gw_name = ""
                        gw_model = ""
                        gw_ip = ""
                        gw_kernel_ver = ""
                        # Capture Connectivity Details
                        for device in connected_devices["data"]:
                            if device["mac"] == endpoint_data.get("gw_mac", ""):
                                gw_name = device.get("name", "")
                                gw_model = device.get("model", "")
                                gw_ip = device.get("ip", "")
                                gw_kernel_ver = device.get("kernel_version", "")
                                gw_seen = True

                            if device["mac"] == endpoint_data.get("sw_mac", ""):
                                sw_name = device.get("name", "")
                                sw_model = device.get("model","")
                                sw_ip = device.get("ip", "")
                                sw_kernel_ver = device.get("kernel_version", "")
                                sw_seen = True

                            if device["mac"] == endpoint_data.get("ap_mac", ""):
                                ap_name = device.get("name","")
                                ap_model = device.get("model","")
                                ap_ip = device.get("ip","")
                                ap_kernel_ver = device.get("kernel_version", "")
                                ap_seen = True

                        # Since we already pulled all this info, lets report it!
                        # TODO Integrate this with cache mechanism so there is an option to pull data using cache
                        # and refresh cache data when new date is learned from controller
                        # General client data
                        props["connect_ubiquitisdn_connectivity_type"] = "Wired" if is_wired is True else "Wireless"
                        props["connect_ubiquitisdn_client_hostname"] = endpoint_data.get("hostname", "")
                        props["connect_ubiquitisdn_client_alias"] = endpoint_data.get("name", "")
                        props["connect_ubiquitisdn_network_binding"] = endpoint_data.get("network", "")
                        props["connect_ubiquitisdn_client_note"] = endpoint_data.get("note", "")
                        props["connect_ubiquitisdn_client_guest"] = str(endpoint_data.get("is_guest", False))
                        
                        if endpoint_data.get("is_guest", False):
                            # Only get the guest authorized state if the endpoint was returned as a guest
                            props["connect_ubiquitisdn_client_guest_authorized"] = str(endpoint_data.get("authorized", False))

                        # Switch Data
                        if sw_seen:
                            composite_entry["wired_switch_port"] = endpoint_data.get("sw_port", "")
                            composite_entry["wired_switch_ip"] = sw_ip
                            composite_entry["wired_switch_name"] = sw_name
                            composite_entry["wired_switch_mac"] = endpoint_data.get("sw_mac", "")
                            composite_entry["wired_switch_kernel"] = sw_kernel_ver
                            props["connect_ubiquitisdn_client_wired_details"] = composite_entry
                            composite_entry = {}
                        # Wifi Data
                        if ap_seen:
                            composite_entry["wireless_channel"] = endpoint_data.get("channel", "")
                            composite_entry["wireless_protocol"] = endpoint_data.get("radio", "")
                            composite_entry["wireless_ap_ip"] = ap_ip
                            composite_entry["wireless_ap_name"] = ap_name
                            composite_entry["wireless_ap_mac"] = endpoint_data.get("ap_mac", "")
                            composite_entry["wireless_ssid"] = endpoint_data.get("essid", "")
                            composite_entry["wireless_kernel"] = ap_kernel_ver
                            props["connect_ubiquitisdn_client_wireless_details"] = composite_entry
                            composite_entry = {}
                        # Gateway Data
                        if gw_seen:
                            composite_entry["gateway_name"] = gw_name
                            composite_entry["gateway_model"] = gw_model
                            composite_entry["gateway_ip"] = gw_ip
                            composite_entry["gateway_kernel"] = gw_kernel_ver
                            props["connect_ubiquitisdn_client_gateway_details"] = composite_entry
                            composite_entry = {}

                        if ip == controller_details["address"]:
                            props["connect_ubiquitisdn_role"] = "Controller"
                        else:
                            props["connect_ubiquitisdn_role"] = "Client"
                        
                        endpoint["properties"] = props
                        endpoints.append(endpoint)
                except KeyError:
                    logging.error("No MAC")

        endpoints = UB_API_NONOO.clean_empty_dict(endpoints)
        response["endpoints"] = endpoints
    except Exception as e:
        response["error"] = "Polling failed: {}".format(str(e))

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
