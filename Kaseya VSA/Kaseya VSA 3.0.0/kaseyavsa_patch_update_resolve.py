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

    kaseyavsa_patch_map = {
    "100": "Security Update - Critical (High Priority)",
    "101": "Security Update - Important (High Priority)",
    "102": "Security Update - Moderate (High Priority)",
    "103": "Security Update - Low (High Priority)",
    "104": "Security Update - Non-rated (High Priority)",
    "110": "Critical Update (High Priority)",
    "120": "Update Rollup (High Priority)",
    "200": "Service Pack (Optional - Software)",
    "210": "Update (Optional - Software)",
    "220": "Feature Pack (Optional - Software)",
    "230": "Tool (Optional - Software)",
    "900": "Unclassified"
    }

    logging.info("POLL PATCH RESOLVE: Login to VSA Server [{}] returned code [{}]".format(vsa_server_details["address"], code))

    if code == 200:
        logging.debug("PARAM Agent ID is [{}]".format(vsa_agent_id))
        properties = {}

        composite_list = []
        logging.debug("Attempting API Query for Agent ID [{}]".format(vsa_agent_id))
        query_code, query_results = KASEYAVSA_API_LIB.KASEYAVSA_QUERY_MISSING_PATCHES(client, vsa_server_details, session_token, vsa_agent_id)
        patch_details = query_results['Result']
        logging.debug("***PATCH DETAILS...***: Query Code:{} Rec Count:{}".format(query_code,str(len(patch_details))))
        ctr = 0
        if not len(patch_details) == 0:
            for entry in patch_details:
                classification_id = patch_details[ctr]['UpdateClassification']
                composite_entry={}
                composite_entry["update_classification"] = kaseyavsa_patch_map[str(classification_id)]
                composite_entry["kb_article"] = patch_details[ctr]['KBArticle']
                composite_entry["update_title"] = patch_details[ctr]['Description']
                composite_entry["product_name"] = patch_details[ctr]['Product']
                composite_list.append(composite_entry)
                ctr = ctr + 1
                logging.debug(kaseyavsa_patch_map[str(classification_id)] + " " + str(classification_id))

            properties['connect_kaseyavsa_patch_update'] = composite_list
            properties['connect_kaseyavsa_patch_compliant'] = False
            response["properties"] = properties
        else:
            #response["error"] = "Could not find this endpoint in the Kaseya VSA Server."
            properties['connect_kaseyavsa_patch_compliant'] = True
            response["properties"] = properties
            logging.debug("**PATCH COMPLIANT** - [{}]".format(vsa_agent_id))
    else:
        response["error"] = "API Connection Failed, check configuration."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))