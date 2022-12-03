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

#global global_connect_medesktopcentral_session_token

credentials = {}
medc_server_details = {}
response = {}

credentials["username"] = params["connect_medesktopcentral_username"]
credentials["password"] = params["connect_medesktopcentral_password"]

medc_server_details["address"] = params["connect_medesktopcentral_server_ipaddress"]
medc_server_details["port"] = params["connect_medesktopcentral_server_port"]

code, client, session_token, data = medesktopcentral_api_lib.medesktopcentral_http_client(credentials, medc_server_details)

log_message = "Attempting test connectivity to ManageEngine Desktop Central server with the following parameters: address={} port={} username={} password={}".format(medc_server_details["address"], medc_server_details["port"], credentials["username"], credentials["password"])
logging.debug(log_message)

if code == 200:

    if not session_token == 0:
        medc_server_details["session_token"] = params.get("connect_medesktopcentral_session_token")
        logging.debug("TEST SCRIPT SESSION TOKEN:[{}] DATA:[{}]".format(session_token,data))

        client_code, medc_assets = medesktopcentral_api_lib.medesktopcentral_check_summary(client, medc_server_details, session_token)
        logging.debug("API Client Query returned code [{}] and response [{}]".format(client_code, medc_assets))

        if client_code == 200:
                message = "Connection to ManageEngine Desktop Central server with IP address {} is successful. ".format(medc_server_details["address"])
                response["succeeded"] = True
                response["result_msg"] = message
        else:
            response["succeeded"] = False
            response["troubleshooting"] = "Did not get a 200 code from List Asset API query. HTTP Error:{} Please check credentials..".format(client_code)
    else:    
        response["succeeded"] = False
        response["result_msg"] = data["error_description"]
        response["troubleshooting"] = data["error_description"]
else:
    response["succeeded"] = False
    response["troubleshooting"] = "Did not get a 200 code from API connection."
