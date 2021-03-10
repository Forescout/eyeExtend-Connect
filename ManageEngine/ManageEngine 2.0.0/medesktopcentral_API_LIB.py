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

import base64
import datetime
import json
import ssl
import time
import urllib.request


def medesktopcentral_http_client(credentials, medc_server_details):
    _current_status_code = None

    _username = credentials["username"]
    auth_header = credentials["password"]
    base64string = base64.b64encode(bytes('%s' % (auth_header), 'ascii'))
    payload = {
        'username': _username,
        'password': base64string.decode('utf-8'),
        'auth_type': 'local_authentication'
    }
    _handlers = []
    _handlers.append(urllib.request.HTTPCookieProcessor())
    _handlers.append(urllib.request.HTTPSHandler())
    _opener = urllib.request.build_opener(*_handlers)
    _address = medc_server_details["address"]
    _port = medc_server_details["port"]
    _baseurl = "http://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/1.3/desktop/authentication".format(_baseurl),
                                     data=bytes(json.dumps(payload), encoding="utf-8"))
    request.add_header("Content-Type", "application/json")
    request.add_header("charset", "utf-8")
    request.add_header("User-Agent", "FSCT/9.16.2020")
    response = _opener.open(request, timeout=100)
    r = response.read()
    data = json.loads(r.decode("utf-8"))
    if data["status"] == "success":
        sess_token = data["message_response"]["authentication"]["auth_data"]["auth_token"]
    else:
        sess_token = 0
    _current_status_code = response.getcode()
    return _current_status_code, _opener, sess_token


def medesktopcentral_check_summary(http_client, medc_server_details, session_token):
    _http_client = http_client
    _address = medc_server_details["address"]
    _port = medc_server_details["port"]
    _session_token = session_token

    _baseurl = "http://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/1.3/som/summary".format(_baseurl))
    request.add_header("Authorization", _session_token)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def medesktopcentral_query_asset(http_client, medc_server_details, session_token, resid):
    _http_client = http_client
    _address = medc_server_details["address"]
    _port = medc_server_details["port"]
    _session_token = session_token
    _resid = resid

    _baseurl = "http://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/1.3/patch/allsystems?resid={}".format(_baseurl, _resid))
    request.add_header("Authorization", _session_token)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def medesktopcentral_query_agent_install_status(http_client, medc_server_details, session_token, resid):
    _http_client = http_client
    _address = medc_server_details["address"]
    _port = medc_server_details["port"]
    _session_token = session_token
    _resid = resid

    _baseurl = "http://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/1.3/som/computers?residfilter={}".format(_baseurl, _resid))
    request.add_header("Authorization", _session_token)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def medesktopcentral_get_timestamp(time_timestamp):
    pattern = '%Y-%m-%d %H:%M:%S'
    _date_time_obj = datetime.datetime.fromtimestamp(int(str(time_timestamp)[:-3])).strftime(pattern)
    epoch = int(time.mktime(time.strptime(_date_time_obj, pattern)))
    return epoch


def medesktopcentral_query_missing_patches(http_client, medc_server_details, session_token, resid):
    _http_client = http_client
    _address = medc_server_details["address"]
    _port = medc_server_details["port"]
    _session_token = session_token
    _resid = resid

    _baseurl = "http://{}:{}".format(_address, _port)

    request = urllib.request.Request(
        "{}/api/1.3/patch/systemreport?resid={}&page=1&pagelimit=250".format(_baseurl, _resid))
    request.add_header("Authorization", _session_token)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def medesktopcentral_query_computer_details(http_client, medc_server_details, session_token, resid):
    _http_client = http_client
    _address = medc_server_details["address"]
    _port = medc_server_details["port"]
    _session_token = session_token
    _resid = resid

    _baseurl = "http://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/1.3/inventory/compdetailssummary?resid={}".format(_baseurl, _resid))
    request.add_header("Authorization", _session_token)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def medesktopcentral_install_all_missing_patch(http_client, medc_server_details, session_token, resid):
    _http_client = http_client
    _address = medc_server_details["address"]
    _port = medc_server_details["port"]
    _session_token = session_token
    _resid = resid
    _baseurl = "http://{}:{}".format(_address, _port)

    _payload = {"ResourceIDs": '[{}]'.format(_resid),
                "ConfigName": "API install patch test1",
                "ConfigDescription": "API test",
                "actionToPerform": "Deploy",
                "isOnlyApproved": "true",
                "DeploymentPolicyTemplateID": 1}

    payload = json.dumps(_payload)
    payload = payload.replace('"[', '[')
    payload = payload.replace(']"', ']')

    request = urllib.request.Request("{}/api/1.3/patch/installpatch".format(_baseurl),
                                     data=bytes(payload, encoding="utf-8"))
    request.add_header("Content-Type", "application/json")
    request.add_header("charset", "utf-8")
    request.add_header("User-Agent", "FSCT/1.16.2020")
    request.add_header("Authorization", _session_token)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def medesktopcentral_patch_scan(http_client, medc_server_details, session_token, resid):
    _http_client = http_client
    _address = medc_server_details["address"]
    _port = medc_server_details["port"]
    _session_token = session_token
    _resid = resid
    _baseurl = "http://{}:{}".format(_address, _port)

    _payload = {"ResourceIDs": [601]}
    _payload["ResourceIDs"] = '[{}]'.format(_resid)
    payload = json.dumps(_payload)
    payload = payload.replace('"[', '[')
    payload = payload.replace(']"', ']')

    request = urllib.request.Request("{}/api/1.3/patch/computers/scan".format(_baseurl),
                                     data=bytes(payload, encoding="utf-8"))
    request.add_header("Content-Type", "application/json")
    request.add_header("charset", "utf-8")
    request.add_header("User-Agent", "FSCT/1.16.2020")
    request.add_header("Authorization", _session_token)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data
