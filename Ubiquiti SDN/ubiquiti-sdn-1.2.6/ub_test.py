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

# CHANGE: parse aligned comma-separated lists for address, api_key, and site
_addresses = [a.strip() for a in params["connect_ubiquitisdn_controller_address"].split(",")]
_api_keys = [k.strip() for k in params["connect_ubiquitisdn_api_key"].split(",")]
_sites    = [s.strip() for s in params["connect_ubiquitisdn_site_name"].split(",")]

# credentials["api_key"] = params["connect_ubiquitisdn_api_key"]
# controller_details["address"] = params["connect_ubiquitisdn_controller_address"]
# controller_details["site"] = params["connect_ubiquitisdn_site_name"]

controller_details["port"] = params["connect_ubiquitisdn_controller_port"]
controller_details["all_sites"] = params.get("connect_ubiquitisdn_discover_all_sites", "false")
controller_details["ssl_context"] = ssl_context

overall_messages = []
any_success = False

# CHANGE: iterate by index so each address/site/api_key align
for i in range(len(_addresses)):
    controller_details["address"] = _addresses[i]
    controller_details["site"] = _sites[i]
    credentials["api_key"] = _api_keys[i]

    code, client, headers = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)
    logging.debug("Login return code: {}".format(str(code)))
    logging.debug("Attempting Ubiquiti SDN with: address={} port={} site={}".format(
            controller_details["address"], controller_details["port"],controller_details["site"]))


    if code == 200:
        try:
            message = []
            sites = []  # reset per controller

            # UnifiOS devices do not support multi sites; preserve original logic
            if controller_details["all_sites"] == "true" and controller_details.get("type") != 'unifios':
                message.append("({}) Querying controller for all managed sites.".format(controller_details["address"]))
                sites_code, query_results = UB_API_NONOO.UB_LIST_SITES(client, controller_details, headers)
                sites_detail = query_results["data"]
                for site in sites_detail:
                    sites.append(site["internalReference"])
            else:
                sites_config = controller_details["site"]
                message.append("({}) Querying controller for the following managed sites: {}".format(
                    controller_details["address"], sites_config))
                sites_list = sites_config.split(",")
                for site in sites_list:
                    sites.append(site)
                logging.debug("Site List: {}".format(list(sites)))

            for site in sites:
                controller_details["site"] = site
                client_code, connected_clients = UB_API_NONOO.UB_LIST_CLIENTS(client, controller_details, headers)
                logging.debug("API Client Query returned code [{}] and response [{}]".format(client_code, connected_clients))

                device_code, connected_devices = UB_API_NONOO.UB_LIST_DEVICES(client, controller_details, headers)
                logging.debug("API Device Query returned code [{}] and response [{}]".format(device_code, connected_devices))

                message.append("({}) Found {} connected clients and {} SDN devices in site: {}".format(
                    controller_details["address"],len(connected_clients["data"]),len(connected_devices["data"]),controller_details["site"])
                )

            any_success = True
            overall_messages.extend(message)
        except Exception as e:
            overall_messages.append("({}) Test failed: {}".format(controller_details["address"], str(e)))
    else:
        overall_messages.append("({}) Did not get a 200 code from API connection.".format(controller_details["address"]))

# preserve original response shape
if any_success:
    response["succeeded"] = True
    response["result_msg"] = "\n".join(overall_messages)
else:
    response["succeeded"] = False
    response["troubleshooting"] = "\n".join(overall_messages) if overall_messages else "No controllers processed."