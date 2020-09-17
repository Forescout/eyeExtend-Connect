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
import urllib.request
import logging
from http.cookiejar import CookieJar


def clean_empty_dict(d):
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_empty_dict(v) for v in d) if v]
    return {k: v for k, v in ((k, clean_empty_dict(v)) for k, v in d.items()) if v or v is False}


def UB_HTTP_CLIENT(credentials, controller_details):
    """
    Unifi API for the Unifi Controller.
    """
    _login_data = {}
    _current_status_code = None
    context = controller_details["ssl_context"]

    _headers = {'Content-Type': 'application/json; charset=utf-8'}

    _address = controller_details["address"]
    _port = controller_details["port"]
    _baseurl = "https://{}:{}".format(_address, _port)
    _login_url = '{}/api/login'.format(_baseurl)
    
    if controller_details["type"] == 'unifios':  
        _login_url = '{}/api/auth/login'.format(_baseurl)
    
    logging.debug("Using Request URL: {}".format(_login_url))

    _handlers = []
    try:
        cookie_jar = CookieJar()
        _handlers.append(urllib.request.HTTPCookieProcessor(cookie_jar))
        _handlers.append(urllib.request.HTTPSHandler(context=context))
        _opener = urllib.request.build_opener(*_handlers)
        _login_data['username'] = credentials["username"]
        _login_data['password'] = credentials["password"]
        request = urllib.request.Request(_login_url,
                                         headers=_headers,data=bytes(json.dumps(_login_data), encoding="utf-8"))
        response = _opener.open(request, timeout=100)
        _current_status_code = response.getcode()
        if controller_details["type"] == "unifios":
            # Required for UnifiOS authentication to work
            _preHeaders = list(response.headers._headers)
            for i in _preHeaders:
                if i[0] == 'X-CSRF-Token':
                    _csrfToken = i[1]
            _headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                    'X-CSRF-Token': _csrfToken
                }
    except Exception as e:
        logging.error("Get HTTP Client failed: {}.".format(str(e)))
    return _current_status_code, _opener, _headers


def UB_LIST_SITES(http_client, controller_details, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _baseurl = "https://{}:{}".format(_address, _port)
    _request_url = '{}/api/stat/sites'.format(_baseurl)

    if controller_details["type"] == 'unifios':  
        # UnifiOS based controllers currently do not support listing sites.  Return default site every time.
        return 200, "default"

    request = urllib.request.Request(_request_url, headers=headers)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_LIST_CLIENTS(http_client, controller_details, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]

    _baseurl = "https://{}:{}".format(_address, _port)
    _request_url = '{}/api/s/{}/stat/sta'.format(_baseurl, _site)

    if controller_details["type"] == 'unifios':  
        _request_url = '{}/proxy/network/api/s/{}/stat/sta'.format(_baseurl,_site)
    logging.debug("Using Request URL: {}".format(_request_url))

    request = urllib.request.Request(_request_url, headers=headers)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    logging.debug("Request Return Code: {}".format(_current_status_code))
    return _current_status_code, data


def UB_LIST_DEVICES(http_client, controller_details, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]

    _baseurl = "https://{}:{}".format(_address, _port)
    _request_url = '{}/api/s/{}/stat/device'.format(_baseurl, _site)
 
    if controller_details["type"] == 'unifios':  
        _request_url = '{}/proxy/network/api/s/{}/stat/device'.format(_baseurl,_site)

    request = urllib.request.Request(_request_url, headers=headers)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_QUERY_DEVICE(http_client, controller_details, device_mac, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]
    _baseurl = "https://{}:{}".format(_address, _port)
    
    _device_url = "{}/api/s/{}/stat/device/{}".format(_baseurl, _site, device_mac)
    if controller_details["type"] == 'unifios': 
        _device_url = "{}/proxy/network/api/s/{}/stat/device/{}".format(_baseurl, _site, device_mac)

    request = urllib.request.Request(_device_url, headers=headers)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_QUERY_CLIENT(http_client, controller_details, client_mac, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]

    _baseurl = "https://{}:{}".format(_address, _port)
    _request_url = "{}/api/s/{}/stat/user/{}".format(_baseurl, _site, client_mac)
 
    if controller_details["type"] == 'unifios':  
        _request_url = '{}/proxy/network/api/s/{}/stat/user/{}'.format(_baseurl, _site, client_mac)

    request = urllib.request.Request(_request_url, headers=headers)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_QUERY_CLIENT_APPS(http_client, controller_details, client_mac, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]

    _baseurl = "https://{}:{}".format(_address, _port)
    _request_url = "{}/api/s/{}/stat/stadpi".format(_baseurl, _site)
 
    if controller_details["type"] == 'unifios':  
        _request_url = '{}/proxy/network/api/s/{}/stat/stadpi'.format(_baseurl, _site)

    payload = {'type': 'by_cat', 'macs': [client_mac]}
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(_request_url, data, headers=headers)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_BLOCK_CLIENT(http_client, controller_details, client_mac, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]
    _baseurl = "https://{}:{}".format(_address, _port)
    _request_url = "{}/api/s/{}/cmd/stamgr".format(_baseurl, _site)
 
    if controller_details["type"] == 'unifios':  
        _request_url = '{}/proxy/network/api/s/{}/cmd/stamgr'.format(_baseurl, _site)

    payload = {'cmd': 'block-sta', 'mac': client_mac}
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(_request_url, data, headers=headers)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_UNBLOCK_CLIENT(http_client, controller_details, client_mac, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]

    _baseurl = "https://{}:{}".format(_address, _port)
    _request_url = "{}/api/s/{}/cmd/stamgr".format(_baseurl, _site)
 
    if controller_details["type"] == 'unifios':  
        _request_url = '{}/proxy/network/api/s/{}/cmd/stamgr'.format(_baseurl, _site)
    payload = {'cmd': 'unblock-sta', 'mac': client_mac}
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(_request_url, data, headers=headers)
    response = _http_client.open(request, timeout=100)
    _current_status_code = response.getcode()
    r = response.read()

    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


# Begin new functions
def UB_ADD_FW_GROUP(http_client, controller_details, client_ip, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]
    _baseurl = "https://{}:{}".format(_address, _port)

    _request_url = '{}/api/s/{}/rest/firewallgroup'.format(_baseurl, _site)
    if controller_details["type"] == 'unifios':  
        _request_url = '{}/proxy/network/api/s/{}/rest/firewallgroup'.format(_baseurl, _site)
    logging.debug("Using Request URL: {}".format(_request_url))
    # Get the firewall group by name, and append our IP to the object
    _ip_exists = False
    _request = urllib.request.Request(_request_url, headers=headers)
    _response = _http_client.open(_request)
    _firewall_groups = json.loads(_response.read())['data']
    for _f in _firewall_groups:
        if _f.get("name") == controller_details['group_name']:
            _current_members = _f.get("group_members")
            if client_ip in _current_members:
                _ip_exists = True
                logging.debug("IP Already exists in group, doing nothing")
            else:
                _new_members = _current_members + [client_ip]   
                _f.update( {'group_members' : _new_members} )
                _group_id = _f.get('_id')
                _group = _f
    logging.debug('Going to send data: {}'.format(_group))
    if _ip_exists is False:
        _fw_update_request_url = "{}/{}".format(_request_url, _group_id)
        _update_request = urllib.request.Request(_fw_update_request_url, headers=headers, method='PUT', data=bytes(json.dumps(_group), encoding="utf-8"))
        _update_response = _http_client.open(_update_request)

        _current_status_code = _update_response.getcode()
        r = _update_response.read()

        data = json.loads(r.decode("utf-8"))
        return _current_status_code, data
    else:
        _current_status_code = 999
        return _current_status_code, ""


def UB_REM_FW_GROUP(http_client, controller_details, client_ip, headers, group_name):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]
    _baseurl = "https://{}:{}".format(_address, _port)

    _request_url = '{}/api/s/{}/rest/firewallgroup'.format(_baseurl, _site)
    if controller_details["type"] == 'unifios':  
        _request_url = '{}/proxy/network/api/s/{}/rest/firewallgroup'.format(_baseurl, _site)
    logging.debug("Using Request URL: {}".format(_request_url))
    _ip_exists = False
    _request = urllib.request.Request(_request_url, headers=headers)
    _response = _http_client.open(_request)
    _firewall_groups = json.loads(_response.read())['data']
    for _f in _firewall_groups:
        if _f.get("name") == controller_details['group_name']:
            _current_members = _f.get("group_members")
            if client_ip in _current_members:
                _current_members.remove(client_ip)
                _f.update({'group_members' : _current_members})
                _group_id = _f.get('_id')
                _group = _f
                _ip_exists = True
            else:
                _ip_exists = False
                logging.debug("IP does not exist in the group, doing nothing")
    if _ip_exists is True:
        logging.debug("Sending Data: {}".format(json.dumps(_group)))
        _fw_update_request_url = "{}/{}".format(_request_url, _group_id)
        _update_request = urllib.request.Request(_fw_update_request_url, headers=headers, method='PUT', data=bytes(json.dumps(_group), encoding="utf-8"))
        _update_response = _http_client.open(_update_request)
        _current_status_code = _update_response.getcode()
        r = _update_response.read()

        data = json.loads(r.decode("utf-8"))
        return _current_status_code, data
    else:
        _current_status_code = 999
        return _current_status_code, ""


def UB_AUTHORIZE_GUEST(http_client, controller_details, client_mac, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]
    _baseurl = "https://{}:{}".format(_address, _port)

    _request_url = '{}/api/s/{}/cmd/stamgr'.format(_baseurl, _site)
    if controller_details["type"] == 'unifios':  
        _request_url = '{}/proxy/network/api/s/{}/cmd/stamgr'.format(_baseurl, _site)

    _json_guest_request = {
        'cmd': 'authorize-guest',
        'mac': client_mac
    }
    # Update request based off data 
    if controller_details['minutes'] != 0:
        j = {
            'minutes': controller_details['minutes']
        }
        _json_guest_request.update(j)
    if controller_details['up'] != 0:
        j = {
            'up': controller_details['up']
        }
        _json_guest_request.update(j) 
    if controller_details['down'] != 0:
        j = {
            'down': controller_details['down']
        }
        _json_guest_request.update(j) 
    if controller_details['bytes'] != 0:
        j = {
            'bytes': controller_details['bytes']
        }
        _json_guest_request.update(j) 

    logging.debug("Using Request URL: {}".format(_request_url))
    logging.debug("Sending Data: {}".format(json.dumps(_json_guest_request)))

    _request = urllib.request.Request(_request_url, headers=headers, data=bytes(json.dumps(_json_guest_request), encoding="utf-8"))
    _response = _http_client.open(_request)
    r = _response.read()
    _current_status_code = _response.getcode()
    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_DEAUTHORIZE_GUEST(http_client, controller_details, client_mac, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]
    _baseurl = "https://{}:{}".format(_address, _port)

    _request_url = '{}/api/s/{}/cmd/stamgr'.format(_baseurl, _site)
    if controller_details["type"] == 'unifios':  
        _request_url = '{}/proxy/network/api/s/{}/cmd/stamgr'.format(_baseurl, _site)

    _json_guest_request = {
        'cmd': 'unauthorize-guest',
        'mac': client_mac
    }
    
    logging.debug("Using Request URL: {}".format(_request_url))
    logging.debug("Sending Data: {}".format(json.dumps(_json_guest_request)))
    _request = urllib.request.Request(_request_url, headers=headers, data=bytes(json.dumps(_json_guest_request), encoding="utf-8"))
    _response = _http_client.open(_request)

    r = _response.read()
    _current_status_code = _response.getcode()
    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_PROVISON_PORT_PROFILE(http_client, controller_details, headers):
    # Get Port Profiles
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]
    _baseurl = "https://{}:{}".format(_address, _port)

    _profile_url = '{}/api/s/{}/rest/portconf'.format(_baseurl, _site)
    if controller_details['type'] == 'unifios':
        _profile_url = '{}/proxy/network/api/s/{}/rest/portconf'.format(_baseurl, _site)
    logging.debug('Using Following URL: {}'.format(_profile_url))
    logging.debug('New Profile Name: {}'.format(controller_details['new_profile_name']))
    _profile_request = urllib.request.Request(_profile_url)
    _profile_response = _http_client.open(_profile_request)
    _port_profiles = {}
    _port_profiles = json.loads(_profile_response.read())['data']
    _profile_id = ''
    # find our profile ID based off the profile name
    for _profile in _port_profiles:
        if _profile['name'].lower() == controller_details['new_profile_name'].lower():
            _profile_id = _profile['_id']
            logging.debug('Found profile, ID: {}'.format(_profile_id))
    if _profile_id == '':
        _current_status_code = 998
        return _current_status_code

    # Get Existing Port Config
    _switch_response, _switch_data = UB_QUERY_DEVICE(http_client, controller_details, controller_details['switch_mac'], headers)
    _updated_port = {}
    _port_override_exists = False
    # Update the Config
    for _override in _switch_data['data'][0]['port_overrides']:
        if int(_override['port_idx']) == int(controller_details['port_index']):
            _port_override_exists = True
            _override['portconf_id'] = _profile_id
            logging.debug("Port Index Changed: {}".format(str(_override['port_idx'])))
            try:
                if _override['dot1x_ctrl'] != controller_details['dot1x_state']:
                    if controller_details['dot1x_state'] != 'inherit'.lower():
                        _override['dot1x_ctrl'] = controller_details['dot1x_state']
                        logging.debug('setting new state')
                    else:
                        del _override['dot1x_ctrl']
                        logging.debug('deleting override')
            except KeyError:
                logging.debug('dot1x_ctrl key not exist')
                if controller_details['dot1x_state'] != 'inherit'.lower():
                    _override['dot1x_ctrl'] = controller_details['dot1x_state']

    _updated_port['port_overrides'] = _switch_data['data'][0]['port_overrides']
    if _port_override_exists is False:
        p = {
            'port_idx': int(controller_details['port_index']),
            'portconf_id': _profile_id
        }
        _p_update = []
        _p_update = _updated_port['port_overrides']
        _p_update.append(p)
        _updated_port.update({'port_overrides': _p_update})
   
    logging.debug("Final Data to send: {}".format(json.dumps(_updated_port)))
    _switch_id = _switch_data['data'][0]['device_id']

    # send the request
    _sw_update_url = '{}/api/s/{}/rest/device/{}'.format(_baseurl, _site, _switch_id)
    if controller_details['type'] == 'unifios':
        _sw_update_url = '{}/proxy/network/api/s/{}/rest/device/{}'.format(_baseurl, _site, _switch_id)
    logging.debug("Using Update URL: {}".format(_sw_update_url))
    _update_request = urllib.request.Request(_sw_update_url, headers=headers, method='PUT', data=bytes(json.dumps(_updated_port), encoding="utf-8"))
    _update_response = _http_client.open(_update_request)

    r = _update_response.read()
    _current_status_code = _update_response.getcode()
    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data


def UB_DISCONNECT_CLIENT(http_client, controller_details, client_mac, headers):
    # disconnects endpoint from the network based off the MAC address of endpoint (Wireless only, switches do not listen to this)
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]
    _baseurl = "https://{}:{}".format(_address, _port)
    _request_url = '{}/api/s/{}/cmd/stamgr'.format(_baseurl, _site)
    if controller_details["type"] == 'unifios':  
        _request_url = '{}/proxy/network/api/s/{}/cmd/stamgr'.format(_baseurl, _site)

    json_block_request = {
        'cmd': 'kick-sta',
        'mac': client_mac
    }
    _request = urllib.request.Request(_request_url, headers=headers, data=bytes(json.dumps(json_block_request), encoding="utf-8"))
    _response = _http_client.open(_request)

    r = _response.read()
    _current_status_code = _response.getcode()
    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data
