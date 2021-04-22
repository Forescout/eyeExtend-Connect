# v1.1.0 Fortigate VPN Poll
# Keith Gilbert / Cedric Antoine

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

import json
import re
import time
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

endpoints = []


#############
# FUNCTIONS #
#############
def call(url, data, method):
    try:
        req = request.Request(url, data=data, method=method)
        resp = request.urlopen(req, context=ssl_context)
        if resp.getcode() == 200:
            resolve_response = json.loads(resp.read())
        return resp.getcode(), resolve_response
    except error.HTTPError as call_error:
        logging.debug(f"HTTPError - Code {call_error.code}: {call_error.reason}")
        response["succeeded"] = False
        response["error"] = f"HTTPError - Code {call_error.code}: {call_error.reason}"
        return call_error.code, call_error.reason
    except error.URLError as call_error:
        logging.debug(f"URLError - Reason: {call_error.reason}")
        response["succeeded"] = False
        response["error"] = f"URLError - Reason: {call_error.reason}"


def endpoints_vpn_ipsec (count_vpn, resolve_response, fgt_information):
    # For each endpoint
    for i in range(0, count_vpn):
        endpoint = {}
        return_results = resolve_response[i]
        if return_results["type"] == "dialup":
            try:
                proxyid = str(return_results["proxyid"][0]["proxy_dst"])
                s = proxyid.rfind("subnet") + 10
                max_ip = proxyid[s:s+15]
                e = max_ip.rfind("-")
                # Create Endpoint entry
                endpoint["ip"] = max_ip[:e]
                properties = {}
                properties["connect_fvpn_eip"] = return_results["rgwy"]
                properties["connect_fvpn_user"] = return_results["xauth_user"]
                properties["connect_fvpn_type"] = "VPN IPSEC XAuth"
                properties["connect_fvpn_p1name"] = return_results["name"]
                properties["connect_fvpn_p2name"] = return_results["proxyid"][0]["p2name"]
                properties["connect_fvpn_p2serial"] = return_results["proxyid"][0]["p2serial"]
                properties["connect_fvpn_ip"] = fgt_information[1]
                properties["connect_fvpn_learnt"] = fgt_information[5]
                properties["connect_fvpn_hostname"] = fgt_information[0]
                properties["connect_fvpn_vdom"] = fgt_information[4]
                properties["connect_fvpn_serial"] = fgt_information[2]
                properties["connect_fvpn_version"] = fgt_information[3]
                properties["connect_fvpn_index"] = ""
                properties["connect_fvpn_poll"] = ctime
                endpoint["properties"] = properties
                endpoints.append(endpoint)
            except :
                logging.info(f"No correct VPN IPSEC User")
                return


def endpoints_vpn_ssl (count_vpn, resolve_response, fgt_information):
        # For each endpoint
    for i in range(0, count_vpn):
        endpoint = {}
        return_results = resolve_response[i]
        try:
            if return_results["subsessions"][0]["mode"] == "Tunnel":
                # Create Endpoint entry
                endpoint["ip"] = return_results["subsessions"][0]["aip"]
                properties = {}
                properties["connect_fvpn_eip"] = return_results["remote_host"]
                properties["connect_fvpn_user"] = return_results["user_name"]
                properties["connect_fvpn_type"] = "VPN SSL Tunnel"
                properties["connect_fvpn_index"] = str(return_results["subsessions"][0]["index"])
                properties["connect_fvpn_ip"] = fgt_information[1]
                properties["connect_fvpn_learnt"] = fgt_information[5]
                properties["connect_fvpn_hostname"] = fgt_information[0]
                properties["connect_fvpn_vdom"] = fgt_information[4]
                properties["connect_fvpn_serial"] = fgt_information[2]
                properties["connect_fvpn_version"] = fgt_information[3]
                properties["connect_fvpn_p1name"] = ""
                properties["connect_fvpn_p2name"] = ""
                properties["connect_fvpn_p2serial"] = ""
                properties["connect_fvpn_poll"] = ctime
                endpoint["properties"] = properties
                endpoints.append(endpoint)
        except :
            logging.info(f"No correct VPN SSL User")
    return

def fmg_endpoints_vpn (vpn_response, fmg_fgt_list, mode):
    count_fgt = len(vpn_response)
    # For each Fortigate
    for i in range(0, count_fgt):
        # Check if Each FGT return Status success code and results not empty
        if vpn_response[i]["status"]["code"] == 0 and vpn_response[i]["response"]["results"] != []:
            endpoints_response = vpn_response[i]["response"]["results"]
            fgt_information=[]
            count_fgt_list = len(fmg_fgt_list)
            # For each users in the Fortigate
            for j in range(0, count_fgt_list):
                # Put information about the FortiGate
                if str(vpn_response[i]["response"]["serial"]) == fmg_fgt_list[j]["sn"] and vpn_response[i]["response"]["vdom"] == fmg_fgt_list[j]["vdom"]:
                    fgt_information.append(str(fmg_fgt_list[j]["name"]))
                    fgt_information.append(str(fmg_fgt_list[j]["ip"]))
                    fgt_information.append(str(vpn_response[i]["response"]["serial"]))
                    fgt_information.append(str(vpn_response[i]["response"]["version"]) + "." + str(vpn_response[i]["response"]["build"]))
                    fgt_information.append(str(fmg_fgt_list[j]["vdom"]))
                    fgt_information.append("FortiManager")
            count_vpn = len(endpoints_response)
            if mode == "IPSEC":
                endpoints_vpn_ipsec(count_vpn,endpoints_response,fgt_information)
            if mode == "SSL":
                endpoints_vpn_ssl(count_vpn,endpoints_response,fgt_information)
    return


def search(list, platform):
    for i in range(len(list)):
        if list[i] == platform:
            return True
    return False

#################
# FUNCTIONS END #
#################

# Get time for poll
ct = time.time()
ctime = str(ct).split('.')[0]

# map FortiGate IP and Token to list
fortigate_ip = []
fortigate_token = []
counter = 0
if fortigate_ip1 is not None and fortigate_ip1 != "" and fortigate_token1 is not None and  fortigate_token1 != "none" and fortigate_token1 != "":
    fortigate_ip.append(fortigate_ip1)
    fortigate_token.append(fortigate_token1)
    counter += 1
if fortigate_ip2 is not None and fortigate_ip2 != "" and fortigate_token2 is not None and fortigate_token2 != "none" and fortigate_token2 != "":
    fortigate_ip.append(fortigate_ip2)
    fortigate_token.append(fortigate_token2)
    counter += 1
if fortigate_ip3 is not None and fortigate_ip3 != "" and fortigate_token3 is not None and fortigate_token3 != "none" and fortigate_token3 != "":
    fortigate_ip.append(fortigate_ip3)
    fortigate_token.append(fortigate_token3)
    counter += 1
if fortigate_ip4 is not None and fortigate_ip4 != "" and fortigate_token4 is not None and fortigate_token4 != "none" and fortigate_token4 != "":
    fortigate_ip.append(fortigate_ip4)
    fortigate_token.append(fortigate_token4)
    counter += 1

response ={}
resolve_response_ipsec = {}
resolve_response_ssl = {}

# FortiGate
if counter >= 1:
    for v in range(0, counter):
        current_fortigate = fortigate_ip[v]
        check_ip = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:[1-9][0-9]{0,3}|:[1-5][0-9]{4}|:6[0-4][0-9]{3}|:65[0-4][0-9]{2}|:655[0-2][0-9]|:6553[0-5])?$",current_fortigate)
        if check_ip:
            fgt_vdom_url = f"https://{fortigate_ip[v]}/api/v2/cmdb/system/vdom?access_token={fortigate_token[v]}"
            fgt_global_url = f"https://{fortigate_ip[v]}/api/v2/cmdb/system/global?access_token={fortigate_token[v]}"
            resolve_response_global = call(fgt_global_url,{},"GET")
            resolve_response_vdom = call(fgt_vdom_url,{},"GET")

            # VDOM JSON Parsing
            fgt_vdom_list = []
            if resolve_response_vdom[0] == 200:
                num_fgt_vdom = len(resolve_response_vdom[1]["results"])
                for x in range(num_fgt_vdom):
                    current_vdom = resolve_response_vdom[1]["results"][x-1]["name"]
                    logging.debug(f"fortiGate VDOM - {current_vdom}")
                    fgt_vdom_list.append(current_vdom)
            else:
                logging.debug(f"Check FortiGate IP and API key has access to VDOM")

            # Global JSON Parsing
            if resolve_response_global[0] == 200:
                fgt_information=[]
                try:
                    #  "hostname" only exists on non-VDOM = try..except to catch vdom mode and set hostname
                    fgt_information.append(str(resolve_response_global[1]["results"]["hostname"]))
                except:
                    fgt_name = f"(VDOM){current_fortigate}"
                    fgt_information.append(str(fgt_name))
                fgt_information.append(str(current_fortigate))
                fgt_information.append(str(resolve_response_global[1]["serial"]))
                fgt_information.append(str(resolve_response_global[1]["version"]) + "." + str(resolve_response_global[1]["build"]))

            for w in range(0, num_fgt_vdom):
                current_vdom = fgt_vdom_list[w]
                fgt_ipsec_url = f"https://{fortigate_ip[v]}/api/v2/monitor/vpn/ipsec?access_token={fortigate_token[v]}&vdom={current_vdom}"
                fgt_ssl_url = f"https://{fortigate_ip[v]}/api/v2/monitor/vpn/ssl?access_token={fortigate_token[v]}&vdom={current_vdom}"
                resolve_response_ipsec = call(fgt_ipsec_url,{},"GET")
                resolve_response_ssl = call(fgt_ssl_url,{},"GET")
                fgt_information.append(str(current_vdom))
                fgt_information.append("FortiGate")

                # IPSEC JSON Parsing
                if resolve_response_ipsec[0] == 200:
                    logging.info("FortiGate - Retrieve VPN IPSEC Users")
                    resolve_response = resolve_response_ipsec[1]["results"]
                    logging.debug(resolve_response)
                    count_vpn = len(resolve_response)
                    endpoints_vpn_ipsec(count_vpn,resolve_response,fgt_information)

                # SSL JSON Parsing
                if resolve_response_ssl[0] == 200:
                    logging.info("FortiGate - Retrieve VPN SSL Users")
                    resolve_response = resolve_response_ssl[1]["results"]
                    logging.debug(resolve_response)
                    count_vpn = len(resolve_response)
                    endpoints_vpn_ssl(count_vpn,resolve_response,fgt_information)

                del fgt_information[5]
                del fgt_information[4]
        else:
            logging.debug(f"FortiGate - Error: Not an IP address in FortiGate [{v+1}] IP field")

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
            if fmg_token is not None and fmg_token != "":
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
                                fgt["vdom"] = vdom
                                fgt["target"] = "adom/" + fmg_adom_list[j] + "/device/" + fmg_fgt_name
                                fgt["sn"] = str(resolve_response[1]["result"][0]["data"][i]["sn"])
                                fgt["name"] = str(fmg_fgt_name)
                                fgt["ip"] = str(resolve_response[1]["result"][0]["data"][i]["ip"])
                                fmg_fgt_list.append(fgt)
                               # Store into vdom_list only for new vdom, STEP 3 will use this list to aggregate fmg call, grouped by VDOM
                                if not search(vdom_list, vdom):
                                    vdom_list.append(vdom)
                    else:
                        message = resolve_response[1]["result"][0]["status"]["message"]
                        logging.debug(f"FortiManager - STEP 2 - Error: ADOM {fmg_adom_list[j]} ")

                # STEP3 : Retrieve all VPN Sessions
                if fmg_fgt_list is not None and fmg_fgt_list != "":
                    logging.debug(f"FortiManager - STEP 3 - Retrieve VPN Sessions")
                    # Execute Call API for each VDOM
                    for i in range(len(vdom_list)) :
                        fmg_targeted_fgt = []
                        for j in range(len(fmg_fgt_list)):
                            # Add Fortigate into fmg_targeted_fgt only if VDOM match the vdom_list
                            if vdom_list[i] == str(fmg_fgt_list[j]["vdom"]) :
                                fmg_targeted_fgt.append(fmg_fgt_list[j]["target"])
                        # VPN IPSEC Call
                        fmg_data_data_ipsec = {"action": "get","resource": "/api/v2/monitor/vpn/ipsec?vdom=" + vdom_list[i],"target": fmg_targeted_fgt}
                        fmg_payload_ipsec = json.dumps({"id": 1, "method": "exec", "params": [{"data": fmg_data_data_ipsec, "url": "/sys/proxy/json"}], "session": fmg_token}).encode("utf-8")
                        resolve_response_ipsec = call (fmg_url,fmg_payload_ipsec,"POST")
                        # VPN SSL Call
                        fmg_data_data_ssl = {"action": "get","resource": "/api/v2/monitor/vpn/ssl?vdom=" + vdom_list[i],"target": fmg_targeted_fgt}
                        fmg_payload_ssl = json.dumps({"id": 2, "method": "exec", "params": [{"data": fmg_data_data_ssl, "url": "/sys/proxy/json"}], "session": fmg_token}).encode("utf-8")
                        resolve_response_ssl = call (fmg_url,fmg_payload_ssl,"POST")

                        # IPSEC JSON Parsing
                        if resolve_response_ipsec[0] == 200:
                            logging.debug(f"FortiManager - STEP 3 - VDOM {vdom_list[i]} - IPSEC Users ")
                            vpn_response = resolve_response_ipsec[1]["result"][0]["data"]
                            fmg_endpoints_vpn (vpn_response, fmg_fgt_list,"IPSEC")
                        # SSL JSON Parsing
                        if resolve_response_ssl[0] == 200:
                            logging.debug(f"FortiManager - STEP 3 - VDOM {vdom_list[i]} - SSL Users ")
                            vpn_response = resolve_response_ssl[1]["result"][0]["data"]
                            fmg_endpoints_vpn (vpn_response, fmg_fgt_list,"SSL")

            # LAST STEP : Logout from FMG
            logging.debug("FortiManager - LAST STEP - Logout")
            fmg_payload_logout = json.dumps({"id": 1, "method": "exec", "params": [{"url": "/sys/logout"}], "session": fmg_token}).encode("utf-8")
            resolve_response = call (fmg_url,fmg_payload_logout,"POST")
            fmg_msg = resolve_response[1]["result"][0]["status"]["message"]
            logging.debug(f"FortiManager - LAST STEP - Logout {fmg_msg} - HTTP Message: {resolve_response[1]}")
        else:
            logging.debug("FortiManager - Error: Connection Failed, Check IP and/or credentials")
    else:
        logging.debug("FortiManager - Error: Not an IP address in IP field")

# Send to FS
logging.debug(f"Final Endpoints: {endpoints}")
response["endpoints"] = endpoints