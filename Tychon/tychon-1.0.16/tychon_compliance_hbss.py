#Software: Copyright © 2020-21 Tychon, LLC
#License: Copyright © 2020 Forescout Technologies, Inc.
 
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
 
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
 
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import logging
import urllib
import json
import ssl
from urllib.request import HTTPError, URLError

ip = params["connect_tychon_ip"]
port = params["connect_tychon_port"]
apiKey = params["connect_tychon_api_key"]
days = params["connect_tychon_vulnerability_days"]
index = params["connect_tychon_cve_iava_index"]
location = params["connect_tychon_appliance_location"]
#dependencies
mac = params["mac"]
sending_ip = params["access_ip"]
domain = params["nbtdomain"]
host_name = params["nbthost"]

upper_mac = mac.upper()
colon_mac = ":".join(upper_mac[i:i+2] for i in range(0,12,2))

request = urllib.request.Request(f'https://{ip}:{port}/dmn/partner/compliance/hbss/')

request.add_header("accept", "application/json")
request.add_header("PARTNER-API-KEY", apiKey)
request.add_header("Content-Type", "application/json")

tychon_index = "tychon_ess_services"
os_fp = "Windows"

def build_body_call():
    return f'{{\"gracePeriodDays\": \"{days}\", '\
        f'"host.appliance_location\": \"{location}\", '\
            f'\"host.domain_name\": \"{domain}\", '\
                f'\"host.ip\": \"{sending_ip}\", '\
                    f'\"host.mac\": \"{colon_mac}\", '\
                        f'\"host.name\":\"{host_name}\", '\
                            f'\"host.os_fingerprint\": \"{os_fp}\", '\
                                f'\"targetIndex\": \"{tychon_index}\"'\
                                    f'}}'


body = build_body_call().encode('UTF-8')

request.data = body
request.get_method = lambda: 'PUT'

def dictionary_to_string(return_dictionary):
    concat_string = ''
    for i in return_dictionary:
        for key, value in i.items():
            concat_string = concat_string + (f'\"{key}\": \"{value}\"')

    return concat_string

host_managed = False

response = {}
properties = {}

try:
    resp = urllib.request.urlopen(request, context=ssl_context)
    resp_bytes = resp.read()
    resp_ascii = resp_bytes.decode(encoding="UTF-8")
    resp_json = json.loads(resp_ascii)

    hbss_list = resp_json["host.hbss"]
    is_managed = resp_json["host.managed"]
    last_communication = resp_json["host.lastCommunication"]
    
    if hbss_list != None:
        hbss_list_string = dictionary_to_string(hbss_list)
    else:
        hbss_list_string = "NA"

    properties["connect_tychon_host_managed"] = resp_json["host.managed"]
    properties["connect_tychon_host_hbss"] = hbss_list_string
    properties["connect_tychon_last_communication"] = last_communication

    response["properties"] = properties

except HTTPError as e:
    response["error"] = "HTTPError: {}".format(e.code)
except URLError as e:
	response["error"] = "URLError: {}".format(e.reason)
except Exception as e:
	response["error"] = "Exception: {}".format(str(e))
