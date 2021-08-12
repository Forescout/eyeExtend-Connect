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

from connectproxyserver import ConnectProxyServer, ProxyProtocol
from urllib import request
from urllib.request import HTTPError, URLError
import logging
import json

def get_sonar_status(bash_status):
    """
    map sonar status based on bash status
    :param: bash_status in integer. Valid should be from 1 to 4
    :return: sonar status in String. Return empty string for invalid value of bash_status
    """
    sonar_status_dict = {
        0: "off",
        1: "on",
        2: "not installed",
        3: "off by policy",
        4: "malfunction"
    }
    return sonar_status_dict.get(bash_status, "")


def get_ips_status(cids_drv_onoff):
    """
    map IPS status based on cidsDrvOnOff value
    :param cids_drv_onoff: integer
    :return: ips status in String. Return empty string for invalid value of cids_drv_onoff
    """
    ips_status_dict = {
        0: "off",
        1: "on",
        2: "not installed",
        3: "off by admin policy",
        127: "unknown"
    }
    return ips_status_dict.get(cids_drv_onoff, "")

def get_ap_status(ap_onoff):
    """
    map AP status based on ap_onoff value
    :param: ap_onoff in integer
    :return: ap status in String. Return empty string for invalid value of ap_onoff
    """
    ap_status_dict = {
        0: "off",
        1: "on",
        2: "not installed",
        3: "disabled by policy",
        4: "malfunctioning",
        5: "disabled as unlicensed",
        127: "status not reported"
    }
    return ap_status_dict.get(ap_onoff, "")

def get_hi_status(vsic_status):
    """
    map host integrity status based on vsic_status
    :param vsic_status: integer
    :return: host integrity status in String. Return empty string for invalid value of vsic_status
    """
    hi_status_dict = {
        0: "fail",
        1: "success",
        2: "pending",
        3: "disabled",
        4: "ignore"
    }
    return hi_status_dict.get(vsic_status, "")

# Mapping between Symantec API response fields to CounterACT properties
symantec_to_ct_props_map = {
    "group": "connect_symantec_group_id",
    "uniqueId": "connect_symantec_computer_id",
    "computerName": "connect_symantec_computer_name",
    "operatingSystem": "connect_symantec_os",
    "apOnOff": "connect_symantec_auto_protection_status",
    "vsicStatus": "connect_symantec_host_integrity_status",
    "infected": "connect_symantec_host_infected",
    "onlineStatus": "connect_symantec_host_managed",
    "cidsDrvOnOff": "connect_symantec_ips_status",
    "lastUpdateTime": "connect_symantec_last_sync_time",
    "firewallOnOff": "connect_symantec_ntp_enabled",
    "bashStatus": "connect_symantec_sonar_status",
    "lastScanTime": "connect_symantec_antivirus_def_date"
}

symantec_infection_info_map = {
    "severity": "connect_symantec_infection_severity",
    "name": "connect_symantec_infection_name",
    "date":"connect_symantec_infection_time"
}

server_url = params.get("connect_symantec_server_url")
port = params.get("connect_symantec_server_port")
protocol = "https://"
response = {}

url = "{}{}:{}/sepm/api/v1/computers".format(protocol, server_url, port)

bearer_token = params.get("connect_authorization_token")

if bearer_token and "mac" in params:
    try:
        mac = '-'.join(params["mac"][i:i+2] for i in range(0,12,2))
        resolve_url = f"{url}?mac={mac}"
        logging.debug(f"Resolve URL: {resolve_url}")
        headers = { "Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + str(bearer_token) }
        # Create proxy server
        proxy_server = ConnectProxyServer(params)
        # Pass to use what HTTPS or HTTP or both in the protocol, pass down the ssl_context
        opener = proxy_server.get_urllib_request_https_opener(ProxyProtocol.all, ssl_context)
        resolve_request = request.Request(resolve_url, headers=headers)
        resolve_response = opener.open(resolve_request)
        if resolve_response.getcode() == 200:
            resolve_response_dict = json.loads(resolve_response.read())
            if resolve_response_dict.get("content"):
                resolve_host = resolve_response_dict["content"][0]
                logging.debug(f"response data for mac {mac}: {resolve_host}")
                properties = {}
                for key, value in resolve_host.items():
                    if key in symantec_to_ct_props_map:
                        if key == "group":
                            properties[symantec_to_ct_props_map[key]] = value.get("id", "")
                        elif key == "apOnOff":
                            properties[symantec_to_ct_props_map[key]] = get_ap_status(value)
                        elif key == "vsicStatus":
                            properties[symantec_to_ct_props_map[key]] = get_hi_status(value)
                        elif key == "cidsDrvOnOff":
                            properties[symantec_to_ct_props_map[key]] = get_ips_status(value)
                        elif key == "bashStatus":
                            properties[symantec_to_ct_props_map[key]] = get_sonar_status(value)
                        elif key in ["infected", "onlineStatus", "firewallOnOff"]:
                            properties[symantec_to_ct_props_map[key]] = value == 1
                        elif key in ["lastUpdateTime", "lastScanTime"]:
                            properties[symantec_to_ct_props_map[key]] = int(value)//1000
                        else:
                            properties[symantec_to_ct_props_map[key]] = value
                response["properties"] = properties
                logging.debug(f"response: {response}")
            else:
                logging.debug(f"No Symantec data available for mac {mac}")
                response["error"] = f"No Symantec data available for mac {mac}"
        else:
            response["error"] = "Failed to connect to Symantec Server."
    except HTTPError as e:
        response["succeeded"] = False
        http_error_msg = f"HTTP Error : Could not connect to Symantec server. Error code: {e.code}"
        response["result_msg"] = http_error_msg
        logging.debug(http_error_msg)
    except URLError as e:
        response["succeeded"] = False
        url_error_msg = f"URL Error : Could not connect to Symantec server. Reason: {e.reason}"
        response["result_msg"] = url_error_msg
        logging.debug(url_error_msg)
    except Exception as e:
        response["succeeded"] = False
        exp_error_msg = f"Could not connect to Symantec server. Exception: {e}"
        response["result_msg"] = exp_error_msg
        logging.debug(exp_error_msg)
else:
    response["succeeded"] = False
    error_msg = "No Bearer Token or No mac address to query the endpoint for."
    response["result_msg"] = error_msg
    logging.debug(error_msg)


