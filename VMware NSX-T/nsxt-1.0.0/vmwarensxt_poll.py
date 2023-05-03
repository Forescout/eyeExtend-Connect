"""
Copyright © 2023 Forescout Technologies, Inc.

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
from multiprocessing.sharedctypes import Value
import requests
import json
import base64

# Values from system.conf
server = params.get("connect_vmwarensxt_server")
port = params.get("connect_vmwarensxt_port")
username = params.get("connect_vmwarensxt_username")
password = params.get("connect_vmwarensxt_password")

# General Values
response = {}
endpoints = []

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

# URLs
base_url = "https://{}:{}/api/v1".format(server,port)

## Logical Switch (aka Segments) queries
ls_base_url = base_url + "/logical-switches"
ls_url = ls_base_url + "?transport_type=OVERLAY"
vtep_url = "/vtep-table?source=realtime"

## Transport Node queries
tn_base_url = base_url + "/transport-nodes"
tn_url = tn_base_url + "?node_types=HostNode"

## Logical Router (aka Gateways) queries
lr_url = base_url + "/logical-router-ports"
larp_url = "/arp-table?source=realtime"

# Auth string
authString = "{}:{}".format(username,password)

b64authString = base64.b64encode(bytes('%s' % (authString), 'ascii'))
auth_header = b64authString.decode('utf-8')

# Request content
headers = {"Authorization":"Basic {}".format(auth_header)}

# Response Captures
switch_ids = []
vtep_entries = {}
tn_entries = {}
lr_entries = {}
larp_entries = {}
larp_total_count = 0
final_table = {}

# Get Logical Switch details

try:
    resp = requests.request("GET", ls_url, headers=headers, verify=ssl_verify, proxies=proxies, timeout=3)
    resp_code = resp.status_code
    json_resp = json.loads(resp.content)
    resp.raise_for_status()
except requests.exceptions.HTTPError as errh:
    logging.debug("***NSX - POLL*** API Client Query returned HTTP error:{}".format(errh))
except requests.exceptions.ConnectionError as errc:
    logging.debug("***NSX - POLL*** API Client Query returned Connecting error:{}".format(errc))
except requests.exceptions.Timeout as errt:
    logging.debug("***NSX - POLL*** API Client Query returned Timeout error:{}".format(errt))
except requests.exceptions.RequestException as err:
    logging.debug("***NSX - POLL*** API Client Query returned error:{}".format(err))

logging.debug("***NSX - POLL*** API Client Query returned code [{}] and response [{}].".format(resp_code,str(json_resp)))

if resp_code == 200:
    ls_count = json_resp["result_count"]
    logging.debug("***NSX - POLL*** Connection successful. Found {} VMware NSX-T Logical Switches.".format(ls_count))
    for x in json_resp["results"]:
        switch_ids.append(x["id"])
    logging.debug("***NSX - POLL*** Retrieved Logical Switch ID's [ {} ]".format(switch_ids))
    switch_ids_num = len(switch_ids)
    logging.debug("***NSX - POLL*** Retrieved {} Logical-Switch / Segment ID's".format(switch_ids_num))

#Logical Switch ARP entries

    if ls_count>=1:
        for x in switch_ids:
            vtep_resp_url = ls_base_url + "/" + x + vtep_url
            try:
                vtep_resp = requests.request("GET", vtep_resp_url, headers=headers, verify=ssl_verify, proxies=proxies, timeout=3)
                vtep_resp_code = vtep_resp.status_code
                vtep_json_resp = json.loads(vtep_resp.content)
                vtep_resp.raise_for_status()            
            except requests.exceptions.HTTPError as errh:
                logging.debug("***NSX - POLL*** VTEP Query returned HTTP error:{}".format(errh))
            except requests.exceptions.ConnectionError as errc:
                logging.debug("***NSX - POLL*** VTEP Query returned Connecting error:{}".format(errc))
            except requests.exceptions.Timeout as errt:
                logging.debug("***NSX - POLL*** VTEP Query returned Timeout error:{}".format(errt))
            except requests.exceptions.RequestException as err:
                logging.debug("***NSX - POLL*** VTEP Query returned error:{}".format(err))
    
            if vtep_resp_code == 200:
                vtep_count = vtep_json_resp["result_count"]
                logging.debug("***NSX - POLL***  VTEP Query - Switch ID: [[ {} ]] Response: [[ {} ]]".format(x,vtep_json_resp))
                for y in vtep_json_resp["results"]:
                    vtep_ip = y["vtep_ip"]
                    vtep_mac_colon = str(y["vtep_mac_address"])
                    vtep_mac = vtep_mac_colon.replace(':','')
                    vtep_entries[vtep_mac] = vtep_ip
                    final_table[vtep_mac] = vtep_ip 
                logging.debug("***NSX - POLL*** Retrieved {} VTEP Entries from Logical Switch / Segment. Entries retrieved [ {} ]".format(vtep_count,vtep_entries))

else:
    logging.debug("Did not get a 200 code from API query for Logical-Switch. HTTP Error: {} Please check permissions.".format(resp_code))

# Logical router query
try:
    lr_resp = requests.request("GET", lr_url, headers=headers, verify=ssl_verify, proxies=proxies, timeout=3)
    lr_resp_code = lr_resp.status_code
    lr_json_resp = json.loads(lr_resp.content)
    lr_resp.raise_for_status()
except requests.exceptions.HTTPError as errh:
    logging.debug("***NSX - POLL*** Logical Router Query returned HTTP error:{}".format(errh))
except requests.exceptions.ConnectionError as errc:
    logging.debug("***NSX - POLL*** Logical Router Query returned Connecting error:{}".format(errc))
except requests.exceptions.Timeout as errt:
    logging.debug("***NSX - POLL*** Logical Router Query returned Timeout error:{}".format(errt))
except requests.exceptions.RequestException as err:
    logging.debug("***NSX - POLL*** Logical Router Query returned error:{}".format(err))

logging.debug("***NSX - POLL*** Logical Router Query - Response: [[ {} ]]".format(lr_json_resp))

if lr_resp_code == 200:
    lr_count = lr_json_resp["result_count"]
    for w in lr_json_resp["results"]:
        lr_name = w["display_name"]
        lr_id = w["id"]
        lr_entries[lr_name] = lr_id

    logging.debug("***NSX - POLL*** Retrieved {} Logical Router Entries. Entries Retrieved [ {} ]\n\n".format(lr_count, lr_entries))

# Logical router ARP entries   

larp_result = []

if lr_count >=1:
    with requests.Session() as reqs:
        for y,z in lr_entries.items():
            larp_resp_url = lr_url + "/" + z + larp_url
            logging.debug("Logical Router URL: {}".format(larp_resp_url))
            try:
                larp_resp = reqs.get(larp_resp_url, headers=headers, verify=ssl_verify, proxies=proxies, timeout=3)
                larp_resp_code = larp_resp.status_code
                larp_json_resp = json.loads(larp_resp.content)
                larp_resp.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                logging.debug("***NSX - POLL*** Logical Router ARP Query returned HTTP error:{}".format(errh))
            except requests.exceptions.ConnectionError as errc:
                logging.debug("***NSX - POLL*** Logical Router ARP Query returned Connecting error:{}".format(errc))
            except requests.exceptions.Timeout as errt:
                logging.debug("***NSX - POLL*** Logical Router ARP Query returned Timeout error:{}".format(errt))
            except requests.exceptions.RequestException as err:
                logging.debug("***NSX - POLL*** Logical Router ARP Query returned error:{}".format(err))

            logging.debug("***NSX - POLL*** Logical Router ARP Query - Logical Router [[ {} Response: [[ {} ]]".format(y,larp_json_resp))
            logging.debug("Resonse Code: [{}]".format(larp_resp_code))

            if larp_resp_code == 200:        
                larp_count = larp_json_resp["result_count"]
                logging.debug("larp_count {}".format(larp_count))
                larp_total_count += larp_count
                logging.debug("larp_total_count {}".format(larp_total_count))
                if "results" in larp_json_resp:
                    for x in larp_json_resp["results"]:
                        larp_mac_colon = str(x["mac_address"])
                        larp_mac = larp_mac_colon.replace(':','')
                        larp_ip = x["ip"]
                        larp_entries[larp_mac] = larp_ip
                        final_table[larp_mac] = larp_ip

                    larp_result.append("Successful ARP Query against Logical Router {}. Found {} entries".format(y,larp_count))
                    logging.debug("***NSX - POLL*** Successful ARP Query against Logical Router {}. Found {} entries".format(y,larp_count))
            else:
                larp_result.append("ARP Query failed for Logical Router {}".format(y))
                logging.debug("***NSX - POLL*** ARP Query failed for Logical Router {}".format(y))
else:
    logging.debug("***NSX - POLL*** Logical Router query Failed")
           
logging.debug("***NSX - POLL*** Indvidual query results [ {} ]".format(larp_result))
logging.debug("***NSX - POLL*** Found {} ARP entries in total. Unique entries found [ {} ]".format(larp_total_count,larp_entries))

logging.debug("***NSX - POLL*** Mapping NSX-T properties")

for key, value in final_table.items():
    endpoint = {}
    endpoint["mac"] = key
    endpoint["ip"] = value

    properties = {}
    properties["connect_vmwarensxt_mac"] = key
    properties["connect_vmwarensxt_ip"] = value

    endpoint["properties"] = properties
    endpoints.append(endpoint)

    logging.debug("***NSX - POLL*** Updating discovered endpoint properties: [{}]".format(endpoint))

    response["endpoints"] = endpoints

final_result = "***NSX - POLL*** Final unique ARP entries collected:\n\n"
for x, y in final_table.items():
    add_entry = "Mac: " + x + " IP: " + y + " \n"
    final_result += str(add_entry)

logging.debug(final_result)