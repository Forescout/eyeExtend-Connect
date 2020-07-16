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

code, client, session_token = KASEYAVSA_API_LIB.KASEYAVSA_HTTP_CLIENT(credentials, vsa_server_details, ssl_context)

log_message = "Attempting to test connectivity to Kaseya VSA server with the following parameters: address={} port={} username={} password={}".format(vsa_server_details["address"], vsa_server_details["port"], credentials["username"], credentials["password"])

if code == 200:

    if not session_token == 0:

        client_code, vsa_assets = KASEYAVSA_API_LIB.KASEYAVSA_LIST_ASSETS(client, vsa_server_details, session_token)
        logging.debug("API Client Query returned code [{}] and response [{}]".format(client_code, vsa_assets))

        if client_code == 200:
                message = "Connection successful. Found {} Kaseya VSA assets".format(len(vsa_assets["Result"]))
                response["succeeded"] = True
                response["result_msg"] = message
        else:
            response["succeeded"] = False
            response["troubleshooting"] = "Did not get a 200 code from List Asset API query. HTTP Error:{} Please check credentials..".format(client_code)
    else:
        response["succeeded"] = False
        response["result_msg"] = "Credentials appears to be wrong or the account provided is disabled."
        response["troubleshooting"] = "Credentials appears to be wrong or the account provided is disabled."
else:
    response["succeeded"] = False
    response["troubleshooting"] = "Did not get a 200 code from API connection."
