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

code, client, session_token = medesktopcentral_API_LIB.medesktopcentral_http_client(credentials, medc_server_details)

medesktopcentral_patch_map = {
    "0": "Unrated",
    "1": "Low",
    "2": "Moderate",
    "3": "Important",
    "4": "Critical"
}

logging.info("POLL PATCH RESOLVE: Login to ME Desktop Central Server [{}] returned code [{}]".format(
    medc_server_details["address"], code))

if code == 200:
    logging.debug("Resource ID is [{}]".format(medc_res_id))
    properties = {}

    if medc_res_id:
        composite_list = []
        logging.debug("Attempting API Query for Resource ID [{}]".format(medc_res_id))
        query_code, query_results = medesktopcentral_API_LIB.medesktopcentral_query_missing_patches(client,
                                                                                                    medc_server_details,
                                                                                                    session_token,
                                                                                                    medc_res_id)
        patch_details = query_results['message_response']['systemreport']
        logging.debug("***PATCH DETAILS...***: Query Code:{} Rec Count:{}".format(query_code, str(len(patch_details))))
        if patch_details:
            for entry in patch_details:
                if "INSTALLED" not in entry['patch_affected_status_label']:
                    classification_id = entry['severity']
                    composite_entry = {}
                    composite_entry["severity"] = medesktopcentral_patch_map[str(classification_id)]
                    composite_entry["bulletin_id"] = entry['bulletin_id']
                    composite_entry["patch_description"] = entry['patch_description']
                    composite_entry["vendor_name"] = entry['vendor_name']
                    composite_list.append(composite_entry)

            properties['connect_medesktopcentral_missing_patches'] = composite_list
            properties['connect_medesktopcentral_patch_compliant'] = False if composite_list else True
            response["properties"] = properties
        else:
            properties['connect_medesktopcentral_patch_compliant'] = True
            response["properties"] = properties
            logging.debug("**PATCH COMPLIANT** - [{}]".format(medc_res_id))

    else:
        logging.debug("NO Resource ID value found.")
        response["error"] = "No Resource ID available to query the Desktop Central server."
else:
    response["error"] = "API Connection Failed, check configuration."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
