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
medc_server_details = {}
response = {}

credentials["username"] = params["connect_medesktopcentral_username"]
credentials["password"] = params["connect_medesktopcentral_password"]

medc_server_details["address"] = params["connect_medesktopcentral_server_ipaddress"]
medc_server_details["port"] = params["connect_medesktopcentral_server_port"]

if "nbthost" in params:
    # and params["nbthost"]!="":
    host_name = params["nbthost"]

    code, client, session_token, data = medesktopcentral_api_lib.medesktopcentral_http_client(credentials, medc_server_details)

    medesktopcentral_property_map = {
        "os_platform_name":"connect_medesktopcentral_endpoint_os",
        "service_pack":"connect_medesktopcentral_endpoint_sp",
        "branch_office_name":"connect_medesktopcentral_branch_office",
        "resource_id": "connect_medesktopcentral_resource_id",
        "agent_last_contact_time":"connect_medesktopcentral_agent_last_contact_time",
        "agent_version": "connect_medesktopcentral_agent_version"}

    #logging.debug("RESOLVE: Login to ManageEngine Server [{}] returned code [{}]".format(medc_server_details["address"], code))

    if code == 200:
        response = {}
        properties = []

        query_code, query_results = medesktopcentral_api_lib.medesktopcentral_get_resid(client, medc_server_details, session_token, host_name)
        logging.debug("RESOLVE: GET RESID hostname[{}] returned code [{}] and RESULTS[{}]".format(host_name,query_code,query_results))

        if query_results["status"] != "error":

            if len(query_results["message_response"]["computers"]) > 0:

                if "error_description" not in query_results["message_response"]["computers"][0]:
                    ctr = 0
                    for endpoint_data in query_results["message_response"]["computers"]: 
                        mac_with_colon_tmp = query_results["message_response"]["computers"][ctr]["mac_address"]
                        mac_with_colon = mac_with_colon_tmp[0:17]
                        
                        properties = {}
                        host_details = query_results["message_response"]["computers"][ctr]
                        
                        logging.debug("RESID RESOLVE: ResID[{}]".format(str(host_details["resource_id"])))
                        
                        for key, value in host_details.items():
                            if key in medesktopcentral_property_map:
                                if key == "agent_last_contact_time":
                                    if value != "--":
                                        properties[medesktopcentral_property_map[key]] = medesktopcentral_api_lib.medesktopcentral_get_timestamp(value)
                                elif key != "mac_address":
                                    if value != "--":
                                        properties[medesktopcentral_property_map[key]] = str(value)
                                    else:
                                        properties[medesktopcentral_property_map[key]] = "None"
                                else:
                                    if value != "--":
                                        properties[medesktopcentral_property_map[key]] = str(value)
                        response["properties"] = properties
                else:
                    logging.debug("ERROR: ME Server Response [{}].".format(query_results["message_response"]["computers"][0]["error_description"]))
                    response["error"] = "ERROR: ME Server Response [{}].".format(query_results["message_response"]["computers"][0]["error_description"])
            else:
                logging.debug("POLL RESID RESOLVE: Host [{}] not found in ManageEngine server.".format(host_name))
                response["error"] = "Host [{}] not found in ManageEngine server.".format(host_name)
        else:
            response["error"] = "ERROR: {}.".format(query_results["error_description"])
    else:
        response["error"] = "API Connection Failed, check configuration."
else:
        response["error"] = "Could not resolve NetBIOS host name."