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
client_wired_details = {}
client_wired_details = json.loads(params["connect_ubiquitisdn_client_wired_details"])

# Fallback to v1.2.4 parameters if v1.2.6 parameters not present
credentials["api_key"] = params.get("connect_controller_api_key_tag") or params.get("connect_ubiquitisdn_api_key")

controller_details["address"] = params.get("connect_controller_ip_tag") or params.get("connect_ubiquitisdn_controller_address")
controller_details["port"] = params["connect_ubiquitisdn_controller_port"]
# Use endpoint-specific site property, not global config
controller_details["site"] = params.get("connect_ubiquitisdn_site", "default")
controller_details["all_sites"] = params.get("connect_ubiquitisdn_discover_all_sites", "false")
controller_details["ssl_context"] = ssl_context
controller_details["switch_mac"] = client_wired_details["wired_switch_mac"]
controller_details["port_index"] = client_wired_details["wired_switch_port"]
controller_details["new_profile_name"] = params["connect_ubiquitisdn_profile_name"]
controller_details["dot1x_state"] = params["connect_ubiquitisdn_dot1x_state"].lower()

code, client, headers = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)
logging.debug("Login to Ubiquiti Controller [{}] returned code [{}]".format(controller_details["address"], code))

if code == 200:
    if params["connect_ubiquitisdn_role"] == "Client":
        try:

            switch_code, switch_results = UB_API_NONOO.UB_PROVISON_PORT_PROFILE(client, controller_details, headers)
            logging.debug("API Query returned code [{}] and response [{}]".format(switch_code, switch_results))

            if switch_code == 200:
                response["succeeded"] = True
                
                # NEW: Store original state for revert capability
                if isinstance(switch_results, dict) and '_original_state' in switch_results:
                    original_state = switch_results['_original_state']
                    response["properties"] = {
                        "connect_ubiquitisdn_original_port_profile": json.dumps(original_state)
                    }
                    logging.debug("Stored original profile state: {}".format(original_state))
                
                logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
        except Exception as e:
            response["succeeded"] = False
            response["troubleshooting"] = "Switch client API connection failed: {}".format(str(e))
    else:
        response["succeeded"] = False
        response["troubleshooting"] = "This property only applies to Ubiquiti SDN Discovered Clients."
else:
    response["succeeded"] = False
    response["troubleshooting"] = "API Connection Failed, check configuration."
