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

# Check if original port profile state exists
if "connect_ubiquitisdn_original_port_profile" not in params:
    response["succeeded"] = False
    response["troubleshooting"] = "No original port profile state found. Cannot revert without prior provision action."
    logging.debug("Revert failed: no original state available")
else:
    try:
        original_state = json.loads(params["connect_ubiquitisdn_original_port_profile"])
        
        # Fallback to v1.2.4 parameters if v1.2.6 parameters not present
        credentials["api_key"] = params.get("connect_controller_api_key_tag") or params.get("connect_ubiquitisdn_api_key")
        
        controller_details["address"] = params.get("connect_controller_ip_tag") or params.get("connect_ubiquitisdn_controller_address")
        controller_details["port"] = params["connect_ubiquitisdn_controller_port"]
        # Use endpoint-specific site property, not global config
        controller_details["site"] = params.get("connect_ubiquitisdn_site", "default")
        controller_details["all_sites"] = params.get("connect_ubiquitisdn_discover_all_sites", "false")
        controller_details["ssl_context"] = ssl_context
        controller_details["switch_mac"] = original_state["switch_mac"]
        controller_details["port_index"] = original_state["port_index"]
        controller_details["original_profile_id"] = original_state["profile_id"]
        controller_details["original_dot1x_ctrl"] = original_state.get("dot1x_ctrl")
        
        code, client, headers = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)
        logging.debug("Login to Ubiquiti Controller [{}] returned code [{}]".format(controller_details["address"], code))
        
        if code == 200:
            if params["connect_ubiquitisdn_role"] == "Client":
                try:
                    switch_code, switch_results = UB_API_NONOO.UB_REVERT_PORT_PROFILE(client, controller_details, headers)
                    logging.debug("Revert API returned code [{}] and response [{}]".format(switch_code, switch_results))
                    
                    if switch_code == 200:
                        response["succeeded"] = True
                        # Clear the original state property after successful revert
                        response["properties"] = {
                            "connect_ubiquitisdn_original_port_profile": None
                        }
                        logging.debug("Successfully reverted port profile. Cleared original state.")
                    else:
                        response["succeeded"] = False
                        response["troubleshooting"] = "Revert returned status code: {}".format(switch_code)
                except Exception as e:
                    response["succeeded"] = False
                    response["troubleshooting"] = "Switch revert API connection failed: {}".format(str(e))
            else:
                response["succeeded"] = False
                response["troubleshooting"] = "This action only applies to Ubiquiti SDN Discovered Clients."
        else:
            response["succeeded"] = False
            response["troubleshooting"] = "API Connection Failed, check configuration."
    except Exception as e:
        response["succeeded"] = False
        response["troubleshooting"] = "Failed to parse original state: {}".format(str(e))
        logging.debug("Exception parsing original state: {}".format(str(e)))
