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
    response["succeeded"] = False
    logging.debug("NO value found for connect_kaseyavsa_agentid property..")
    response["troubleshooting"] = "No Agent ID available."
else:
    code, client, session_token = KASEYAVSA_API_LIB.KASEYAVSA_HTTP_CLIENT(credentials, vsa_server_details, ssl_context)
    logging.debug("**ACTION** Login to Kaseya VSA server [{}] returned code [{}]".format(vsa_server_details["address"], code))

    if code == 200:
        patch_action_code, patch_action_results = KASEYAVSA_API_LIB.KASEYAVSA_PATCH_NOW(client, vsa_server_details, session_token, vsa_agent_id)
        logging.debug("**ACTION** API Trigger Patch Scan Now Query returned code [{}] and response [{}]".format(patch_action_code, patch_action_results))

        if patch_action_code == 200 or patch_action_code == 204:
            response["succeeded"] = True
            logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
    else:
        response["succeeded"] = False
        response["troubleshooting"] = "Did not get a 200 code from API connection."
