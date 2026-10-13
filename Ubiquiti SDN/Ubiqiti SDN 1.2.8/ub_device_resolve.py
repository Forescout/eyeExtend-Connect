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

# Fallback to v1.2.4 parameters if v1.2.6 parameters not present
credentials["api_key"] = params.get("connect_controller_api_key_tag") or params.get("connect_ubiquitisdn_api_key")
# Legacy self-hosted controllers (no UniFi OS / API key support) authenticate with
# username/password instead. UB_HTTP_CLIENT() picks whichever is populated.
credentials["username"] = params.get("connect_ubiquitisdn_username")
credentials["password"] = params.get("connect_ubiquitisdn_password")

controller_details["address"] = params.get("connect_controller_ip_tag") or params.get("connect_ubiquitisdn_controller_address")
controller_details["port"] = params.get("connect_ubiquitisdn_controller_port") or 8443
# Use endpoint-specific site property, not global config
controller_details["site"] = params.get("connect_ubiquitisdn_site", "default")
controller_details["all_sites"] = params.get("connect_ubiquitisdn_discover_all_sites", "false")
controller_details["ssl_context"] = ssl_context

code, client, headers = UB_API_NONOO.UB_HTTP_CLIENT(credentials, controller_details)

# Flat keys that map straight across from the stat/device response.
ubiquiti_property_map = {
    "model": "connect_ubiquitisdn_device_model",
    "serial": "connect_ubiquitisdn_device_serial",
    "type": "connect_ubiquitisdn_device_type",
    "name": "connect_ubiquitisdn_device_name",
    "version": "connect_ubiquitisdn_device_firmware",
    "ip": "connect_ubiquitisdn_device_ip",
    "state": "connect_ubiquitisdn_device_state",
    "adopted": "connect_ubiquitisdn_device_adopted",
    "uptime": "connect_ubiquitisdn_device_uptime_seconds",
    "num_sta": "connect_ubiquitisdn_device_num_clients",
    "guest-num-sta": "connect_ubiquitisdn_device_num_guests",
    "satisfaction": "connect_ubiquitisdn_device_satisfaction_pct",
}


def _format_uptime(seconds):
    """9d 2h 13m 10s style string, matching the controller UI's General panel."""
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return None
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    return "{}d {}h {}m {}s".format(days, hours, minutes, secs)


def _extract_load_average(device_details):
    # Field name varies by controller build: legacy self-hosted controllers report
    # raw loadavg under sys_stats; some newer builds duplicate it under system-stats.
    stats = device_details.get("sys_stats") or device_details.get("system-stats") or {}
    parts = [stats.get("loadavg1"), stats.get("loadavg5"), stats.get("loadavg15")]
    if all(p is None for p in parts):
        return None
    return " / ".join(str(p) if p is not None else "-" for p in parts)


def _extract_memory_pct(device_details):
    stats = device_details.get("sys_stats") or {}
    mem = stats.get("mem")
    if mem is None:
        mem = (device_details.get("system-stats") or {}).get("mem")
    return mem


def _extract_wifi_membership(device_details):
    # vap_table lists this AP's virtual APs (one per SSID/radio); essid is the SSID name.
    vaps = device_details.get("vap_table") or []
    ssids = sorted({v.get("essid") for v in vaps if v.get("essid")})
    return ", ".join(ssids) if ssids else None


logging.debug("Login to Ubiquiti Controller [{}] returned code [{}]".format(controller_details["address"], code))
if code == 200:
    if "mac" in params:
        if "connect_ubiquitisdn_role" in params:
            if params["connect_ubiquitisdn_role"] == "Device":
                # Add if no connect_ubiquitisdn_site defined then set site to default
                # TODO: if discovery is not enabled there is no way to learn connect_ubiquitisdn_site
                #       Need to create a resolve script
                controller_details["site"] = params.get("connect_ubiquitisdn_site", "default")
                mac = ':'.join(params["mac"][i:i + 2] for i in range(0, 12, 2))
                logging.debug("Attempting API Query for MAC [{}]".format(mac))
                try:
                    query_code, query_results = UB_API_NONOO.UB_QUERY_DEVICE(client, controller_details, mac, headers)
                    if not len(query_results) == 0:
                        device_details = query_results["data"][0]
                        logging.debug("API Query returned code [{}] and response [{}]".format(query_code, query_results))

                        properties = {}
                        for key, value in device_details.items():
                            if key in ubiquiti_property_map:
                                properties[ubiquiti_property_map[key]] = value

                        # Derived/nested fields the flat map above can't reach directly.
                        uptime_fmt = _format_uptime(device_details.get("uptime"))
                        if uptime_fmt:
                            properties["connect_ubiquitisdn_device_uptime"] = uptime_fmt

                        load_avg = _extract_load_average(device_details)
                        if load_avg:
                            properties["connect_ubiquitisdn_device_load_average"] = load_avg

                        mem_pct = _extract_memory_pct(device_details)
                        if mem_pct is not None:
                            properties["connect_ubiquitisdn_device_memory_pct"] = mem_pct

                        wifi_membership = _extract_wifi_membership(device_details)
                        if wifi_membership:
                            properties["connect_ubiquitisdn_device_wifi_membership"] = wifi_membership

                        response["properties"] = properties
                    else:
                        response["error"] = "Could not find this endpoint in the Unifi SDN Controller."
                except Exception as e:
                    response["error"] = "Query device failed: {}".format(str(e))
            else:
                response["error"] = "This property only applies to Ubiquiti SDN Discovered Devices."
        else:
            response["error"] = "Ubiquiti SDN Role determination is required to resolve this property."
    else:
        response["error"] = "No mac address to query the device."
else:
    response["error"] = "API Connection Failed, check configuration."

logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
