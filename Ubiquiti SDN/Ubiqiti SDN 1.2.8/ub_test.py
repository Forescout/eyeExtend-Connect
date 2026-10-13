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
import logging

credentials = {}
controller_details = {}
response = {}
sites = []

# CHANGE: parse aligned comma-separated lists for address, api_key/username/password, and site.
# A controller with no API key (legacy self-hosted, no UniFi OS) leaves that slot in the
# api_key list empty and instead fills the matching username/password slot; UB_HTTP_CLIENT
# picks whichever credential is populated for that controller.
#
# FIX: with "Enable Controller Routing" on, the engine hands scripts the controller
# address/API key under generic aliases (connect_controller_ip_tag /
# connect_controller_api_key_tag) instead of the app-specific field IDs -- ub_device_resolve.py
# and ub_basic_details.py already check those aliases first, but this script (as shipped by
# Forescout in 1.2.7) used direct params[...] lookups with no fallback and raised a raw
# KeyError on 'connect_ubiquitisdn_controller_address' as soon as routing was enabled.
_address_raw = params.get("connect_controller_ip_tag") or params.get("connect_ubiquitisdn_controller_address") or ""
_api_key_raw = params.get("connect_controller_api_key_tag") or params.get("connect_ubiquitisdn_api_key") or ""
_sites_raw = params.get("connect_ubiquitisdn_site_name") or params.get("connect_ubiquitisdn_site") or "default"

_addresses = [a.strip() for a in _address_raw.split(",")]
_api_keys = [k.strip() for k in _api_key_raw.split(",")]
_sites    = [s.strip() for s in _sites_raw.split(",")]
_usernames = [u.strip() for u in params.get("connect_ubiquitisdn_username", "").split(",")]
_passwords = [p for p in params.get("connect_ubiquitisdn_password", "").split(",")]

# TEMP DIAGNOSTIC: if the address alias resolution above came up empty, surface the actual
# parameter keys the platform handed this script (never their values) so we can see the real
# key name instead of guessing at more aliases.
_diag_prefix = ""
if not _address_raw:
    try:
        _diag_prefix = "[DIAG] params keys seen: {}\n".format(sorted(params.keys()))
    except Exception as _diag_e:
        _diag_prefix = "[DIAG] could not list params keys: {}\n".format(str(_diag_e))


def _at(lst, i, default=""):
    return lst[i] if i < len(lst) else default

# credentials["api_key"] = params["connect_ubiquitisdn_api_key"]
# controller_details["address"] = params["connect_ubiquitisdn_controller_address"]
# controller_details["site"] = params["connect_ubiquitisdn_site_name"]

controller_details["port"] = params.get("connect_ubiquitisdn_controller_port") or 8443
controller_details["all_sites"] = params.get("connect_ubiquitisdn_discover_all_sites", "false")
controller_details["ssl_context"] = ssl_context

overall_messages = []
any_success = False

# CHANGE: iterate by index so each address/site/api_key align
for i in range(len(_addresses)):
    controller_details["address"] = _addresses[i]
    controller_details["site"] = _sites[i]
    credentials["api_key"] = _at(_api_keys, i)
    credentials["username"] = _at(_usernames, i)
    credentials["password"] = _at(_passwords, i)

    code, client, headers = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)
    logging.debug("Login return code: {}".format(str(code)))
    logging.debug("Attempting Ubiquiti SDN with: address={} port={} site={}".format(
            controller_details["address"], controller_details["port"],controller_details["site"]))


    if code == 200:
        try:
            message = []
            sites = []  # reset per controller

            if controller_details["all_sites"] == "true":
                message.append("({}) Querying controller for all managed sites.".format(controller_details["address"]))
                sites_code, query_results = UB_API_NONOO.UB_LIST_SITES(client, controller_details, headers)
                sites_detail = query_results["data"]
                # FIX: the site-id field name differs by controller type -- UniFi OS's
                # integration/v1 API (apikey mode) calls it "internalReference"; a legacy
                # self-hosted controller's /api/stat/sites (legacy mode) calls it "name".
                # The original code hardcoded "internalReference" only, which would KeyError
                # against a legacy controller's response.
                _site_id_key = "internalReference" if controller_details.get("auth_mode") == "apikey" else "name"
                for site in sites_detail:
                    sites.append(site.get(_site_id_key) or site.get("name") or site.get("internalReference"))
            else:
                sites_config = controller_details["site"]
                message.append("({}) Querying controller for the following managed sites: {}".format(
                    controller_details["address"], sites_config))
                sites_list = sites_config.split(",")
                for site in sites_list:
                    sites.append(site)
                logging.debug("Site List: {}".format(list(sites)))

            for site in sites:
                controller_details["site"] = site
                client_code, connected_clients = UB_API_NONOO.UB_LIST_CLIENTS(client, controller_details, headers)
                logging.debug("API Client Query returned code [{}] and response [{}]".format(client_code, connected_clients))

                device_code, connected_devices = UB_API_NONOO.UB_LIST_DEVICES(client, controller_details, headers)
                logging.debug("API Device Query returned code [{}] and response [{}]".format(device_code, connected_devices))

                message.append("({}) Found {} connected clients and {} SDN devices in site: {}".format(
                    controller_details["address"],len(connected_clients["data"]),len(connected_devices["data"]),controller_details["site"])
                )

            any_success = True
            overall_messages.extend(message)
        except Exception as e:
            overall_messages.append("({}) Test failed: {}".format(controller_details["address"], str(e)))
    else:
        error_msg = "({}) API connection failed - Status code: {}. Check API key or username/password, and controller address.".format(
            controller_details["address"], code if code else "None/403 Forbidden")
        overall_messages.append(error_msg)
        logging.error(error_msg)

# preserve original response shape
if any_success:
    response["succeeded"] = True
    response["result_msg"] = "\n".join(overall_messages)
else:
    response["succeeded"] = False
    _failure_text = _diag_prefix + ("\n".join(overall_messages) if overall_messages else "No controllers processed successfully.")
    # FIX: the console's generic Test dialog only recognizes "result_msg" (success) or
    # "error" (failure) -- it has no idea what to do with "troubleshooting" (what Forescout's
    # shipped 1.2.7 code actually sets here), so a real failure was rendered as the unhelpful
    # "No result_msg or error tag in response" instead of the actual reason. Set both so the
    # real diagnostic text shows up.
    response["troubleshooting"] = _failure_text
    response["error"] = _failure_text