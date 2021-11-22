"""
Copyright © 2021 Forescout Technologies, Inc.

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

response = {}

# Requests Proxy
is_proxy_enabled = params.get("connect_proxy_enable")
if is_proxy_enabled == "true":
    proxy_ip = params.get("connect_proxy_ip")
    proxy_port = params.get("connect_proxy_port")
    proxy_user = params.get("connect_proxy_username")
    proxy_pass = params.get("connect_proxy_password")
    if not proxy_user:
        proxy_url = f"https://{proxy_ip}:{proxy_port}"
        proxies = {"https" : proxy_url}
        logging.debug ("Proxy enabled / no user")
    else:
        proxy_url = f"https://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
        proxies = {"https" : proxy_url}
        logging.debug ("Proxy enabled / user")
else:
    logging.debug ("Proxy disabled")
    proxies = None

# Values from system.conf
server = params["connect_kaseyavsa_server_ipaddress"]
port = params["connect_kaseyavsa_server_port"]

# Additional values
vsa_agent_id = params.get("connect_kaseyavsa_agentid")

token = params["connect_authorization_token"]

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

logging.info("POLL PATCH RESOLVE: Login to VSA Server [{}]".format(server))

if token != "":
    logging.debug("PARAM Agent ID is [{}]".format(vsa_agent_id))
    properties = {}

    if vsa_agent_id is not None:
        composite_list = []
        logging.debug("Attempting API Query for Agent ID [{}]".format(vsa_agent_id))
        query_code, query_results = KASEYAVSA_API_LIB.KASEYAVSA_QUERY_MISSING_PATCHES(server, port, token, vsa_agent_id, proxies)
        patch_details = query_results['Result']
        patch_id_list = ''
        logging.debug("***PATCH DETAILS...***: Query Code: {} Rec Count: {}".format(query_code,query_results['TotalRecords']))
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
                if patch_details[ctr]['UpdateClassification'] != "900": #900 - Unclassified
                    patch_id_list = patch_id_list + '{}, '.format(str(patch_details[ctr]['PatchDataId']))
                    
                ctr = ctr + 1
                logging.debug(kaseyavsa_patch_map[str(classification_id)] + " " + str(classification_id))

            properties['connect_kaseyavsa_patch_update'] = composite_list
            properties['connect_kaseyavsa_missing_patchids'] = patch_id_list
            properties['connect_kaseyavsa_patch_compliant'] = False
            response["properties"] = properties
        else:
            #response["error"] = "Could not find this endpoint in the Kaseya VSA Server."
            properties['connect_kaseyavsa_patch_compliant'] = True
            response["properties"] = properties
            logging.debug("**PATCH COMPLIANT** - [{}]".format(vsa_agent_id))

    else:
        logging.debug("NO value found for connect_kaseyavsa_agentid property..")
        response["error"] = "No Agent ID available to query the VSA server."       
else:
    response["error"] = "API Connection Failed, check configuration."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))