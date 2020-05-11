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

controller_details["address"] = params["connect_ubiquitisdn_controller_address"]
controller_details["port"] = params["connect_ubiquitisdn_controller_port"]
controller_details["site"] = params["connect_ubiquitisdn_site_name"]
controller_details["ssl_context"] = ssl_context

code, client = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)

if code == 200:
    properties = []
    if "mac" in params:
        if "connect_ubiquitisdn_role" in params:
            if params["connect_ubiquitisdn_role"] == "Client":
                mac = ':'.join(params["mac"][i:i + 2] for i in range(0, 12, 2))
                logging.debug("Attempting API Query for MAC [{}]".format(mac))
                query_code, query_results = UB_API_NONOO.UB_QUERY_CLIENT(client, controller_details, mac)
                client_details = query_results["data"][0]
                logging.debug("API Query returned code [{}] and response [{}]".format(query_code, query_results))
                composite_entry = {}

                try:
                    properties = {}
                    if params["connect_ubiquitisdn_connectivity_type"] == "Wireless":
                        ap_mac = client_details["ap_mac"]
                        device_query_code, device_query_results = UB_API_NONOO.UB_QUERY_DEVICE(client, controller_details,
                                                                                               ap_mac)
                        device_details = device_query_results["data"][0]
                        logging.debug("API Query returned code [{}] and response [{}]".format(device_query_code,
                                                                                              device_query_results))

                        composite_entry["wireless_ssid"] = client_details["essid"]
                        composite_entry["wireless_protocol"] = client_details["radio"]
                        composite_entry["wireless_ssid"] = client_details["essid"]
                        composite_entry["wireless_ap_mac"] = client_details["ap_mac"]
                        composite_entry["wireless_ap_ip"] = device_details["ip"]
                        composite_entry["wireless_ap_name"] = device_details["name"]
                        composite_entry["wireless_channel"] = client_details["channel"]
                        properties["connect_ubiquitisdn_client_wireless_details"] = composite_entry

                    if params["connect_ubiquitisdn_connectivity_type"] == "Wired":
                        switch_mac = client_details["sw_mac"]
                        device_query_code, device_query_results = UB_API_NONOO.UB_QUERY_DEVICE(client, controller_details,
                                                                                               switch_mac)
                        device_details = device_query_results["data"][0]
                        logging.debug("API Query returned code [{}] and response [{}]".format(device_query_code,
                                                                                              device_query_results))

                        composite_entry["wired_switch_name"] = device_details["name"]
                        composite_entry["wired_switch_port"] = client_details["sw_port"]
                        composite_entry["wired_switch_mac"] = client_details["sw_mac"]
                        composite_entry["wired_switch_ip"] = device_details["ip"]

                        properties["connect_ubiquitisdn_client_wired_details"] = composite_entry

                    response["properties"] = properties
                except Exception as e:
                    response["error"] = "Query device failed: {}".format(str(e))
            else:
                response["error"] = "This property only applies to Ubiquiti SDN Discovered Clients."
        else:
            response["error"] = "Ubiquiti SDN Role determination is required to resolve this property."
    else:
        response["error"] = "No mac address to query the endpoint."
else:
    response["error"] = "API Connection Failed, check configuration."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
