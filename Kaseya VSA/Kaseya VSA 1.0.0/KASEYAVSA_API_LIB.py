"""
Copyright © 2020 Forescout Technologies, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to  the following conditions:

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
import ssl
import urllib.request
from hashlib import sha256
from hashlib import sha1
import datetime
import random
import decimal
import base64
import http.client
import mimetypes

def KASEYAVSA_HTTP_CLIENT(credentials, vsa_server_details, ssl_context):
    """
    Unifi API for the Unifi Controller.
    """
    _login_data = {}
    _current_status_code = None

    kusername = credentials["username"]
    kpassword = credentials["password"]
    kUserPassword = kpassword+kusername
    random_number = random.randint(9999999,100000000)

    RawSHA256Hash = sha256(kpassword.encode('utf-8')).hexdigest()
    CoveredSHA256HashTemp = sha256(kUserPassword.encode('utf-8')).hexdigest()
    CoveredSHA256Hash = sha256((CoveredSHA256HashTemp+str(random_number)).encode('utf-8')).hexdigest()
    RawSHA1Hash = sha1(kpassword.encode('utf-8')).hexdigest()
    CoveredSHA1HashTemp = sha1(kUserPassword.encode('utf-8')).hexdigest()
    CoveredSHA1Hash = sha1((CoveredSHA1HashTemp+str(random_number)).encode('utf-8')).hexdigest()
    Auth_header = 'user='+kusername+',pass2='+CoveredSHA256Hash+',pass1='+CoveredSHA1Hash+',rpass2='+RawSHA256Hash+',rpass1='+RawSHA1Hash+',rand2='+str(random_number)


    _handlers = []
    _handlers.append(urllib.request.HTTPCookieProcessor())
    _handlers.append(urllib.request.HTTPSHandler(context=ssl_context))
    _opener = urllib.request.build_opener(*_handlers)
    _address = vsa_server_details["address"]
    _port = vsa_server_details["port"]
    _baseurl = "https://{}:{}".format(_address, _port)
    request = urllib.request.Request("{}/api/v1.0/auth".format(_baseurl))
    base64string = base64.b64encode(bytes('%s' % (Auth_header),'ascii'))
    request.add_header("Authorization", "Basic "+base64string.decode('utf-8'))
    response = _opener.open(request, timeout=100)
    r = response.read()
    data = json.loads(r.decode("utf-8"))
    if data["ResponseCode"] == 0:
        sess_token = data["Result"]["Token"]
    else:
        sess_token = 0
    _current_status_code = response.getcode()
    return _current_status_code, _opener, sess_token


def KASEYAVSA_LIST_ASSETS(http_client, vsa_server_details, session_token):
    _http_client = http_client
    _address = vsa_server_details["address"]
    _port = vsa_server_details["port"]
    _session_token = session_token

    _baseurl = "https://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/v1.0/assetmgmt/assets".format(_baseurl))
    request.add_header("Authorization", "Bearer "+_session_token)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def KASEYAVSA_QUERY_ASSETS(http_client, vsa_server_details, session_token, mac):
    _http_client = http_client
    _address = vsa_server_details["address"]
    _port = vsa_server_details["port"]
    _session_token = session_token
    _mac = mac

    _baseurl = "https://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/v1.0/assetmgmt/assets?$filter=MACAddresses+eq+'{}'".format(_baseurl, _mac))
    request.add_header("Authorization", "Bearer "+_session_token)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def KASEYAVSA_QUERY_MISSING_PATCHES(http_client, vsa_server_details, session_token, agentid):
    _http_client = http_client
    _address = vsa_server_details["address"]
    _port = vsa_server_details["port"]
    _session_token = session_token
    _agentid = agentid

    _baseurl = "https://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/v1.0/assetmgmt/patch/{}/machineupdate".format(_baseurl, _agentid))
    request.add_header("Authorization", "Bearer "+_session_token)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def KASEYAVSA_PATCH_NOW(http_client, vsa_server_details, session_token, agentid):
    _http_client = http_client
    _address = vsa_server_details["address"]
    _port = vsa_server_details["port"]
    _session_token = session_token
    _agentid = agentid
    conn=http.client.HTTPConnection(_address)
    _payload = {'AgentGuids': [421898335696963], 'ServerTimeZone': True, 'SkipIfOffLine': True, 'PowerUpIfOffLine': True, 'PatchIds': [0], 'Recurrence': {'Repeat': 'Never', 'Times': 0, 'DaysOfWeek': 'string', 'DayOfMonth': 'FirstSunday', 'SpecificDayOfMonth': 0, 'MonthOfYear': 'January', 'EndAt': 'T0000', 'EndOn': '2020-06-15T15:42:01.762Z', 'EndAfterIntervalTimes': 0}, 'Distribution': {'Interval': 'Minutes', 'Magnitude': 0}, 'Start': {'StartOn': '2020-06-15T15:42:01.762Z', 'StartAt': 'T0000'}, 'Exclusion': {'From': 'T0000', 'To': 'T0000'}, 'SchedInAgentTime': True, 'Attributes': {}}
    _payload["AgentGuids"] = '[{}]'.format(_agentid)
    payload = json.dumps(_payload)
    payload = payload.replace('"[','[')
    payload = payload.replace(']"',']')
    #print(payload)
    headers = {
    'Authorization': '',
    'Content-Type': 'application/json'
    }
    headers["Authorization"]="Bearer "+_session_token
    conn.request("PUT", "/api/v1.0/assetmgmt/patch/runnow", payload, headers)
    res = conn.getresponse()
    _current_status_code = res.status
    data = res.read()
    return _current_status_code, data


def KASEYAVSA_QUERY_LAST_PATCH_SCAN(http_client, vsa_server_details, session_token, agentid):
    _http_client = http_client
    _address = vsa_server_details["address"]
    _port = vsa_server_details["port"]
    _session_token = session_token
    _agentid = agentid
    _baseurl = "https://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/v1.0/assetmgmt/patch/{}/status".format(_baseurl, _agentid))
    request.add_header("Authorization", "Bearer "+_session_token)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def KASEYAVSA_SCAN_NOW(http_client, vsa_server_details, session_token, agentid):
    _http_client = http_client
    _address = vsa_server_details["address"]
    _port = vsa_server_details["port"]
    _session_token = session_token
    _agentid = agentid
    conn=http.client.HTTPConnection(_address)
    payload = {}
    headers = {
    'Authorization': '',
    'Content-Type': 'application/json'
    }
    headers["Authorization"]="Bearer "+_session_token
    conn.request("PUT", "/api/v1.0/assetmgmt/patch/{}/scannow".format(_agentid), json.dumps(payload), headers)
    res = conn.getresponse()
    _current_status_code = res.status
    data = res.read()
    return _current_status_code, data