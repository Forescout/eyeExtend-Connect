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
import urllib.parse
import urllib.error
import logging
from http.cookiejar import CookieJar


def clean_empty_dict(d):
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_empty_dict(v) for v in d) if v]
    return {k: v for k, v in ((k, clean_empty_dict(v)) for k, v in d.items()) if v or v is False}


def _api_prefix(controller_details):
    """
    UniFi OS controllers (API-key auth) serve the legacy Network API proxied under
    /proxy/network. Legacy self-hosted Network Application controllers (username/password
    auth, no UniFi OS layer) serve the same paths directly at /api. All UB_* functions below
    build their URLs through this helper so the same code works against either type.
    """
    return "/proxy/network" if controller_details.get("auth_mode") == "apikey" else ""


def UB_HTTP_CLIENT(credentials, controller_details):
    """
    Unifi API for the Unifi Controller.

    Dual-mode auth: if a username/password are supplied, use legacy session login
    (/api/login + cookie jar), which is what a self-hosted Network Application
    without UniFi OS requires. Otherwise fall back to API-key auth against a
    UniFi OS controller (X-API-KEY header, /proxy/network/integration/v1 paths).
    Sets controller_details["auth_mode"] so every subsequent UB_* call knows which
    URL scheme to use via _api_prefix().

    Username/password take precedence over the API key on purpose: the Connect
    engine's own "controller config field name" validation forces the API Key
    field to be non-empty whenever the controller address is set, even though
    it's declared "mandatory": "false" in system.conf. That means a legacy
    controller's row will always carry *some* placeholder text in the API Key
    box just to pass that platform check — so api_key alone can't be trusted to
    mean "use UniFi OS auth". Only fall through to API-key mode when there's no
    real username/password on file.
    """
    _current_status_code = None
    context = controller_details["ssl_context"]

    _address = controller_details["address"]
    _port = controller_details["port"]
    _baseurl = "https://{}:{}".format(_address, _port)

    _api_key = (credentials.get('api_key') or '').strip()
    _username = (credentials.get('username') or '').strip()
    _password = credentials.get('password') or ''

    cookie_jar = CookieJar()
    _handlers = [urllib.request.HTTPCookieProcessor(cookie_jar), urllib.request.HTTPSHandler(context=context)]
    _opener = urllib.request.build_opener(*_handlers)

    if not (_username and _password) and _api_key:
        controller_details["auth_mode"] = "apikey"
        _headers = {
            "Accept": "application/json",
            "X-API-KEY": _api_key
        }
        _check_url = '{}/proxy/network/integration/v1/sites'.format(_baseurl)
        logging.debug("Using Request URL: {}".format(_check_url))
        try:
            request = urllib.request.Request(_check_url, headers=_headers, method='GET')
            response = _opener.open(request, timeout=100)
            _current_status_code = response.getcode()
        except urllib.error.HTTPError as e:
            _current_status_code = e.code
            logging.error("HTTP Client authentication failed: HTTP Error {} - {}. Check API key and endpoint.".format(e.code, e.reason))
        except urllib.error.URLError as e:
            _current_status_code = None
            logging.error("HTTP Client connection failed: {}. Check controller address and network connectivity.".format(str(e.reason)))
        except Exception as e:
            _current_status_code = None
            logging.error("HTTP Client failed: {}.".format(str(e)))
        return _current_status_code, _opener, _headers

    # Legacy fallback: no API key supplied, use username/password session login.
    controller_details["auth_mode"] = "legacy"
    _headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8"
    }
    _login_url = '{}/api/login'.format(_baseurl)
    _login_data = {"username": _username, "password": _password}
    logging.debug("Using Request URL: {}".format(_login_url))
    try:
        request = urllib.request.Request(
            _login_url,
            data=bytes(json.dumps(_login_data), encoding="utf-8"),
            headers=_headers,
            method='POST'
        )
        response = _opener.open(request, timeout=100)
        _current_status_code = response.getcode()
    except urllib.error.HTTPError as e:
        _current_status_code = e.code
        logging.error("HTTP Client authentication failed: HTTP Error {} - {}. Check username/password.".format(e.code, e.reason))
    except urllib.error.URLError as e:
        _current_status_code = None
        logging.error("HTTP Client connection failed: {}. Check controller address and network connectivity.".format(str(e.reason)))
    except Exception as e:
        _current_status_code = None
        logging.error("HTTP Client failed: {}.".format(str(e)))
    return _current_status_code, _opener, _headers


def UB_LIST_SITES(http_client, controller_details, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _baseurl = "https://{}:{}".format(_address, _port)

    if controller_details.get("auth_mode") == "apikey":
        _request_url = '{}/proxy/network/integration/v1/sites'.format(_baseurl)
    else:
        # Legacy self-hosted controllers don't expose the integration/v1 API at all.
        _request_url = '{}/api/stat/sites'.format(_baseurl)

    request = urllib.request.Request(_request_url, headers=headers, method="GET")
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
    _request_url = '{}{}/api/s/{}/stat/sta'.format(_baseurl, _api_prefix(controller_details), _site)

    logging.debug("Using Request URL: {}".format(_request_url))

    request = urllib.request.Request(_request_url, headers=headers, method="GET")
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
    _request_url = '{}{}/api/s/{}/stat/device'.format(_baseurl, _api_prefix(controller_details), _site)
 
    request = urllib.request.Request(_request_url, headers=headers, method="GET")
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
    
    # FIX: this controller's REST router rejects a percent-encoded colon in the MAC path
    # segment (b4%3Afb%3A... -> 400 api.err.UnknownDevice); it wants the raw "b4:fb:..." mac
    # literally in the path. safe=":" keeps colons unescaped while still encoding anything
    # genuinely unsafe.
    _device_mac_enc = urllib.parse.quote(device_mac, safe=":")

    _device_url = "{}{}/api/s/{}/stat/device/{}".format(_baseurl, _api_prefix(controller_details), _site, _device_mac_enc)

    request = urllib.request.Request(_device_url, headers=headers, method="GET")
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

    # FIX: same as UB_QUERY_DEVICE -- keep colons unescaped, this controller wants the literal
    # "b4:fb:..." mac in the path, not "b4%3Afb%3A...".
    _client_mac_enc = urllib.parse.quote(client_mac, safe=":")

    _request_url = "{}{}/api/s/{}/stat/user/{}".format(_baseurl, _api_prefix(controller_details), _site, _client_mac_enc)

    request = urllib.request.Request(_request_url, headers=headers, method="GET")
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

    _request_url = "{}{}/api/s/{}/stat/stadpi".format(_baseurl, _api_prefix(controller_details), _site)

    # NEW: ensure we send JSON with the correct Content-Type for POST
    # WHY: Some controllers will reject or mis-handle POSTs without an explicit JSON Content-Type.
    _headers_local = dict(headers)
    _headers_local.setdefault("Content-Type", "application/json; charset=utf-8")

    # (Unchanged semantics) Request body: DPI stats by category for the given client MAC
    payload = {'type': 'by_cat', 'macs': [client_mac]}
    payload_bytes = json.dumps(payload).encode("utf-8")  # CHANGED: use a distinct name to avoid shadowing 'data' below

    # CHANGED: explicitly set method="POST"
    request = urllib.request.Request(_request_url, data=payload_bytes, headers=_headers_local, method="POST")

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

    _request_url = "{}{}/api/s/{}/cmd/stamgr".format(_baseurl, _api_prefix(controller_details), _site)

    # NEW: ensure JSON Content-Type for POST
    _headers_local = dict(headers)
    _headers_local.setdefault("Content-Type", "application/json; charset=utf-8")

    # (Unchanged semantics) Command payload to block a client by MAC
    payload = {'cmd': 'block-sta', 'mac': client_mac}
    payload_bytes = json.dumps(payload).encode("utf-8")  # CHANGED: distinct var name for clarity

    # CHANGED: explicitly set method="POST"
    request = urllib.request.Request(_request_url, data=payload_bytes, headers=_headers_local, method="POST")
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

    _request_url = "{}{}/api/s/{}/cmd/stamgr".format(_baseurl, _api_prefix(controller_details), _site)

    # NEW: ensure JSON Content-Type for POST
    _headers_local = dict(headers)
    _headers_local.setdefault("Content-Type", "application/json; charset=utf-8")

    # (Unchanged semantics) Command payload to unblock a client by MAC
    payload = {'cmd': 'unblock-sta', 'mac': client_mac}
    payload_bytes = json.dumps(payload).encode("utf-8")  # CHANGED: use a distinct var name for clarity

    # CHANGED: explicitly set method="POST"
    request = urllib.request.Request(_request_url, data=payload_bytes, headers=_headers_local, method="POST")
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

    _request_url = '{}{}/api/s/{}/rest/firewallgroup'.format(_baseurl, _api_prefix(controller_details), _site)
    logging.debug("Using Request URL: {}".format(_request_url))

    # CHANGED: make the initial list request explicitly a GET
    # WHY: Be explicit & future-proof; avoids accidental method changes if a body sneaks in later.
    _request = urllib.request.Request(_request_url, headers=headers, method="GET")  # CHANGED
    _response = _http_client.open(_request)
    _resp_body = _response.read()  # CHANGED: read once, reuse
    _firewall_groups = json.loads(_resp_body.decode("utf-8"))['data']  # CHANGED: explicit decode for clarity

    _ip_exists = False
    _group = None         # NEW: define upfront to avoid UnboundLocal if not found
    _group_id = None      # NEW: define upfront to avoid UnboundLocal if not found

    # Get the firewall group by name, and append our IP to the object
    for _f in _firewall_groups:
        if _f.get("name") == controller_details['group_name']:
            # CHANGED: default to [] if group_members is missing/None
            # WHY: Prevents TypeError when concatenating with a list.
            _current_members = _f.get("group_members") or []  # CHANGED
            if client_ip in _current_members:
                _ip_exists = True
                logging.debug("IP Already exists in group, doing nothing")
            else:
                _new_members = _current_members + [client_ip]
                _f.update({'group_members': _new_members})
                _group_id = _f.get('_id')
                _group = _f

    # NEW: handle case where the named group was not found
    # WHY: Avoids referencing _group/_group_id when they were never set.
    if _group is None and _ip_exists is False:  # NEW
        logging.debug("Firewall group '%s' not found; nothing to update", controller_details['group_name'])
        _current_status_code = 998  # NEW: distinct code for "group not found"
        return _current_status_code, ""

    logging.debug('Going to send data: {}'.format(_group))
    if _ip_exists is False:
        _fw_update_request_url = "{}/{}".format(_request_url, _group_id)

        # CHANGED: ensure JSON Content-Type on PUT
        # WHY: Some controllers reject/mis-handle PUT without explicit JSON content type.
        _headers_put = dict(headers)                                           # NEW
        _headers_put.setdefault("Content-Type", "application/json; charset=utf-8")  # NEW

        _update_request = urllib.request.Request(
            _fw_update_request_url,
            headers=_headers_put,                   # CHANGED
            method='PUT',
            data=bytes(json.dumps(_group), encoding="utf-8")
        )
        _update_response = _http_client.open(_update_request)

        _current_status_code = _update_response.getcode()
        r = _update_response.read()

        data = json.loads(r.decode("utf-8"))
        return _current_status_code, data
    else:
        _current_status_code = 999  # (kept) indicate "no change; IP already in group"
        return _current_status_code, ""


def UB_REM_FW_GROUP(http_client, controller_details, client_ip, headers, group_name):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]
    _baseurl = "https://{}:{}".format(_address, _port)

    _request_url = '{}{}/api/s/{}/rest/firewallgroup'.format(_baseurl, _api_prefix(controller_details), _site)
    logging.debug("Using Request URL: {}".format(_request_url))
    _ip_exists = False

    # CHANGED: explicitly GET the list of firewall groups
    _request = urllib.request.Request(_request_url, headers=headers, method="GET")  # CHANGED
    _response = _http_client.open(_request)
    _resp_body = _response.read()  # CHANGED: read once
    _firewall_groups = json.loads(_resp_body.decode("utf-8"))['data']  # CHANGED: explicit decode

    _group = None    # NEW: define upfront
    _group_id = None # NEW: define upfront

    for _f in _firewall_groups:
        # CHANGED: use the function parameter 'group_name' instead of controller_details['group_name']
        # WHY: The function already accepts 'group_name'; using it makes the API consistent and testable.
        if _f.get("name") == group_name:  # CHANGED
            _current_members = _f.get("group_members") or []  # CHANGED: default to [] if missing/None
            if client_ip in _current_members:
                _current_members.remove(client_ip)
                _f.update({'group_members': _current_members})
                _group_id = _f.get('_id')
                _group = _f
                _ip_exists = True
            else:
                _ip_exists = False
                logging.debug("IP does not exist in the group, doing nothing")

    # NEW: if the named group wasn't found at all, return a distinct status
    if _group is None and _ip_exists is False:  # NEW
        logging.debug("Firewall group '%s' not found; nothing to update", group_name)
        _current_status_code = 998  # NEW: "group not found"
        return _current_status_code, ""

    if _ip_exists is True:
        logging.debug("Sending Data: {}".format(json.dumps(_group)))
        _fw_update_request_url = "{}/{}".format(_request_url, _group_id)

        # CHANGED: ensure JSON Content-Type on PUT
        # WHY: Some controllers reject/mis-handle PUT without explicit JSON content type.
        _headers_put = dict(headers)                                           # NEW
        _headers_put.setdefault("Content-Type", "application/json; charset=utf-8")  # NEW

        _update_request = urllib.request.Request(
            _fw_update_request_url,
            headers=_headers_put,                  # CHANGED
            method='PUT',
            data=bytes(json.dumps(_group), encoding="utf-8")
        )
        _update_response = _http_client.open(_update_request)
        _current_status_code = _update_response.getcode()
        r = _update_response.read()

        data = json.loads(r.decode("utf-8"))
        return _current_status_code, data
    else:
        _current_status_code = 999  # (kept) "no change; IP not in group"
        return _current_status_code, ""

def UB_AUTHORIZE_GUEST(http_client, controller_details, client_mac, headers):
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]
    _baseurl = "https://{}:{}".format(_address, _port)

    _request_url = '{}{}/api/s/{}/cmd/stamgr'.format(_baseurl, _api_prefix(controller_details), _site)

    _json_guest_request = {
        'cmd': 'authorize-guest',
        'mac': client_mac
    }
    # (kept) Update request based off data
    if controller_details['minutes'] != 0:
        _json_guest_request.update({'minutes': controller_details['minutes']})
    if controller_details['up'] != 0:
        _json_guest_request.update({'up': controller_details['up']})
    if controller_details['down'] != 0:
        _json_guest_request.update({'down': controller_details['down']})
    if controller_details['bytes'] != 0:
        _json_guest_request.update({'bytes': controller_details['bytes']})

    logging.debug("Using Request URL: {}".format(_request_url))
    logging.debug("Sending Data: {}".format(json.dumps(_json_guest_request)))

    # NEW: ensure JSON Content-Type for POST
    _headers_local = dict(headers)  # NEW
    _headers_local.setdefault("Content-Type", "application/json; charset=utf-8")  # NEW

    # CHANGED: explicitly set method="POST" and add timeout to open()
    _request = urllib.request.Request(
        _request_url,
        headers=_headers_local,  # CHANGED
        data=bytes(json.dumps(_json_guest_request), encoding="utf-8"),
        method="POST"  # CHANGED
    )
    _response = _http_client.open(_request, timeout=100)  # CHANGED: added timeout

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

    _request_url = '{}{}/api/s/{}/cmd/stamgr'.format(_baseurl, _api_prefix(controller_details), _site)

    _json_guest_request = {
        'cmd': 'unauthorize-guest',
        'mac': client_mac
    }
    
    logging.debug("Using Request URL: {}".format(_request_url))
    logging.debug("Sending Data: {}".format(json.dumps(_json_guest_request)))

    # NEW: ensure JSON Content-Type for POST
    _headers_local = dict(headers)  # NEW
    _headers_local.setdefault("Content-Type", "application/json; charset=utf-8")  # NEW

    # CHANGED: explicitly set method="POST" and add timeout to open()
    _request = urllib.request.Request(
        _request_url,
        headers=_headers_local,  # CHANGED
        data=bytes(json.dumps(_json_guest_request), encoding="utf-8"),
        method="POST"  # CHANGED
    )
    _response = _http_client.open(_request, timeout=100)  # CHANGED: added timeout

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

    _profile_url = '{}{}/api/s/{}/rest/portconf'.format(_baseurl, _api_prefix(controller_details), _site)
    logging.debug('Using Following URL: {}'.format(_profile_url))
    logging.debug('New Profile Name: {}'.format(controller_details['new_profile_name']))

    # CHANGED: include headers and make the list call an explicit GET
    # WHY: We’re using API-key auth; some controllers reject requests without headers,
    #      and being explicit about the method is clearer/future-proof.
    _profile_request = urllib.request.Request(_profile_url, headers=headers, method="GET")  # CHANGED
    _profile_response = _http_client.open(_profile_request, timeout=100)  # CHANGED: added timeout for consistency
    _port_profiles = {}
    # CHANGED: decode explicitly before json.loads for clarity and to avoid bytes/str issues
    _port_profiles = json.loads(_profile_response.read().decode("utf-8"))['data']  # CHANGED

    _profile_id = ''
    # find our profile ID based off the profile name
    for _profile in _port_profiles:
        if _profile['name'].lower() == controller_details['new_profile_name'].lower():
            _profile_id = _profile['_id']
            logging.debug('Found profile, ID: {}'.format(_profile_id))

    if _profile_id == '':
        _current_status_code = 998
        # NOTE: preserving original behavior (return only status code in this branch)
        return _current_status_code  # (kept signature)

    # Get Existing Port Config
    _switch_response, _switch_data = UB_QUERY_DEVICE(http_client, controller_details, controller_details['switch_mac'], headers)

    _updated_port = {}
    _port_override_exists = False
    
    # NEW: Capture original port profile state for potential revert
    _original_profile_id = None
    _original_dot1x_ctrl = None

    # CHANGED: guard when device/port_overrides are missing; default to empty list
    # WHY: Prevent KeyError if the device has no overrides yet.
    device = _switch_data['data'][0] if (_switch_data and 'data' in _switch_data and _switch_data['data']) else {}  # CHANGED
    device.setdefault('port_overrides', [])  # CHANGED

    # Update the Config
    for _override in device['port_overrides']:
        if int(_override['port_idx']) == int(controller_details['port_index']):
            _port_override_exists = True
            # NEW: Capture original values before modification
            _original_profile_id = _override.get('portconf_id')
            _original_dot1x_ctrl = _override.get('dot1x_ctrl')
            _override['portconf_id'] = _profile_id
            logging.debug("Port Index Changed: {}".format(str(_override['port_idx'])))
            try:
                # CHANGED: normalize comparison on dot1x_state via .lower()
                # WHY: Avoids case-sensitivity bugs if caller passes 'INHERIT'/'Inherit', etc.
                if _override.get('dot1x_ctrl') != str(controller_details['dot1x_state']).lower():  # CHANGED
                    if str(controller_details['dot1x_state']).lower() != 'inherit':  # CHANGED
                        _override['dot1x_ctrl'] = str(controller_details['dot1x_state']).lower()
                        logging.debug('setting new state')
                    else:
                        # If inheriting, remove override if present
                        if 'dot1x_ctrl' in _override:
                            del _override['dot1x_ctrl']
                        logging.debug('deleting override')
            except KeyError:
                logging.debug('dot1x_ctrl key not exist')
                if str(controller_details['dot1x_state']).lower() != 'inherit':  # CHANGED
                    _override['dot1x_ctrl'] = str(controller_details['dot1x_state']).lower()  # CHANGED

    _updated_port['port_overrides'] = device['port_overrides']
    if _port_override_exists is False:
        # CHANGED: build/append override safely even if no prior overrides existed
        # WHY: Ensures a brand-new override list can be created cleanly.
        p = {
            'port_idx': int(controller_details['port_index']),
            'portconf_id': _profile_id
        }
        _p_update = list(_updated_port.get('port_overrides', []))  # CHANGED
        _p_update.append(p)
        _updated_port.update({'port_overrides': _p_update})

    logging.debug("Final Data to send: {}".format(json.dumps(_updated_port)))
    _switch_id = device.get('device_id')  # CHANGED: safer access

    # send the request
    _sw_update_url = '{}{}/api/s/{}/rest/device/{}'.format(_baseurl, _api_prefix(controller_details), _site, _switch_id)
    logging.debug("Using Update URL: {}".format(_sw_update_url))

    # CHANGED: ensure JSON Content-Type on PUT
    # WHY: Some controllers reject/mis-handle PUT without explicit JSON content type.
    _headers_put = dict(headers)  # CHANGED
    _headers_put.setdefault("Content-Type", "application/json; charset=utf-8")  # CHANGED

    # CHANGED: explicit method='PUT' and added timeout
    # WHY: Be explicit and consistent with other calls; timeout avoids hangs.
    _update_request = urllib.request.Request(
        _sw_update_url,
        headers=_headers_put,  # CHANGED
        method='PUT',          # CHANGED
        data=bytes(json.dumps(_updated_port), encoding="utf-8")
    )
    _update_response = _http_client.open(_update_request, timeout=100)  # CHANGED

    r = _update_response.read()
    _current_status_code = _update_response.getcode()
    data = json.loads(r.decode("utf-8"))
    
    # NEW: Add original state info to response for revert capability
    data['_original_state'] = {
        'profile_id': _original_profile_id,
        'dot1x_ctrl': _original_dot1x_ctrl,
        'switch_mac': controller_details['switch_mac'],
        'port_index': controller_details['port_index']
    }
    
    return _current_status_code, data


def UB_REVERT_PORT_PROFILE(http_client, controller_details, headers):
    """
    Reverts a port profile to its original state.
    Requires controller_details to contain:
    - switch_mac: MAC address of the switch
    - port_index: Port index to revert
    - original_profile_id: The original profile ID to restore
    - original_dot1x_ctrl: The original 802.1x control state (or None/inherit)
    """
    _http_client = http_client
    _address = controller_details["address"]
    _port = controller_details["port"]
    _site = controller_details["site"]
    _baseurl = "https://{}:{}".format(_address, _port)

    _original_profile_id = controller_details.get('original_profile_id')
    _original_dot1x_ctrl = controller_details.get('original_dot1x_ctrl')
    
    if not _original_profile_id:
        logging.debug("No original profile ID to revert to")
        return 997, {"message": "No original profile state available"}

    # Get Existing Port Config
    _switch_response, _switch_data = UB_QUERY_DEVICE(http_client, controller_details, controller_details['switch_mac'], headers)

    _updated_port = {}
    _port_override_exists = False

    device = _switch_data['data'][0] if (_switch_data and 'data' in _switch_data and _switch_data['data']) else {}
    device.setdefault('port_overrides', [])

    # Find and revert the port configuration
    for _override in device['port_overrides']:
        if int(_override['port_idx']) == int(controller_details['port_index']):
            _port_override_exists = True
            _override['portconf_id'] = _original_profile_id
            logging.debug("Reverting Port Index {}: profile_id={}".format(_override['port_idx'], _original_profile_id))
            
            # Restore original 802.1x control state
            if _original_dot1x_ctrl:
                _override['dot1x_ctrl'] = _original_dot1x_ctrl
                logging.debug('Restoring dot1x_ctrl to: {}'.format(_original_dot1x_ctrl))
            else:
                # If there was no original override, remove it
                if 'dot1x_ctrl' in _override:
                    del _override['dot1x_ctrl']
                    logging.debug('Removing dot1x_ctrl override (was inherited)')

    _updated_port['port_overrides'] = device['port_overrides']
    
    if _port_override_exists is False:
        # Port override doesn't exist anymore - create it with original values
        p = {
            'port_idx': int(controller_details['port_index']),
            'portconf_id': _original_profile_id
        }
        if _original_dot1x_ctrl:
            p['dot1x_ctrl'] = _original_dot1x_ctrl
            
        _p_update = list(_updated_port.get('port_overrides', []))
        _p_update.append(p)
        _updated_port.update({'port_overrides': _p_update})

    logging.debug("Final Data to send for revert: {}".format(json.dumps(_updated_port)))
    _switch_id = device.get('device_id')

    # Send the revert request
    _sw_update_url = '{}{}/api/s/{}/rest/device/{}'.format(_baseurl, _api_prefix(controller_details), _site, _switch_id)
    logging.debug("Using Update URL: {}".format(_sw_update_url))

    _headers_put = dict(headers)
    _headers_put.setdefault("Content-Type", "application/json; charset=utf-8")

    _update_request = urllib.request.Request(
        _sw_update_url,
        headers=_headers_put,
        method='PUT',
        data=bytes(json.dumps(_updated_port), encoding="utf-8")
    )
    _update_response = _http_client.open(_update_request, timeout=100)

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

    # (kept) Modern UniFi OS proxy path for client management commands
    _request_url = '{}{}/api/s/{}/cmd/stamgr'.format(_baseurl, _api_prefix(controller_details), _site)

    # CHANGED: ensure JSON Content-Type is present for POSTs
    _headers_local = dict(headers)
    _headers_local.setdefault("Content-Type", "application/json; charset=utf-8")

    # CHANGED: use a clear payload variable and encode once
    payload = {'cmd': 'kick-sta', 'mac': client_mac}
    payload_bytes = json.dumps(payload).encode("utf-8")

    # CHANGED: explicitly set method="POST" and add a timeout
    _request = urllib.request.Request(_request_url, headers=_headers_local, data=payload_bytes, method="POST")
    _response = _http_client.open(_request, timeout=100)  # CHANGED: added timeout

    r = _response.read()
    _current_status_code = _response.getcode()
    data = json.loads(r.decode("utf-8"))
    return _current_status_code, data