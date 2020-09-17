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

if code == 200:
    if "mac" in params:
        if "connect_ubiquitisdn_role" in params:
            if params["connect_ubiquitisdn_role"] == "Controller":
                mac = ':'.join(params["mac"][i:i + 2] for i in range(0, 12, 2))
                logging.debug("Attempting API Query for MAC [{}]".format(mac))
                try:
                    query_code, query_results = UB_API_NONOO.UB_LIST_SITES(client, controller_details, headers)
                    sites_detail = query_results["data"]
                    logging.debug("API Query returned code [{}] and response [{}]".format(query_code, query_results))

                    composite_list = []
                    properties = {}
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

                    for site in sites_detail:
                        composite_entry = {}
                        total_clients = 0
                        total_guests = 0
                        total_devices = 0
                        for subsystem in site['health']:
                            users = subsystem.get('num_user')
                            guests = subsystem.get('num_guest')
                            devices = subsystem.get('num_adopted')
                            if users is not None:
                                total_clients = total_clients + users
                            if guests is not None:
                                total_guests = total_guests + guests
                            if devices is not None:
                                total_devices = total_devices + devices
                        composite_entry["site_name"] = site["name"]
                        composite_entry["site_description"] = site["desc"]
                        composite_entry["site_clients"] = total_clients
                        composite_entry["site_guests"] = total_guests
                        composite_entry["site_devices"] = total_devices
                        if site["name"] in sites:
                            composite_entry["site_managed"] = True
                        else: 
                            composite_entry["site_managed"] = False

                        composite_list.append(composite_entry)
                    properties["connect_ubiquitisdn_controller_sites"] = composite_list
                    response["properties"] = properties
                except Exception as e:
                    response["error"] = "List sites failed: {}".format(str(e))
            else:
                response["error"] = "This property only applies to Ubiquiti SDN Discovered Clients."
        else:
            response["error"] = "Ubiquiti SDN Role determination is required to resolve this property."
    else:
        response["error"] = "No mac address to query the endpoint."
else:
    response["error"] = "API Connection Failed, check configuration."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
