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
vsa_server_details = {}
response = {}

credentials["username"] = params["connect_kaseyavsa_username"]
credentials["password"] = params["connect_kaseyavsa_password"]

vsa_server_details["address"] = params["connect_kaseyavsa_server_ipaddress"]
vsa_server_details["port"] = params["connect_kaseyavsa_server_port"]
vsa_agent_id = params.get("connect_kaseyavsa_agentid")

if vsa_agent_id is None:
    logging.debug("NO value found for connect_kaseyavsa_agentid property..")
    response["error"] = "No Agent ID available to query the VSA server."
else:
    code, client, session_token = KASEYAVSA_API_LIB.KASEYAVSA_HTTP_CLIENT(credentials, vsa_server_details, ssl_context)

    kaseyavsa_property_map = {
        "LastPatchScan": "connect_kaseyavsa_last_patch_scan_date"}


    logging.debug("RESOLVE PATCH SCAN DATE: Login to VSA Server [{}] returned code [{}]".format(vsa_server_details["address"], code))

    if code == 200:
        logging.debug("PARAM Agent ID is [{}]".format(vsa_agent_id))
        properties = {}
        _date_time_str = ''

        logging.debug("Attempting Patch Scan Date API Query for Agent ID [{}]".format(vsa_agent_id))
        query_code, query_results = KASEYAVSA_API_LIB.KASEYAVSA_QUERY_LAST_PATCH_SCAN(client, vsa_server_details, session_token, vsa_agent_id)
        patch_details = query_results['Result']
        logging.debug("***PATCH SCAN DATE STATUS...***: Query Code:{} Data:{}".format(query_code,patch_details))

        if query_code == 200:
            _date_time_str = patch_details["LastPatchScan"]
            if _date_time_str is not None:
                _date_time_obj = datetime.datetime.strptime(_date_time_str, '%Y-%m-%dT%H:%M:%S')
                properties['connect_kaseyavsa_last_patch_scan_date'] = int(datetime.datetime.timestamp(_date_time_obj))
                properties['connect_kaseyavsa_has_patch_scan_history'] = True
                response["properties"] = properties
            else:
                properties['connect_kaseyavsa_has_patch_scan_history'] = False
                response["properties"] = properties
                #response["error"] = "No patch scan history found in Kaseya server({}) for this endpoint with Agent ID: {}.".format(vsa_server_details["address"],vsa_agent_id)
                #Note: Property has patch scan history will not be resolved if the Response Object contains "error" or "troubleshooting"
        else:
            properties['connect_kaseyavsa_has_patch_scan_history'] = False
            response["properties"] = properties
            #response["error"] = "No patch scan history found in Kaseya server({}) for this endpoint with Agent ID: {}.".format(vsa_server_details["address"],vsa_agent_id)
            #response["troubleshooting"] = "Did not get a 200 code from Last Patch Scan API query. HTTP Error:{} Please check credentials..".format(query_code)
    else:
        response["error"] = "API Connection Failed, check configuration."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))