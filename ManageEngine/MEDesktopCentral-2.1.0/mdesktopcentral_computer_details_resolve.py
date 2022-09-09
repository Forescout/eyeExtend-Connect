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

medc_res_id = params["script_result.2b9fcadea69fc1cf870dc5c7a50446f1"]

code, client, session_token, data = medesktopcentral_api_lib.medesktopcentral_http_client(credentials, medc_server_details)

logging.info("POLL COMPUTER DETAILS RESOLVE: Login to ME Desktop Central Server [{}] returned code [{}]".format(medc_server_details["address"], code))

if code == 200:
    logging.debug("Resource ID is [{}]".format(medc_res_id))
    properties = {}

    if medc_res_id is not None:
        composite_list = []
        logging.debug("Attempting Computer Details API Query for Resource ID [{}]".format(medc_res_id))
        query_code, query_results = medesktopcentral_api_lib.medesktopcentral_query_computer_details(client, medc_server_details, session_token, medc_res_id)
        computer_details = query_results['message_response']['compdetailssummary']
        logging.debug("***COMPUTER DETAILS...***: Query Code:{} Rec Count:{}".format(query_code,str(len(computer_details))))
        #ctr = 0
        if not len(computer_details) == 0:
            for entry in computer_details:
                #classification_id = patch_details[ctr]['severity']
                composite_entry={}
                composite_entry["memory"] = entry['computer_hardware_summary']['memory']
                composite_entry["device_model"] = entry['computer_hardware_summary']['device_model']
                composite_entry["device_type"] = entry['computer_hardware_summary']['device_type']
                composite_entry["serial_number"] = entry['computer_hardware_summary']['serial_number']
                composite_entry["processor"] = entry['computer_hardware_summary']['processor']
                composite_entry["device_manufacturer"] = entry['computer_hardware_summary']['device_manufacturer']
                composite_entry["percent_used"] = entry['computer_disk_summary']['percent_used']
                composite_entry["total_size"] = entry['computer_disk_summary']['total_size']
                composite_list.append(composite_entry)
                #ctr = ctr + 1
                #logging.debug(medesktopcentral_patch_map[str(classification_id)] + " " + str(classification_id))

            properties['connect_medesktopcentral_computer_details'] = composite_list
            response["properties"] = properties
        else:
            response["error"] = "Could not find this endpoint in the Desktop Central Server."
    else:
        logging.debug("NO Resource ID value found..")
        response["error"] = "No Resource ID available to query the Desktop Central server."       
else:
    response["error"] = "API Connection Failed, check configuration."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))