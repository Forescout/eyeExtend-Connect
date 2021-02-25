# v1.0.3 Fortinet VPN Test
# Keith Gilbert / Cedric Antoine

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

import json
import re
from urllib import request, error

# Values for system.conf passed to params
fortigate_ip1 = params.get("connect_fvpn_fip1")
fortigate_ip2 = params.get("connect_fvpn_fip2")
fortigate_ip3 = params.get("connect_fvpn_fip3")
fortigate_ip4 = params.get("connect_fvpn_fip4")
fortigate_token1 = params.get("connect_fvpn_token1")
fortigate_token2 = params.get("connect_fvpn_token2")
fortigate_token3 = params.get("connect_fvpn_token3")
fortigate_token4 = params.get("connect_fvpn_token4")
fortimanager_ip = params.get("connect_fvpn_fmg_ip")
fortimanager_login = params.get("connect_fvpn_fmg_login")
fortimanager_password = params.get("connect_fvpn_fmg_password")
fortimanager_adom = params.get("connect_fvpn_fmg_adom")

#############
# FUNCTIONS #
#############
def call (url,data,method):
    try:
        req = request.Request(url, data=data, method=method)
        resp = request.urlopen(req, context=ssl_context)
        if resp.getcode() == 200:
            resolve_response = json.loads(resp.read())
        return resp.getcode(),resolve_response
    except error.HTTPError as call_error:
        code = call_error.code
        reason = call_error.reason
        return code,reason
    except error.URLError as call_error:
        reason = call_error.reason
        return reason


def search(list, platform):
    for i in range(len(list)):
        if list[i] == platform:
            return True
    return False
#################
# FUNCTIONS END #
#################

# Map FortiGate IP and Token to list
fortigate_ip = []
fortigate_token = []
counter = 0
if fortigate_ip1 is not None and fortigate_ip1 != "" and fortigate_token1 != "none" and fortigate_token1 != "":
    fortigate_ip.append(fortigate_ip1)
    fortigate_token.append(fortigate_token1)
    counter += 1
if fortigate_ip2 is not None and fortigate_ip2 != "" and fortigate_token2 != "none" and fortigate_token2 != "":
    fortigate_ip.append(fortigate_ip2)
    fortigate_token.append(fortigate_token2)
    counter += 1
if fortigate_ip3 is not None and fortigate_ip3 != "" and fortigate_token3 != "none" and fortigate_token3 != "":
    fortigate_ip.append(fortigate_ip3)
    fortigate_token.append(fortigate_token3)
    counter += 1
if fortigate_ip4 is not None and fortigate_ip4 != "" and fortigate_token4 != "none" and fortigate_token4 != "":
    fortigate_ip.append(fortigate_ip4)
    fortigate_token.append(fortigate_token4)
    counter += 1


result_msg = []

# FortiGate
if counter >= 1:
    for i in range(0, counter):
        current_ip = fortigate_ip[i]
        check_ip = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:[1-9][0-9]{0,3}|:[1-5][0-9]{4}|:6[0-4][0-9]{3}|:65[0-4][0-9]{2}|:655[0-2][0-9]|:6553[0-5])?$",current_ip)
        if check_ip:
            fgt_ipsec_url = f"https://{fortigate_ip[i]}/api/v2/monitor/vpn/ipsec?access_token={fortigate_token[i]}"
            fgt_ssl_url = f"https://{fortigate_ip[i]}/api/v2/monitor/vpn/ssl?access_token={fortigate_token[i]}"
            resolve_response_ipsec = call(fgt_ipsec_url,{},"GET")
            resolve_response_ssl = call(fgt_ssl_url,{},"GET")
            if resolve_response_ipsec[0] != 200 and resolve_response_ssl[0] !=200:
                logging.debug(f"FortiGate - {fortigate_ip[i]} - Error : Connection Failed, Check API Token and IP")
                result = f"FortiGate - {fortigate_ip[i]} - Error : Connection Failed, Check API Token and IP"
                result_msg.append(result)
            else:
                if resolve_response_ipsec[0] == 200 and resolve_response_ssl[0] == 200:
                    fgt_serial = str(resolve_response_ipsec[1]["serial"])
                    fgt_version = str(resolve_response_ipsec[1]["version"]) + "." + str(resolve_response_ipsec[1]["build"])
                    result = f"FortiGate - {fortigate_ip[i]} - Connection Successful, Serial={fgt_serial} version={fgt_version}"
                    result_msg.append(result)
                else:
                    if resolve_response_ipsec[0] == 200 and resolve_response_ssl[0] != 200:
                       result = f"FortiGate - {fortigate_ip[i]} - Error: VPN IPSEC Connection Successful BUT SSL Fail"
                       result_msg.append(result)
                    if resolve_response_ipsec[0] != 200 and resolve_response_ssl[0] == 200:
                       result = f"FortiGate - {fortigate_ip[i]} - Error: VPN SSL Connection Successful BUT IPSEC Fail"
                       result_msg.append(result)
        else:
            logging.debug(f"FortiGate - Error: Not an IP address in FortiGate [{i+1}] IP field")
            result = f"FortiGate - Error: Not an IP address in FortiGate[{i+1}] IP field"
            result_msg.append(result)


# FortiManager section
if fortimanager_ip is not None and fortimanager_ip != "none" and fortimanager_ip != "":
    check_ip = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:[1-9][0-9]{0,3}|:[1-5][0-9]{4}|:6[0-4][0-9]{3}|:65[0-4][0-9]{2}|:655[0-2][0-9]|:6553[0-5])?$",fortimanager_ip)
    if check_ip:

        # STEP1 : Login to FMG to retrieve Session Token
        logging.debug("FortiManager - STEP 1 - Login")
        fmg_url = f"https://{fortimanager_ip}/jsonrpc"
        fmg_login = {"user": fortimanager_login,"passwd": fortimanager_password}
        fmg_payload_login = json.dumps({"id": 1, "method": "exec", "params": [{"data": fmg_login, "url": "/sys/login/user"}]}).encode("utf-8")
        resolve_response = call (fmg_url,fmg_payload_login,"POST")
        if resolve_response[0] == 200 and resolve_response[1]["result"][0]["status"]["code"] == 0:
            fmg_token = resolve_response[1]["session"]

            # STEP2  : Retrieve all FortiGate Device
            logging.debug("FortiManager - STEP 2 - Retrieve couple FGT/VDOM device for each ADOM")
            fmg_fgt_list = []
            vdom_list = ["root"]
            if fmg_token != "" or fmg_token != None :
                fmg_adom_list = fortimanager_adom.split('\n')
                # For each ADOM retrieve all the Fortigate device
                for j in range(len(fmg_adom_list)) :
                    fmg_params = [{"url": "/dvmdb/adom/" + fmg_adom_list[j] + "/device"}]
                    fmg_payload_device = json.dumps({"id": 1, "method": "get", "params": fmg_params, "session": fmg_token}).encode("utf-8")
                    resolve_response = call (fmg_url,fmg_payload_device,"POST")
                    # Check if ADOM exist
                    if resolve_response[1]["result"][0]["status"]["code"] == 0:
                        # For each Fortigate, and for each VDOM inside the Fortigate
                        for i in range(len(resolve_response[1]["result"][0]["data"])):
                            for k in range(len(resolve_response[1]["result"][0]["data"][i]["vdom"])):
                                # Store information into "fmg_fgt_list", 1 FGT(1 VDOM) = 1 entry / 1 FGT(2 VDOM) = 2 entries / 2 FGT(2 VDOM each) = 4 entries
                                fgt ={}
                                vdom = str(resolve_response[1]["result"][0]["data"][i]["vdom"][k]["name"])
                                fmg_fgt_name = resolve_response[1]["result"][0]["data"][i]["name"]
                                fmg_fgt_ip = str(resolve_response[1]["result"][0]["data"][i]["ip"])
                                fgt["vdom"] = vdom
                                fgt["target"] = "adom/" + fmg_adom_list[j] + "/device/" + fmg_fgt_name
                                fgt["sn"] = str(resolve_response[1]["result"][0]["data"][i]["sn"])
                                fgt["name"] = str(fmg_fgt_name)
                                fgt["ip"] = fmg_fgt_ip
                                fmg_fgt_list.append(fgt)
                                result = f"FortiManager - {fmg_fgt_name}({fmg_fgt_ip}) VDOM: {vdom}) Connection Successful"
                                result_msg.append(result)
                                logging.debug(f"FortiManager - STEP 2 - ADOM:{fmg_adom_list[j]} FortiGate:{fmg_fgt_name} (vdom {vdom})")
                    else:
                        message = resolve_response[1]["result"][0]["status"]["message"]
                        logging.debug(f"FortiManager Test - STEP 2 - Error on ADOM {fmg_adom_list[j]} ")
                        result = f"FortiManager - Error: ADOM {fmg_adom_list[j]} doesn't exist"
                        result_msg.append(result)

            # LAST STEP : Logout from FMG
            logging.debug("FortiManager - LAST STEP - Logout")
            fmg_payload_logout = json.dumps({"id": 1, "method": "exec", "params": [{"url": "/sys/logout"}], "session": fmg_token}).encode("utf-8")
            resolve_response = call (fmg_url,fmg_payload_logout,"POST")
            fmg_msg = resolve_response[1]["result"][0]["status"]["message"]
            logging.debug(f"FortiManager - LAST STEP - Logout {fmg_msg} - HTTP Message: {resolve_response[1]}")
        else:
            logging.debug("FortiManager - Error: Connection Failed: Check IP and/or credentials")
            result = f"FortiManager - Error: Connection Failed, Check IP and/or credentials"
            result_msg.append(result)
    else:
        logging.debug("FortiManager - Error: Not an IP address in IP field")
        result = f"FortiManager - Error: Not an IP address in FortiManager IP field"
        result_msg.append(result)

# Final Response
response = {}
fail = False
for result in result_msg:
    if "Error" in result:
        fail = True
    if result == "":
        fail = True
# Display
result_tmp = ""
for i in range(len(result_msg)):
    result_tmp += result_msg[i] + "\n"
logging.debug(f"Result: {result_msg}")
# If No Error
if fail != True:
    response["succeeded"] = True
    response["result_msg"] = result_tmp
else:
    response["succeeded"] = False
    response["result_msg"] = result_tmp