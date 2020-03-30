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

import json
import ssl
import urllib.request


def UB_HTTP_CLIENT(credentials, controller_details):
    """
    Unifi API for the Unifi Controller.
    """
    _login_data = {}
    _current_status_code = None

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    _handlers = []
    _handlers.append(urllib.request.HTTPCookieProcessor())
    _handlers.append(urllib.request.HTTPSHandler(context=context))
    _opener = urllib.request.build_opener(*_handlers)
    _address = controller_details["address"]
    _port = controller_details["port"]
    _baseurl = "https://{}:{}".format(_address, _port)
    _login_data['username'] = credentials["username"]
    _login_data['password'] = credentials["password"]
    request = urllib.request.Request("{}/api/login".format(_baseurl),
                                     data=bytes(json.dumps(_login_data), encoding="utf-8"))
    response = _opener.open(request, timeout=100)
    _current_status_code = response.getcode()
    return _current_status_code, _opener


def UB_LIST_CLIENTS(http_client, controller_details):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]

    _baseurl = "https://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/s/{}/stat/sta".format(_baseurl, _site))
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_LIST_DEVICES(http_client, controller_details):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]

    _baseurl = "https://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/s/{}/stat/device".format(_baseurl, _site))
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_QUERY_DEVICE(http_client, controller_details, device_mac):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]

    _baseurl = "https://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/s/{}/stat/device/{}".format(_baseurl, _site, device_mac))
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_QUERY_CLIENT(http_client, controller_details, client_mac):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]

    _baseurl = "https://{}:{}".format(_address, _port)

    request = urllib.request.Request("{}/api/s/{}/stat/user/{}".format(_baseurl, _site, client_mac))
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_QUERY_CLIENT_APPS(http_client, controller_details, client_mac):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]

    _baseurl = "https://{}:{}".format(_address, _port)
    payload = {'type': 'by_cat', 'macs': [client_mac]}
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request("{}/api/s/{}/stat/stadpi".format(_baseurl, _site), data,
                                     headers={'Content-Type': 'application/json'})
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_BLOCK_CLIENT(http_client, controller_details, client_mac):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]

    _baseurl = "https://{}:{}".format(_address, _port)
    payload = {'cmd': 'block-sta', 'mac': client_mac}
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request("{}/api/s/{}/cmd/stamgr".format(_baseurl, _site), data,
                                     headers={'Content-Type': 'application/json'})
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_UNBLOCK_CLIENT(http_client, controller_details, client_mac):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]

    _baseurl = "https://{}:{}".format(_address, _port)
    payload = {'cmd': 'unblock-sta', 'mac': client_mac}
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request("{}/api/s/{}/cmd/stamgr".format(_baseurl, _site), data,
                                     headers={'Content-Type': 'application/json'})
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data
