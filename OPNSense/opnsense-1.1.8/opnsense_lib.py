"""
OPNSense Connect App - Shared Library
Provides helper functions for OPNSense API communication.
Library files cannot access params directly - all values must be passed as arguments.
"""

import requests
import math
import re


# --- Multi-Instance / Controller Routing Helpers ---

def _ensure_list(value):
    """Ensure a param value is a list.

    The Connect framework pre-parses multi-instance field values into Python
    lists. For robustness (e.g. single-instance or edge cases), this helper
    also handles bare strings by splitting on commas.

    Args:
        value: A list (from framework pre-parsing) or a comma-separated string.

    Returns:
        list of stripped, non-empty strings
    """
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return []


def get_all_controllers(params):
    """Build a list of controller dicts from pre-parsed params.

    Used by poll and test scripts to iterate over all configured OPNSense instances.
    The Connect framework pre-parses multi-instance values into lists.

    Returns:
        list of dicts with keys: url, api_key, api_secret, lan_interface
    """
    all_urls = _ensure_list(params.get("connect_opnsense_url", ""))
    all_keys = _ensure_list(params.get("connect_opnsense_api_key", ""))
    all_secrets = _ensure_list(params.get("connect_opnsense_api_secret", ""))
    all_lans = _ensure_list(params.get("connect_opnsense_lan_interface", ""))

    controllers = []
    for i in range(len(all_urls)):
        if not all_urls[i]:
            continue
        controllers.append({
            "url": all_urls[i],
            "api_key": all_keys[i] if i < len(all_keys) else "",
            "api_secret": all_secrets[i] if i < len(all_secrets) else "",
            "lan_interface": all_lans[i] if i < len(all_lans) else ""
        })
    return controllers


def get_routed_controller(params):
    """Extract the framework-routed controller credentials for resolve/action scripts.

    When controller routing is enabled, the Connect framework provides:
      - connect_controller_ip_tag: the routed controller URL
      - connect_controller_api_key_tag: the routed controller API key

    The LAN interface requires index-based lookup since it is not a
    framework-routed tag.

    Falls back to single-controller behavior when routing tags are absent.

    Returns:
        dict with keys: url, api_key, api_secret, lan_interface
    """
    routed_url = params.get("connect_controller_ip_tag", "")
    routed_key = params.get("connect_controller_api_key_tag", "")

    all_urls = _ensure_list(params.get("connect_opnsense_url", ""))
    all_lans = _ensure_list(params.get("connect_opnsense_lan_interface", ""))

    if routed_url:
        # Use framework-provided URL and API key; look up LAN interface by index
        idx = _find_controller_index(routed_url, all_urls)
        all_secrets = _ensure_list(params.get("connect_opnsense_api_secret", ""))
        return {
            "url": all_urls[idx] if idx < len(all_urls) else routed_url,
            "api_key": routed_key,
            "api_secret": all_secrets[idx] if idx < len(all_secrets) else "",
            "lan_interface": all_lans[idx] if idx < len(all_lans) else ""
        }
    else:
        # Single-instance fallback (no routing tags present)
        all_keys = _ensure_list(params.get("connect_opnsense_api_key", ""))
        all_secrets = _ensure_list(params.get("connect_opnsense_api_secret", ""))
        return {
            "url": all_urls[0] if all_urls else "",
            "api_key": all_keys[0] if all_keys else "",
            "api_secret": all_secrets[0] if all_secrets else "",
            "lan_interface": all_lans[0] if all_lans else ""
        }


def _find_controller_index(routed_tag, all_urls):
    """Find the index of the controller matching the routed tag value.

    The framework's connect_controller_ip_tag may provide the full URL or
    just the IP/hostname. This tries exact match first, then fuzzy match
    by checking if the tag value appears within any configured URL.

    Returns:
        int index into all_urls (defaults to 0 if no match)
    """
    # Exact match
    try:
        return all_urls.index(routed_tag)
    except ValueError:
        pass

    # Fuzzy match: tag may be just an IP while config has full URL
    tag_lower = routed_tag.lower().rstrip("/")
    for i, url in enumerate(all_urls):
        url_lower = url.lower().rstrip("/")
        # Check if the tag appears in the URL (e.g. "192.168.1.1" in "https://192.168.1.1")
        if tag_lower in url_lower or url_lower in tag_lower:
            return i

    return 0


def build_proxies(proxy_enable, proxy_ip, proxy_port, proxy_user="", proxy_pass=""):
    """Build a proxies dict for the requests library from Connect proxy settings."""
    if proxy_enable != "true":
        return None
    if proxy_user:
        proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
    else:
        proxy_url = f"http://{proxy_ip}:{proxy_port}"
    return {"http": proxy_url, "https": proxy_url}


def get_proxies_from_params(params):
    """Extract proxy settings from params and build a proxies dict."""
    return build_proxies(
        params.get("connect_proxy_enable", ""),
        params.get("connect_proxy_ip", ""),
        params.get("connect_proxy_port", ""),
        params.get("connect_proxy_username", ""),
        params.get("connect_proxy_password", "")
    )


def opnsense_request(method, base_url, endpoint, api_key, api_secret,
                     verify=True, proxies=None, json_data=None):
    """Make an authenticated request to the OPNSense API.

    OPNSense uses HTTP Basic Auth with the API key as the username
    and the API secret as the password.

    Args:
        method: HTTP method (GET, POST)
        base_url: OPNSense firewall URL (e.g. https://192.168.1.1)
        endpoint: API path (e.g. /api/core/firmware/status)
        api_key: OPNSense API key
        api_secret: OPNSense API secret
        verify: SSL verification setting
        proxies: Proxy dict for requests
        json_data: JSON body for POST requests

    Returns:
        requests.Response object
    """
    url = f"{base_url.rstrip('/')}{endpoint}"
    resp = requests.request(
        method.upper(), url,
        auth=(api_key, api_secret),
        verify=verify, proxies=proxies,
        json=json_data
    )
    resp.raise_for_status()
    return resp


# --- Connection Test ---

def test_connection(base_url, api_key, api_secret, verify=True, proxies=None):
    """Test connectivity to OPNSense by fetching firmware status.

    Returns:
        dict with firmware status data
    """
    resp = opnsense_request("GET", base_url, "/api/core/firmware/status",
                            api_key, api_secret, verify=verify, proxies=proxies)
    return resp.json()


# --- System Information & Telemetry ---

def get_system_information(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get overall system information.

    Returns:
        dict with system info (name, versions, etc.)
    """
    resp = opnsense_request("GET", base_url,
                            "/api/diagnostics/system/system_information",
                            api_key, api_secret, verify=verify, proxies=proxies)
    return resp.json()


def get_system_resources(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get system resource usage (CPU, memory, processes).

    Returns:
        dict with resource data
    """
    resp = opnsense_request("GET", base_url,
                            "/api/diagnostics/system/system_resources",
                            api_key, api_secret, verify=verify, proxies=proxies)
    return resp.json()


def get_system_memory(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get memory statistics.

    Returns:
        dict with memory data
    """
    resp = opnsense_request("GET", base_url,
                            "/api/diagnostics/system/memory",
                            api_key, api_secret, verify=verify, proxies=proxies)
    return resp.json()


def get_system_disk(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get disk usage information.

    Returns:
        dict with disk data
    """
    resp = opnsense_request("GET", base_url,
                            "/api/diagnostics/system/system_disk",
                            api_key, api_secret, verify=verify, proxies=proxies)
    return resp.json()


def get_system_temperature(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get temperature sensor readings.

    Returns:
        dict with temperature data, or empty dict if no sensors
    """
    try:
        resp = opnsense_request("GET", base_url,
                                "/api/diagnostics/system/system_temperature",
                                api_key, api_secret, verify=verify, proxies=proxies)
        return resp.json()
    except Exception:
        return {}


def get_system_time(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get system time and uptime.

    Returns:
        dict with time/uptime data
    """
    resp = opnsense_request("GET", base_url,
                            "/api/diagnostics/system/system_time",
                            api_key, api_secret, verify=verify, proxies=proxies)
    return resp.json()


def get_cpu_type(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get CPU type information.

    Returns:
        dict with CPU model data
    """
    resp = opnsense_request("GET", base_url,
                            "/api/diagnostics/cpu_usage/get_c_p_u_type",
                            api_key, api_secret, verify=verify, proxies=proxies)
    return resp.json()


def get_firmware_info(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get firmware version information.

    Returns:
        dict with firmware details (product_version, product_name, etc.)
    """
    resp = opnsense_request("GET", base_url,
                            "/api/core/firmware/info",
                            api_key, api_secret, verify=verify, proxies=proxies)
    return resp.json()


# --- Network & Interface ---

def get_arp_table(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get the full ARP table from the firewall.

    Returns:
        list of ARP entry dicts with keys:
        ip, mac, manufacturer, intf, intf_description, hostname, expired, permanent
    """
    resp = opnsense_request("GET", base_url,
                            "/api/diagnostics/interface/get_arp",
                            api_key, api_secret, verify=verify, proxies=proxies)
    data = resp.json()
    # Response may wrap entries in a top-level key
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Try common wrapper keys
        for key in ("rows", "arp", ""):
            if key in data and isinstance(data[key], list):
                return data[key]
        # If the dict itself contains arp entries as values, return all values
        # that look like ARP entries
        entries = []
        for v in data.values():
            if isinstance(v, list):
                entries.extend(v)
        if entries:
            return entries
    return []


def get_interface_statistics(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get network interface statistics (bytes, packets, errors).

    Returns:
        dict keyed by interface name with statistics
    """
    resp = opnsense_request("GET", base_url,
                            "/api/diagnostics/interface/get_interface_statistics",
                            api_key, api_secret, verify=verify, proxies=proxies)
    data = resp.json()
    if isinstance(data, dict) and "statistics" in data:
        return data["statistics"]
    return data if isinstance(data, dict) else {}


def get_interfaces_info(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get comprehensive interface info including IPs and MACs.

    Returns:
        dict keyed by interface identifier with detailed info
    """
    resp = opnsense_request("GET", base_url,
                            "/api/interfaces/overview/interfaces_info?details=true",
                            api_key, api_secret, verify=verify, proxies=proxies)
    data = resp.json()
    if isinstance(data, dict) and "rows" in data:
        return data["rows"]
    return data if isinstance(data, dict) else {}


def get_pf_statistics(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get PF (packet filter) statistics.

    Returns:
        dict with PF stats (state count, etc.)
    """
    resp = opnsense_request("GET", base_url,
                            "/api/diagnostics/firewall/pf_statistics",
                            api_key, api_secret, verify=verify, proxies=proxies)
    return resp.json()


def get_pf_states(base_url, api_key, api_secret, verify=True, proxies=None):
    """Get current PF state count and limit.

    Returns:
        dict with keys 'current' and 'limit' (string values)
    """
    resp = opnsense_request("GET", base_url,
                            "/api/diagnostics/firewall/pf_states",
                            api_key, api_secret, verify=verify, proxies=proxies)
    return resp.json()


# --- Firewall Management Interface ---

def parse_management_interface(interfaces_info, lan_interface_hint=""):
    """Find the LAN interface and extract its MAC and IP.

    Lookup order:
      1. If lan_interface_hint is provided, match by device name or description
         (case-insensitive).
      2. If no hint (or hint didn't match), find the interface whose description
         is "LAN" (the default OPNSense LAN assignment).
      3. Fallback: first interface with an IPv4 address that is NOT the WAN
         (i.e., does not have a gateway).

    Args:
        interfaces_info: dict or list from get_interfaces_info()
        lan_interface_hint: optional device name (e.g. "vtnet0") or description
            (e.g. "LAN") from the config field

    Returns:
        (mac, ip) tuple - either may be None
    """
    if not interfaces_info:
        return None, None

    # Build a list of (key, iface_dict) tuples
    items = []
    if isinstance(interfaces_info, dict):
        for key, val in interfaces_info.items():
            if isinstance(val, dict):
                items.append((key, val))
    elif isinstance(interfaces_info, list):
        for val in interfaces_info:
            if isinstance(val, dict):
                items.append(("", val))
    if not items:
        return None, None

    best = None
    hint = (lan_interface_hint or "").strip()

    # --- Pass 1: match by user-provided hint ---
    if hint:
        hint_lower = hint.lower()
        for key, iface in items:
            # Match against device name (key or "device" field) or description
            device_name = (iface.get("device", "") or key or "").lower()
            description = (iface.get("description", "") or "").lower()
            identifier = (iface.get("identifier", "") or "").lower()
            if hint_lower in (device_name, description, identifier):
                best = iface
                break

    # --- Pass 2: find the interface assigned as "LAN" ---
    if not best:
        for key, iface in items:
            description = (iface.get("description", "") or "").strip()
            if description.upper() == "LAN":
                best = iface
                break

    # --- Pass 3: fallback to first non-WAN interface with an IPv4 address ---
    if not best:
        for key, iface in items:
            # Skip interfaces that have a gateway (those are WAN)
            has_gateway = False
            if iface.get("gateway"):
                has_gateway = True
            routes = iface.get("routes", [])
            if isinstance(routes, list):
                for route in routes:
                    if isinstance(route, dict) and route.get("gateway"):
                        has_gateway = True
                        break
            if has_gateway:
                continue
            addr = _extract_ipv4(iface)
            if addr:
                best = iface
                break

    # --- Final fallback: any interface with an IPv4 address ---
    if not best:
        for key, iface in items:
            addr = _extract_ipv4(iface)
            if addr:
                best = iface
                break

    if not best:
        return None, None

    ip = _extract_ipv4(best)
    mac = _extract_mac(best)

    return mac, ip


def _extract_ipv4(iface):
    """Extract the first non-loopback IPv4 address from an interface dict."""
    # Try direct fields
    for field in ("ipv4", "addr", "address", "ipaddr"):
        val = iface.get(field)
        if isinstance(val, str) and val and not val.startswith("127."):
            # Strip CIDR if present
            return val.split("/")[0]
        if isinstance(val, list):
            for entry in val:
                if isinstance(entry, dict):
                    addr = entry.get("ipaddr", "") or entry.get("address", "")
                    if addr and not addr.startswith("127."):
                        return addr.split("/")[0]
                elif isinstance(entry, str) and entry and not entry.startswith("127."):
                    return entry.split("/")[0]
    return None


def _extract_mac(iface):
    """Extract MAC address from an interface dict and convert to Forescout format."""
    for field in ("macaddr", "mac", "hwaddr", "ether"):
        val = iface.get(field)
        if isinstance(val, str) and val and re.match(r'^[0-9A-Fa-f:]{17}$', val):
            return val.replace(":", "").upper()
    return None


def normalize_mac(mac_str):
    """Convert a MAC address string to Forescout 12-char uppercase hex format.

    Handles formats like:
        AA:BB:CC:DD:EE:FF
        aa:bb:cc:dd:ee:ff
        AA-BB-CC-DD-EE-FF
        aabbccddeeff

    Returns:
        12-char uppercase hex string, or None if invalid
    """
    if not mac_str:
        return None
    cleaned = mac_str.replace(":", "").replace("-", "").replace(".", "").upper()
    if len(cleaned) == 12 and all(c in "0123456789ABCDEF" for c in cleaned):
        return cleaned
    return None


# --- Firewall Alias Management ---

def add_to_alias(base_url, api_key, api_secret, alias_name, address,
                 verify=True, proxies=None):
    """Add an IP address to an OPNSense alias.

    Args:
        alias_name: Name of the alias on the firewall
        address: IP address to add

    Returns:
        API response dict
    """
    endpoint = f"/api/firewall/alias_util/add/{alias_name}"
    resp = opnsense_request("POST", base_url, endpoint, api_key, api_secret,
                            verify=verify, proxies=proxies,
                            json_data={"address": address})
    return resp.json()


def delete_from_alias(base_url, api_key, api_secret, alias_name, address,
                      verify=True, proxies=None):
    """Remove an IP address from an OPNSense alias.

    Args:
        alias_name: Name of the alias on the firewall
        address: IP address to remove

    Returns:
        API response dict
    """
    endpoint = f"/api/firewall/alias_util/delete/{alias_name}"
    resp = opnsense_request("POST", base_url, endpoint, api_key, api_secret,
                            verify=verify, proxies=proxies,
                            json_data={"address": address})
    return resp.json()


def reconfigure_aliases(base_url, api_key, api_secret, verify=True, proxies=None):
    """Apply alias changes on the firewall.

    Must be called after add_to_alias or delete_from_alias to make changes effective.

    Returns:
        API response dict
    """
    resp = opnsense_request("POST", base_url,
                            "/api/firewall/alias/reconfigure",
                            api_key, api_secret, verify=verify, proxies=proxies,
                            json_data={})
    return resp.json()


# --- Utility ---

def bytes_to_mb(value):
    """Convert bytes to megabytes, rounded down."""
    if value and value > 0:
        return math.floor(value / 1048576)
    return 0


def bytes_to_gb(value):
    """Convert bytes to gigabytes, rounded down."""
    if value and value > 0:
        return math.floor(value / 1073741824)
    return 0


def safe_int(value):
    """Safely convert a value to int."""
    try:
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def parse_size_gb(size_str):
    """Parse a size string (e.g. '50G', '1024M', '1073741824') to GB."""
    if not size_str:
        return 0
    size_str = str(size_str).strip().upper()
    try:
        if size_str.endswith("T"):
            return int(float(size_str[:-1]) * 1024)
        elif size_str.endswith("G"):
            return int(float(size_str[:-1]))
        elif size_str.endswith("M"):
            return int(float(size_str[:-1]) / 1024)
        elif size_str.endswith("K"):
            return int(float(size_str[:-1]) / 1048576)
        else:
            return bytes_to_gb(int(float(size_str)))
    except (ValueError, TypeError):
        return 0


def parse_pct(pct_str):
    """Parse a percentage string (e.g. '45%', '45') to int."""
    if not pct_str:
        return 0
    pct_str = str(pct_str).strip().rstrip("%")
    try:
        return int(float(pct_str))
    except (ValueError, TypeError):
        return 0
