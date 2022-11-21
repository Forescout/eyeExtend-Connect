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
asset_details = {}
health_status_table = {0:'Unknown', 1:'Healthy', 2:'Vulnerable', 3:'Highly Vulnerable'}
scan_status_table = {226:'Failed', 227:'In Progress', 228:'Success', 229:'Not Scanned'}
agent_install_status_table = {21:'Yet to Install', 22:'Installed', 23:'Uninstalled', 24:'Yet to Uninstall', 29:'Installation Failure'}

res_id = ''
response = {}

credentials["username"] = params["connect_medesktopcentral_username"]
credentials["password"] = params["connect_medesktopcentral_password"]

medc_server_details["address"] = params["connect_medesktopcentral_server_ipaddress"]
medc_server_details["port"] = params["connect_medesktopcentral_server_port"]

res_id = params["connect_medesktopcentral_resource_id"]

code, client, session_token, data = medesktopcentral_api_lib.medesktopcentral_http_client(credentials, medc_server_details)

medesktopcentral_property_map = {
    "last_successful_scan":"connect_medesktopcentral_last_successful_scan",
    "scan_status":"connect_medesktopcentral_patch_scan_status",
    "installation_status":"connect_medesktopcentral_ais",
    "agent_version":"connect_medesktopcentral_agent_version"
}


if code == 200:

    if not session_token == 0:

        query_code, query_results = medesktopcentral_api_lib.medesktopcentral_query_asset(client, medc_server_details, session_token, res_id)

        if not len(query_results) == 0:
            asset_details = query_results['message_response']['allsystems'][0]
            logging.debug("API Client Query ME server asset returned code [{}] and response [{}]".format(query_code, query_results))

            properties = {}
            properties['connect_medesktopcentral_ais']=''
            for key, value in asset_details.items():
                if key in medesktopcentral_property_map:
                    #properties[medesktopcentral_property_map[key]] = value
                    if key == "last_successful_scan" or key == "agent_last_contact_time":
                        properties[medesktopcentral_property_map[key]] = medesktopcentral_api_lib.medesktopcentral_get_timestamp(value)
                    elif key == "resource_health_status":
                        properties[medesktopcentral_property_map[key]] = health_status_table[value]
                    elif key == "scan_status":
                        properties[medesktopcentral_property_map[key]] = scan_status_table[value]
                    elif key == "resource_id":
                        properties[medesktopcentral_property_map[key]] = str(value)
                    else:    
                        properties[medesktopcentral_property_map[key]] = value

            if properties['connect_medesktopcentral_ais'] is None:
                properties['connect_medesktopcentral_ais']='Installed'
                #properties['connect_medesktopcentral_agent_version']=''

            #Retrieve Computer Details Summary..
            composite_list = []
            logging.debug("Attempting Computer Details API Query for Resource ID [{}]".format(res_id))
            query_code, query_results = medesktopcentral_api_lib.medesktopcentral_query_computer_details(client, medc_server_details, session_token, res_id)
            computer_details = query_results['message_response']['compdetailssummary']
            logging.debug("***COMPUTER DETAILS...***: Query Code:{} Rec Count:{} Response:{}".format(query_code,str(len(computer_details)), query_results))
            
            if not len(computer_details) == 0:
                for entry in computer_details:
                    composite_entry={}
                    composite_entry["memory"] = computer_details['computer_hardware_summary']['memory']
                    composite_entry["device_model"] = computer_details['computer_hardware_summary']['device_model']
                    composite_entry["device_type"] = computer_details['computer_hardware_summary']['device_type']
                    composite_entry["serial_number"] = computer_details['computer_hardware_summary']['serial_number']
                    composite_entry["processor"] = computer_details['computer_hardware_summary']['processor']
                    composite_entry["device_manufacturer"] = computer_details['computer_hardware_summary']['device_manufacturer']
                    composite_entry["percent_used"] = computer_details['computer_disk_summary']['percent_used']
                    composite_entry["total_size"] = computer_details['computer_disk_summary']['total_size']
                    composite_list.append(composite_entry)
                    
                properties['connect_medesktopcentral_computer_details'] = composite_list

            #Retrieve Endpoint Agent Install Status..
            logging.debug("Attempting Agent Install Status API Query for Resource ID [{}]".format(res_id))
            query_code, query_results = medesktopcentral_api_lib.medesktopcentral_query_agent_install_status(client, medc_server_details, session_token, res_id)
            agent_details = query_results['message_response']['computers'][0]
            logging.debug("***ME AGENT INSTALL STATUS QUERY...***: Query Code:{} Rec Count:{}".format(query_code,str(len(agent_details))))
            #Assign install status..
            properties[medesktopcentral_property_map['installation_status']] = agent_install_status_table[agent_details['installation_status']]
            properties[medesktopcentral_property_map['agent_version']] = agent_details['agent_version']

            response["properties"] = properties
        else:
            response["error"] = "Could not find this endpoint in the Desktop Central Server."            
    else:    
        response["succeeded"] = False
        response["result_msg"] = "Credentials appears to be wrong or the account provided is disabled."
        response["troubleshooting"] = "Credentials appears to be wrong or the account provided is disabled."
else:
    response["succeeded"] = False
    response["troubleshooting"] = "Did not get a 200 code from API connection."
