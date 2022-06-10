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

import logging
import requests
import json
from datetime import datetime

# Values from system.conf
server = params.get("connect_sotimobicontrol_server")
port = params.get("connect_sotimobicontrol_port")

# General Values
response = {}
endpoints = []
token = params.get("connect_authorization_token")

if "mac" in params:
    mac = params.get("mac")
    logging.debug("Retrieved Mac Address for API query [{}]".format(mac))
else:
    logging.debug("Mac Address not Found")
    exit()

# SOTI MobiControl to Forescout property map
sotimobicontrol_props_map = {
    "DeviceId":"connect_sotimobicontrol_deviceid",
    "ComplianceStatus":"connect_sotimobicontrol_compliance_status",
    "AgentVersion":"connect_sotimobicontrol_agentversion",
    "CellularCarrier":"connect_sotimobicontrol_cellularcarrier",
    "IMEI_MEID_ESN":"connect_sotimobicontrol_imei_meid_esn",
    "IsEncrypted":"connect_sotimobicontrol_isencrypted",
    "LastCheckInTime":"connect_sotimobicontrol_lastcheckintime",
    "LastAgentConnectTime":"connect_sotimobicontrol_lastagentconnecttime",
    "LastAgentDisconnectTime":"connect_sotimobicontrol_lastagentdisconnecttime",
    "LastLoggedOnUser":"connect_sotimobicontrol_lastloggedonuser",
    "NetworkSSID":"connect_sotimobicontrol_networkssid",
    "PersonalizedName":"connect_sotimobicontrol_personalizedname",
    "PhoneNumber":"connect_sotimobicontrol_phonenumber",
    "BuildSecurityPatch":"connect_sotimobicontrol_buildsecuritypatch",
    "Kind":"connect_sotimobicontrol_kind",
    "DeviceName":"connect_sotimobicontrol_devicename",
    "HostName":"connect_sotimobicontrol_hostname",
    "Family":"connect_sotimobicontrol_family",
    "IsAgentOnline":"connect_sotimobicontrol_isagentonline",
    "Manufacturer":"connect_sotimobicontrol_manufacturer",
    "Model":"connect_sotimobicontrol_model",
    "OSVersion":"connect_sotimobicontrol_osversion",
    "Path":"connect_sotimobicontrol_path",
    "Platform":"connect_sotimobicontrol_platform",
    "ComplianceItems":"connect_sotimobicontrol_complianceitems"
}

# Requests Proxy
is_proxy_enabled = params.get("connect_proxy_enable")
if is_proxy_enabled == "true":
    proxy_ip = params.get("connect_proxy_ip")
    proxy_port = params.get("connect_proxy_port")
    proxy_user = params.get("connect_proxy_username")
    proxy_pass = params.get("connect_proxy_password")
    if not proxy_user:
        proxy_url = f"https://{proxy_ip}:{proxy_port}"
        proxies = {"https" : proxy_url}
        logging.debug ("Proxy enabled / no user")
    else:
        proxy_url = f"https://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
        proxies = {"https" : proxy_url}
        logging.debug ("Proxy enabled / user")
else:
    logging.debug ("Proxy disabled")
    proxies = None

# Query Base URL
url = "https://{}:{}/MobiControl/api/devices/search?filter=MACAddress='{}'".format(server,port,mac)

# Request content
payload = {}
headers = {"Authorization":"Bearer {}".format(token)}

logging.debug("***RESOLVE*** Querying SOTI MobiControl API at {} for device with Mac Address '{}'".format(server,mac))

resp = requests.request("GET", url, headers=headers, data=payload, verify=ssl_verify, proxies=proxies)
resp_code = resp.status_code
json_resp = json.loads(resp.content)
logging.debug("API Query returned code [{}] and response [{}].".format(resp_code,str(json_resp)))

if token != "":

    if resp_code == 200:
            logging.debug("Response received [{}]".format(str(json_resp)))
            
            for endpoint_data in json_resp:
                properties = {}
                composite_list = []

                for key, value in endpoint_data.items():
                    
                    if key in sotimobicontrol_props_map:
                        
                        if key not in ['LastCheckInTime', 'LastAgentConnectTime', 'LastAgentDisconnectTime', 'ComplianceItems']:
                            
                            properties[sotimobicontrol_props_map[key]] = value

                        elif key == 'ComplianceItems':

                            for i in value: 

                                if i["ComplianceValue"] in [True, False]:

                                    obj = {}
                                    obj["type"] = i["ComplianceType"]
                                    obj["value"] = i["ComplianceValue"]
                                    composite_list.append(obj)
                        
                            properties["connect_sotimobicontrol_complianceitems"] = composite_list
                   
                        elif value is not None:

                            try:
                                with_ms = bool(datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ'))
                            except ValueError:
                                with_ms = False
                            
                            try:
                                no_ms = bool(datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ'))
                            except ValueError:
                                no_ms = False

                            if with_ms:
                                date_time_obj = int(datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%s'))
                            elif no_ms:
                                date_time_obj = int(datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').strftime('%s'))
                            else:
                                break
                            
                            properties[sotimobicontrol_props_map[key]] = date_time_obj
                
                response["properties"] = properties

    else:
        response["error"] = "Did not get a 200 code from API query. HTTP Error: {} Please check permissions.".format(resp_code)
        logging.debug(response["error"])

else:
    response["error"] = "Failed to retrieve Token. Credentials or permissions may be wrong or disabled."
    logging.debug(response["error"])

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))