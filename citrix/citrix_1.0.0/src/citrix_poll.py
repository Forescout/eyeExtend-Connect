# POLL: Discover endpoints from Citrix ADM (VPN)
# Connect Plugin V1.6

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

from base64 import b64encode
import datetime
import logging
import time

begin_time = datetime.datetime.now()

endpoints = []
response = {}

citrix_func.debug('Starting Citrix ADM Poll Script')

URL = params.get('connect_citrix_ADM') + ":" + params.get("connect_citrix_ADM_port")
citrix_username = params.get('connect_citrix_username')
citrix_password = params.get('connect_citrix_password')

# Login and get ADM session ID
citrix_func.debug('\n=====  Getting SessionID  =====')
(code, sessid, session) = citrix_func.citrix_login(URL, citrix_username, citrix_password, ssl_context)
citrix_func.debug("Session ID Returned: {}".format(sessid))

# Get Citrix VPN Gateways
citrix_func.debug("\n=====  Getting VPN Gateways  =====")

(code, vpngateways) = citrix_func.citrix_get_vpn_gws(URL, sessid, session, ssl_context)
if code == 200:
    citrix_func.debug("Citrix Gateways Returned Successfully {}".format(vpngateways))
    unique_ns_ips = set([ sub['ns_ip_address'] for sub in vpngateways ])
    unique_vpn_gws =[]
    for unique_ip in unique_ns_ips:
        names = [d['name'] for d in vpngateways if d['ns_ip_address'] == unique_ip]
        hostname = "".join(set([d['hostname'] for d in vpngateways if d['ns_ip_address'] == unique_ip]))
        separator = " & "
        concat_names = separator.join(names)
        unique_vpn_gw = {}
        unique_vpn_gw["ns_ip_address"] = unique_ip
        unique_vpn_gw["hostname"] = hostname
        unique_vpn_gw["name"] = concat_names
        unique_vpn_gws.append(unique_vpn_gw)
    citrix_func.debug("Unique gateways, return code: {}, response: {}".format(code, unique_vpn_gws))
else:
    citrix_func.debug("Error getting gateways, return code: {}, response: {}".format(code, vpngateways))

#Get Citrix VPN Users
citrix_func.debug("\n=====  Getting VPN Endpoints  =====")
for vpn_gw in unique_vpn_gws:
    (code, vpnusers) = citrix_func.citrix_get_vpn_users(URL, sessid, session, ssl_context, vpn_gw)
    if code == 200:
        endpoints.extend(vpnusers)
    else:
        citrix_func.debug("Error getting vpnusers {}".format(vpnusers))

citrix_func.debug("Endpoints Returned Successfully {}".format(endpoints))
num_endpoints = len(endpoints)
citrix_func.debug("Total number of endpoints:" + str(num_endpoints))

response["endpoints"] = endpoints
elapsed_time = (datetime.datetime.now() - begin_time)
citrix_func.debug('Ending Citrix ADM Poll Script, Polling Time: ' + str(elapsed_time))
