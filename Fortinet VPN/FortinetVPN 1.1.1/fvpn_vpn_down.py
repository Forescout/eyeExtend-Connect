# v1.1.1 Fortigate IPSec / SSL Tunnel Down/Terminate
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

# Values for property.conf passed to params
fortinet_ip = params["connect_fvpn_ip"]
fortigate_serial = params["connect_fvpn_serial"]
fortigate_learnt = params["connect_fvpn_learnt"]
fortinet_type = params["connect_fvpn_type"]
fvpn_p1name = params["connect_fvpn_p1name"]
fvpn_p2name = params["connect_fvpn_p2name"]
fvpn_p2serial = params["connect_fvpn_p2serial"]
fvpn_index = params["connect_fvpn_index"]
fvpn_vdom = params["connect_fvpn_vdom"]


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
        return call_error.code, call_error.reason
    except error.URLError as call_error:
        logging.debug(f"URLError - Errno {call_error.errno}: {call_error.reason}")
        return call_error.errno, call_error.reason
    except Exception as call_error:
        logging.debug(f"Failed to access url: {url}. Error: {call_error}")
        return None, call_error

#################
# FUNCTIONS END #
#################
response = {}

if fortigate_learnt == "FortiGate":
    if fortigate_ip1 == fortinet_ip:
        fortigate_token = fortigate_token1
    if fortigate_ip2 == fortinet_ip:
        fortigate_token = fortigate_token2
    if fortigate_ip3 == fortinet_ip:
        fortigate_token = fortigate_token3
    if fortigate_ip4 == fortinet_ip:
        fortigate_token = fortigate_token4

    # FortiGate
    if fortinet_ip is not None and fortinet_ip != "none" and fortinet_ip != "":
        if fortigate_token is None or fortigate_token == "" or fortigate_token == "none":
            logging.debug ("FortiGate - No API Token")
            response["succeeded"] = False
            response["troubleshooting"] = {}
        else:
            if fortinet_type  == "VPN IPSEC XAuth":
                fgt_vpn_down_url = f"https://{fortinet_ip}/api/v2/monitor/vpn/ipsec/tunnel_down?access_token={fortigate_token}&vdom={fvpn_vdom}"
                fgt_vpn_down_payload = json.dumps({"p1name": fvpn_p1name ,"p2name": fvpn_p2name ,"p2serial": int(fvpn_p2serial) }).encode("utf-8")
            if fortinet_type == "VPN SSL Tunnel":
                fgt_vpn_down_url = f"https://{fortinet_ip}/api/v2/monitor/vpn/ssl/delete?access_token={fortigate_token}&vdom={fvpn_vdom}"
                fgt_vpn_down_payload = json.dumps({"type": "subsession","index": int(fvpn_index)}).encode("utf-8")

            resolve_response = call(fgt_vpn_down_url,fgt_vpn_down_payload,"POST")

            if resolve_response[0] == 200:
                logging.debug (f"FortiGate - VPN Session down with Success {resolve_response[1]}")
                response["succeeded"] = True
            else:
                logging.debug (f"FortiGate - Error - VPN Session down fail {resolve_response[1]} (HTTP Code {resolve_response[0]})")
                response["succeeded"] = False
                response["error"] = f"FortiGate - Error - VPN Session down fail {resolve_response[1]} (HTTP Code {resolve_response[0]})"
else:
    # FortiManager
    if fortimanager_ip is not None and fortimanager_ip != "none" and fortimanager_ip != "":
        fmg_url = "https://" + fortimanager_ip + "/jsonrpc"

        # STEP1 : Login to FMG to retrieve Session Token
        logging.debug ("FortiManager - Retrieve Token")
        fmg_login = {"user": fortimanager_login,"passwd": fortimanager_password}
        fmg_payload_login = json.dumps({"id": 1, "method": "exec", "params": [{"data": fmg_login, "url": "/sys/login/user"}]}).encode("utf-8")
        resolve_response = call (fmg_url,fmg_payload_login,"POST")
        fmg_token = resolve_response[1]["session"]

        # STEP2  : Retrieve all FortiGate Device
        if fmg_token != "":
            logging.debug ("FortiManager - Retrieve Device")
            fmg_params = [{"url": "/dvmdb/adom/" + fortimanager_adom + "/device","filter": [["sn","==",fortigate_serial]]}]
            fmg_payload_device = json.dumps({"id": 1, "method": "get", "params": fmg_params, "session": fmg_token}).encode("utf-8")
            resolve_response = call (fmg_url,fmg_payload_device,"POST")
            fmg_device = resolve_response[1]["result"][0]["data"][0]["name"]
            fmg_targeted_fgt = "adom/" + fortimanager_adom + "/device/" + fmg_device

            # STEP3 : Shutdown VPN Session on FortiGate Device
            if fmg_targeted_fgt is not None or fmg_targeted_fgt != "":
                logging.debug (f"FortiManager - Shutdown VPN Session")
                fmg_data = {}
                if fortinet_type  == "VPN IPSEC XAuth":
                    fgt_vpn_down_payload = {"p1name": fvpn_p1name ,"p2name": fvpn_p2name ,"p2serial": int(fvpn_p2serial)}
                    fgt_vpn_down_ressource = "/api/v2/monitor/vpn/ipsec/tunnel_down?vdom=" + fvpn_vdom
                    fmg_data = {"action": "POST","resource": fgt_vpn_down_ressource,"target": [fmg_targeted_fgt],"payload": fgt_vpn_down_payload}
                if fortinet_type == "VPN SSL Tunnel":
                    fgt_vpn_down_payload = {"type": "subsession","index": int(fvpn_index)}
                    fgt_vpn_down_ressource = "/api/v2/monitor/vpn/ssl/delete?vdom=" + fvpn_vdom
                    fmg_data = {"action": "POST","resource": fgt_vpn_down_ressource,"target": [fmg_targeted_fgt],"payload": fgt_vpn_down_payload}

                fmg_payload = json.dumps({"id": 1, "method": "exec", "params": [{"data": fmg_data, "url": "/sys/proxy/json"}], "session": fmg_token}).encode("utf-8")
                resolve_response = call (fmg_url,fmg_payload,"POST")
                if resolve_response[0] == 200:
                    logging.debug (f"FortiManager - VPN Down Successful {resolve_response[1]}")
                    response["succeeded"] = True
                else:
                    logging.debug (f"FortiManager - Error - VPN Session down fail {resolve_response[1]} (HTTP Code {resolve_response[0]})")
                    response["succeeded"] = False
                    response["error"] = f"FortiManager - Error - VPN Session down fail {resolve_response[1]} (HTTP Code {resolve_response[0]})"