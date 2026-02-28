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
controller_details = {}
response = {}

credentials["api_key"] = params["connect_controller_api_key_tag"]

controller_details["address"] = params["connect_controller_ip_tag"]
controller_details["port"] = params["connect_ubiquitisdn_controller_port"]
controller_details["site"] = params["connect_ubiquitisdn_site_name"]
controller_details["all_sites"] = params.get("connect_ubiquitisdn_discover_all_sites", "false")
controller_details["ssl_context"] = ssl_context

code, client, headers = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)
logging.debug("Login to Ubiquiti Controller [{}] returned code [{}]".format(controller_details["address"], code))

if code == 200:
    if "mac" in params:
        if params["connect_ubiquitisdn_role"] == "Client":
            # Add if no connect_ubiquitisdn_site defined then set site to default
            # TODO: if discovery is not enabled there is no way to learn connect_ubiquitisdn_site
            #       Need to create a resolve script
            controller_details["site"] = params.get("connect_ubiquitisdn_site", "default")
            mac = ':'.join(params["mac"][i:i + 2] for i in range(0, 12, 2))
            logging.debug("Attempting API Query for MAC [{}]".format(mac))
            try:
                block_code, block_results = UB_API_NONOO.UB_BLOCK_CLIENT(client, controller_details, mac, headers)
                logging.debug("API Query returned code [{}] and response [{}]".format(block_code, block_results))

                if block_code == 200:
                    response["succeeded"] = True
                    logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
            except Exception as e:
                response["succeeded"] = False
                response["troubleshooting"] = "Block client API connection failed: {}".format(str(e))
        else:
            response["succeeded"] = False
            response["troubleshooting"] = "This property only applies to Ubiquiti SDN Discovered Clients."
    else:
        response["succeeded"] = False
        response["troubleshooting"] = "No mac address to query the endpoint."
else:
    response["succeeded"] = False
    response["troubleshooting"] = "API Connection Failed, check configuration."
