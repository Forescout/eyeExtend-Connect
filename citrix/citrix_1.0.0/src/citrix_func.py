# LIBRARY: Common Citrix ADM functions
# Connect Plugin V1.6

"""
Copyright @ 2020 Forescout Technologies, Inc.

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

import requests
import json
import logging
import ssl
import urllib3
import time


# Supress certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

####################################
# --- Global Functions ---
####################################


# Streamline Logging
def debug(MESSAGE):
    message = "==>" + MESSAGE
    logging.debug(message)


# Web REST calls, Login and retrieve session
def citrix_login(URL, citrix_username, citrix_password, CTX):
    login_url = URL + "/nitro/v2/config/login"
    raw_data = '{"login": {"username": "' + str(citrix_username) + '","password": "' + str(citrix_password)+ '"}}'
    session = requests.Session()
    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json",
        'charset': "utf-8",
        'User-Agent': "FSCT/7.17.2020"
        }

    rjson = {}  # if the response is empty/errors, need to return something

    try:
        with session.post(login_url, headers=headers, data=raw_data, timeout=90, verify=False) as response:
            code = response.status_code
            rjson = response.json()
            sessid = rjson['login'][0]['sessionid']
            return(code, sessid, session)
    except Exception as err:
        code = 500
        debug("get_data() - Error logging in to Citrix ADM, URL Requested ==> " + str(URL) + "| Error Returned: " + str(err))
        return(code, str(err))



# Web REST calls, returns HTTP response Code and Response
def citrix_get_data(URL, SESSID, session, CTX, GW_IP):
    if GW_IP == "":
        #session.headers.update({'SESSID': '%s' % SESSID})
        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            'charset': "utf-8",
            'User-Agent': "FSCT/7.17.2020",
            'SESSID': '%s' % SESSID
            }
    else:
        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            'charset': "utf-8",
            'User-Agent': "FSCT/7.17.2020",
            '_MPS_API_PROXY_MANAGED_INSTANCE_IP': '%s' % GW_IP,
            'SESSID': '%s' % SESSID
            }
    debug("get_data() - Header ==> " + str(URL) + "| Error Returned: " + str(headers))
    rjson = {}  # if the response is empty/errors, need to return something
    payload = {}

    try:
        with session.get(URL, headers=headers, timeout=90, verify=False) as response:
            code = response.status_code
            rjson = response.json()
            return(code, rjson)
    except Exception as err:
        code = 500
        debug("get_data() - Error sending data to Citrix ADM, URL Requested ==> " + str(URL) + "| Error Returned: " + str(err))
        return(code, str(err))

# Return the Citrix VPN Gateways
def citrix_get_vpn_gws(URL, SESSID, session, CTX):
    debug('Starting Citrix VPN gateway Function.')
    debug('Getting Citrix VPN Gateways')
    req_url = URL + "/nitro/v2/stat/ns_vpnvserver"
    (code, resp) = citrix_get_data(req_url, SESSID, session, CTX, "")
    if code == 200:
        vpnservers = resp.get("ns_vpnvserver")
        debug("Citrix VPN GWs returned: " + str(vpnservers))
    else:
        debug("get_vpn_gws() - Error, get_data() returned ==> " + vpnservers)
        version = 0
    debug("Ending Citrix VPN GW Function.")
    return(code, vpnservers)

# Return the Citrix VPN Users
def citrix_get_vpn_users(URL, SESSID, session, CTX, VPN_APPL):
    debug('Starting Citrix VPN user Function for' + VPN_APPL["ns_ip_address"])
    debug('Getting Citrix VPN users')
    endpoints = []
    req_url = URL + "/nitro/v1/config/aaasession"
    gw_ip = VPN_APPL["ns_ip_address"]
    gw_hostname = VPN_APPL["hostname"]
    gw_desc = VPN_APPL["name"]
    (code, resp) = citrix_get_data(req_url, SESSID, session, CTX, gw_ip)
    current_poll_time = int(time.time())
    if code == 200:
        vpnusers = resp.get("aaasession")
        for vpnuser in vpnusers:
            vpnip = vpnuser.get("intranetip", "")
            if (vpnip and vpnip != "0.0.0.0"):
                endpoint = {}
                properties = {}
                endpoint["ip"] = vpnip
                properties["connect_citrix_last_poll_datetime"] = str(current_poll_time)
                properties["connect_citrix_ns_vpnvserver_hostname"] = str(gw_hostname)
                properties["connect_citrix_ns_vpnvserver_description"] = str(gw_desc)
                properties["connect_citrix_vpnuser"] = vpnuser.get("username", "")
                endpoint["properties"] = properties
                debug("Endpoint For VPN GW " + gw_ip + ": " + endpoint["ip"] + " - " + vpnuser.get("username", ""))
                
                endpoints.append(endpoint)
    else:
        debug("get_vpn_users() - Error, get_data() returned ==> " + resp)

    #Remove Duplicate endpoints
    unique_endpoints = list({v['ip']:v for v in endpoints}.values())

    debug("Ending Citrix VPN User Function.")
    return(code, unique_endpoints)


