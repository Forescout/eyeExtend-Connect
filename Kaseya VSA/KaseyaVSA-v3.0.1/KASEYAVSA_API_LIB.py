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
from hashlib import sha256
from hashlib import sha1
import datetime
import logging
import requests

refresh_token = "new"

def KASEYAVSA_REFRESH(status):
    global refresh_token

    if status == "new":
        return refresh_token
    else:
        refresh_token = status
        return refresh_token

def KASEYAVSA_LIST_ASSETS(server, port, token, proxies):
        
    _baseurl = "https://{}:{}".format(server,port)

    header = {"Authorization": "Bearer " + token}
    request = ("{}/api/v1.0/assetmgmt/assets".format(_baseurl))
    response = requests.request("GET", request, headers=header, verify=ssl_verify, proxies=proxies)
    _current_status_code = response.status_code
    
    if _current_status_code == 200:
        r = response.content
        data = json.loads(r.decode("utf-8"))
    else:
        data = "Kaseya VSA Server returned No Content with Response"
    return _current_status_code, data

def KASEYAVSA_QUERY_AGENT(server, port, token, _ipadd, proxies):
    
    _baseurl = "https://{}:{}".format(server,port)

    header = {"Authorization": "Bearer " + token}
    request = ("{}/api/v1.0/assetmgmt/agents?$filter=IPAddress+eq+'{}'".format(_baseurl,_ipadd))
    response = requests.request("GET", request, headers=header, verify=ssl_verify, proxies=proxies)
    _current_status_code = response.status_code
    
    if _current_status_code == 200:
        r = response.content
        data = json.loads(r.decode("utf-8"))
    else:
        data = "Kaseya VSA Server returned No Content with Response"
    return _current_status_code, data

def KASEYAVSA_QUERY_MISSING_PATCHES(server, port, token, vsa_agent_id, proxies):
    
    _agentid = vsa_agent_id
    
    _baseurl = "https://{}:{}".format(server,port)

    header = {"Authorization": "Bearer " + token}
    request = ("{}/api/v1.0/assetmgmt/patch/{}/machineupdate".format(_baseurl,_agentid))
    response = requests.request("GET", request, headers=header, verify=ssl_verify, proxies=proxies)
    _current_status_code = response.status_code
    
    if _current_status_code == 200:
        r = response.content
        data = json.loads(r.decode("utf-8"))
    else:
        data = "Kaseya VSA Server returned No Content with Response"
    return _current_status_code, data

def KASEYAVSA_PATCH_UPDATE_NOW(server, port, token, vsa_agent_id, vsa_patch_ids, proxies):
    
    _agentid = vsa_agent_id
    _patchids = vsa_patch_ids[:-2] #remove last 2 char

    _baseurl = "https://{}:{}".format(server,port)

    _payload = {"ServerTimeZone": True,"SkipIfOffLine": True,"PowerUpIfOffLine": True,"PatchIds": [299,266]}
    _payload["PatchIds"] = '[{}]'.format(_patchids)
    payload = json.dumps(_payload)
    payload = payload.replace('"[','[')
    payload = payload.replace(']"',']')
    #logging.debug(payload)
    logging.debug("**LIB ACTION** Payload: [{}]".format(payload))
    
    header = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
    request = ("{}/api/v1.0/assetmgmt/patch/{}/schedule".format(_baseurl,_agentid))
    response = requests.request("PUT", request, data=payload, headers=header, verify=ssl_verify, proxies=proxies)
    _current_status_code = response.status_code
    
    if _current_status_code == 200:
        r = response.content
        data = json.loads(r.decode("utf-8"))
    else:
        data = "Kaseya VSA Server returned No Content with Response"
    return _current_status_code, data

def KASEYAVSA_QUERY_LAST_PATCH_SCAN(server, port, token, vsa_agent_id, proxies):
    
    _agentid = vsa_agent_id
    _baseurl = "https://{}:{}".format(server,port)

    header = {"Authorization": "Bearer " + token}
    request = ("{}/api/v1.0/assetmgmt/patch/{}/status".format(_baseurl,_agentid))
    response = requests.request("GET", request, headers=header, verify=ssl_verify, proxies=proxies)
    _current_status_code = response.status_code
    
    if _current_status_code == 200:
        r = response.content
        data = json.loads(r.decode("utf-8"))
    else:
        data = "Kaseya VSA Server returned No Content with Response"
    return _current_status_code, data

def KASEYAVSA_SCAN_NOW(server, port, token, vsa_agent_id, proxies):
    _agentid = vsa_agent_id
    
    _baseurl = "https://{}:{}".format(server,port)

    header = {"Authorization": "Bearer " + token}
    request = ("{}/api/v1.0/assetmgmt/patch/{}/scannow".format(_baseurl,_agentid))
    response = requests.request("PUT", request, headers=header, verify=ssl_verify, proxies=proxies)
    _current_status_code = response.status_code
    
    if _current_status_code == 200:
        r = response.content
        data = json.loads(r.decode("utf-8"))
    else:
        data = "Kaseya VSA Server returned No Content with Response"
    return _current_status_code, data