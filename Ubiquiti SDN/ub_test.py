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

code, client, headers = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)
logging.debug("Login return code: {}".format(str(code)))
logging.debug("Attempting to test Ubiquiti SDN with the following parameters: address={} port={} site={} username={} password=*****".format(
    controller_details["address"], controller_details["port"], controller_details["site"], credentials["username"]))

if code == 200:
    try:
        message = []
        if controller_details["all_sites"] == "true":
            message.append("Querying controller for all managed sites.")
            sites_code, query_results = UB_API_NONOO.UB_LIST_SITES(client, controller_details, headers)
            sites_detail = query_results["data"]
            for site in sites_detail:
                sites.append(site["name"])
        else:
            sites_config = controller_details["site"]
            message.append("Querying controller for the following managed sites: {}".format(sites_config))
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

            message.append("Found {} connected clients and {} SDN devices in site: {}".format(len(connected_clients["data"]),len(connected_devices["data"]),controller_details["site"]))
        response["succeeded"] = True
        response["result_msg"] = "\n".join(message)
    except Exception as e:
        response["succeeded"] = False
        response["troubleshooting"] = "Test failed: {}".format(str(e))
else:
    response["succeeded"] = False
    response["troubleshooting"] = "Did not get a 200 code from API connection."
