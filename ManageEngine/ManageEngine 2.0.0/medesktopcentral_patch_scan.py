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
res_id = params["connect_medesktopcentral_resource_id"]

code, client, session_token = medesktopcentral_API_LIB.medesktopcentral_http_client(credentials, medc_server_details)

logging.debug(
    "INITIATE PATCH SCAN: Login to ME Desktop Central Server [{}] returned code [{}]  Resource ID [{}]".format(
        medc_server_details["address"], code, res_id))

if code == 200:
    patch_action_code, patch_action_results = medesktopcentral_API_LIB.medesktopcentral_patch_scan(client,
                                                                                                   medc_server_details,
                                                                                                   session_token,
                                                                                                   res_id)
    logging.debug(
        "**ACTION** Attempted API Trigger Initiate Patch Scan Query returned code [{}] and response [{}]".format(
            patch_action_code, patch_action_results))

    if patch_action_code == 200:
        response["succeeded"] = True
        logging.debug("API call to initiate patch scan in ManageEngine successful, please verify patch scan schedule in ME. response=[{}]".format(
                response))
    else:
        response["succeeded"] = False
        logging.debug("API Action FAILED. response=[{}]".format(response))
else:
    response["succeeded"] = False
    response["troubleshooting"] = "Did not get a 200 code from API connection."
