"""
Oracle KVM Connect App - Shared Library
Helper functions for communicating with the OLVM (oVirt) REST API.
Uses OAuth2 SSO token authentication.
"""

import requests
import logging
import urllib.parse


# ---------------------------------------------------------------------------
# Response normalization
# ---------------------------------------------------------------------------

def ensure_list(val):
    """oVirt returns a single dict when there is 1 result, a list for >1.

    This normalises the response so callers always get a list.
    """
    if val is None:
        return []
    if isinstance(val, dict):
        return [val]
    if isinstance(val, list):
        return val
    return []


def normalize_mac(raw_mac):
    """Convert any MAC format to Forescout's 12-char uppercase hex.

    Forescout requires MAC as '001122334455' — no colons, dashes, or dots.
    """
    if not raw_mac:
        return None
    return raw_mac.replace(":", "").replace("-", "").replace(".", "").upper()


# ---------------------------------------------------------------------------
# Proxy helpers
# ---------------------------------------------------------------------------

def build_proxies(proxy_host, proxy_port):
    """Build a proxy dict for requests."""
    if proxy_host and proxy_port:
        proxy_url = f"https://{proxy_host}:{proxy_port}"
        return {"https": proxy_url, "http": proxy_url}
    return {}


def get_proxies_from_params(p):
    """Extract proxy settings from Connect params."""
    return build_proxies(
        p.get("connect_proxy_host", ""),
        p.get("connect_proxy_port", "")
    )


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def get_auth_header(p):
    """Return HTTP headers with Bearer token Authorization.

    The token is obtained by the authorization script and cached in
    ``connect_authorization_token``.
    """
    headers = {
        "Accept": "application/json",
        "Version": "4",
    }

    token = p.get("connect_authorization_token", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        logging.warning("Oracle KVM: no authorization token available")

    return headers


# ---------------------------------------------------------------------------
# HTTP request wrapper
# ---------------------------------------------------------------------------

def olvm_request(method, url, p, verify=True, proxies=None, **kwargs):
    """Make an authenticated request to the OLVM API.

    Returns the parsed JSON body.  Raises on HTTP errors.
    """
    headers = get_auth_header(p)
    resp = requests.request(
        method,
        url,
        headers=headers,
        verify=verify,
        proxies=proxies or {},
        **kwargs,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Test / Connectivity
# ---------------------------------------------------------------------------

def test_connection(base_url, p, verify=True, proxies=None):
    """Hit the API root to verify connectivity and auth.

    Returns the product_info dict from the API root response.
    """
    url = f"{base_url.rstrip('/')}/ovirt-engine/api"
    data = olvm_request("GET", url, p, verify=verify, proxies=proxies)
    return data.get("product_info", {})


# ---------------------------------------------------------------------------
# VM helpers
# ---------------------------------------------------------------------------

def get_all_vms(base_url, p, verify=True, proxies=None):
    """Paginate through /api/vms and return the full list of VM dicts.

    Uses the ``follow`` parameter to inline nics and reported_devices
    so that MAC/IP can be extracted without per-VM API calls.
    """
    all_vms = []
    page = 1
    page_size = 100
    api_root = f"{base_url.rstrip('/')}/ovirt-engine/api"

    while True:
        url = (f"{api_root}/vms?max={page_size}&search=page+{page}"
               f"&follow=nics,reported_devices")
        data = olvm_request("GET", url, p, verify=verify, proxies=proxies)
        vms = ensure_list(data.get("vm"))
        logging.info(f"Oracle KVM get_all_vms page {page}: got {len(vms)} VMs")
        if not vms:
            break
        all_vms.extend(vms)
        if len(vms) < page_size:
            break
        page += 1

    return all_vms


def extract_vm_nics_inline(vm):
    """Extract NIC list from an inline-followed VM dict."""
    nics_block = vm.get("nics") or vm.get("nic") or {}
    if isinstance(nics_block, dict):
        return ensure_list(nics_block.get("nic"))
    return ensure_list(nics_block)


def extract_vm_reported_devices_inline(vm):
    """Extract reported devices from an inline-followed VM dict."""
    rd_block = vm.get("reported_devices") or vm.get("reported_device") or {}
    if isinstance(rd_block, dict):
        return ensure_list(rd_block.get("reported_device"))
    return ensure_list(rd_block)


def get_vm_reported_devices(base_url, vm_id, p, verify=True, proxies=None):
    """Get the reported devices (NICs with MAC/IP) for a VM.

    Returns a list of reported-device dicts.  Falls back to empty list.
    """
    url = (f"{base_url.rstrip('/')}/ovirt-engine/api"
           f"/vms/{vm_id}/reporteddevices")
    try:
        data = olvm_request("GET", url, p, verify=verify, proxies=proxies)
        devs = ensure_list(data.get("reported_device"))
        logging.debug(f"Oracle KVM reported_devices for {vm_id}: {len(devs)} devices")
        return devs
    except Exception as e:
        logging.warning(f"Oracle KVM: failed to get reported devices for VM {vm_id}: {e}")
        return []


def get_vm_nics(base_url, vm_id, p, verify=True, proxies=None):
    """Get the NIC definitions for a VM (for MAC when reported devices are empty).

    Returns a list of NIC dicts.
    """
    url = (f"{base_url.rstrip('/')}/ovirt-engine/api"
           f"/vms/{vm_id}/nics")
    try:
        data = olvm_request("GET", url, p, verify=verify, proxies=proxies)
        nics = ensure_list(data.get("nic"))
        logging.debug(f"Oracle KVM NICs for VM {vm_id}: {len(nics)} nics")
        return nics
    except Exception as e:
        logging.warning(f"Oracle KVM: failed to get NICs for VM {vm_id}: {e}")
        return []


def parse_vm_mac_and_ip(reported_devices, nics):
    """Extract the first non-loopback MAC and IPv4 address from a VM.

    Tries reported_devices first (populated by guest-agent), then falls back
    to NIC definitions for MAC only.
    """
    mac = None
    ip_address = None

    for dev in reported_devices:
        dev_mac = dev.get("mac", {}).get("address", "")
        if dev_mac:
            mac = normalize_mac(dev_mac)
        # Look for IPv4 in the ips list
        ips_block = dev.get("ips", {}) or {}
        ips = ensure_list(ips_block.get("ip"))
        for ip_entry in ips:
            if ip_entry.get("version") == "v4":
                addr = ip_entry.get("address", "")
                if addr and not addr.startswith("127."):
                    ip_address = addr
                    break
        if mac and ip_address:
            break

    # Fallback: get MAC from NIC definitions
    if not mac:
        for nic in nics:
            nic_mac = nic.get("mac", {}).get("address", "")
            if nic_mac:
                mac = normalize_mac(nic_mac)
                break

    return mac, ip_address


def parse_vm_properties(vm, cluster_map=None, host_map=None):
    """Extract Connect properties from a single oVirt VM dict."""
    props = {}

    props["connect_oraclekvm_vm_id"] = vm.get("id", "")
    props["connect_oraclekvm_name"] = vm.get("name", "")
    props["connect_oraclekvm_status"] = vm.get("status", "unknown")
    props["connect_oraclekvm_online"] = vm.get("status", "") == "up"
    props["connect_oraclekvm_type"] = vm.get("type", "")
    props["connect_oraclekvm_description"] = vm.get("comment", "") or vm.get("description", "") or ""

    os_block = vm.get("os", {})
    props["connect_oraclekvm_os_type"] = os_block.get("type", "") if os_block else ""

    props["connect_oraclekvm_fqdn"] = vm.get("fqdn", "") or ""

    cpu = vm.get("cpu", {})
    topo = cpu.get("topology", {}) if cpu else {}
    sockets = int(topo.get("sockets", 1))
    cores = int(topo.get("cores", 1))
    threads = int(topo.get("threads", 1))
    props["connect_oraclekvm_cpu_cores"] = sockets * cores * threads

    mem_bytes = int(vm.get("memory", 0))
    props["connect_oraclekvm_memory_mb"] = bytes_to_mb(mem_bytes)

    # Cluster name
    cluster_ref = vm.get("cluster", {})
    cluster_id = cluster_ref.get("id", "") if cluster_ref else ""
    if cluster_map and cluster_id in cluster_map:
        props["connect_oraclekvm_cluster"] = cluster_map[cluster_id]
    else:
        props["connect_oraclekvm_cluster"] = cluster_id

    # Running host
    host_ref = vm.get("host", {})
    host_id = host_ref.get("id", "") if host_ref else ""
    if host_map and host_id in host_map:
        props["connect_oraclekvm_host_affinity"] = host_map[host_id]
    else:
        props["connect_oraclekvm_host_affinity"] = host_id

    # Creation time (epoch ms)
    creation = vm.get("creation_time")
    if creation:
        props["connect_oraclekvm_creation_time"] = parse_timestamp(creation)

    # Uptime — start_time is available when the VM is up
    start_time = vm.get("start_time")
    if start_time:
        props["connect_oraclekvm_uptime"] = format_uptime_from_start(start_time)
    else:
        props["connect_oraclekvm_uptime"] = ""

    return props


# ---------------------------------------------------------------------------
# Host helpers
# ---------------------------------------------------------------------------

def get_all_hosts(base_url, p, verify=True, proxies=None):
    """Paginate through /api/hosts and return full list.

    Uses the ``follow`` parameter to inline nics so that MAC/IP
    can be extracted without per-host API calls.
    """
    all_hosts = []
    page = 1
    page_size = 100
    api_root = f"{base_url.rstrip('/')}/ovirt-engine/api"

    while True:
        url = (f"{api_root}/hosts?max={page_size}&search=page+{page}"
               f"&follow=nics")
        data = olvm_request("GET", url, p, verify=verify, proxies=proxies)
        hosts = ensure_list(data.get("host"))
        logging.info(f"Oracle KVM get_all_hosts page {page}: got {len(hosts)} hosts")
        if not hosts:
            break
        all_hosts.extend(hosts)
        if len(hosts) < page_size:
            break
        page += 1

    return all_hosts


def extract_host_nics_inline(host):
    """Extract NIC list from an inline-followed host dict."""
    nics_block = host.get("nics") or host.get("host_nic") or {}
    if isinstance(nics_block, dict):
        return ensure_list(nics_block.get("host_nic"))
    return ensure_list(nics_block)


def get_host_nics(base_url, host_id, p, verify=True, proxies=None):
    """Get the NIC list for a host. Returns list of NIC dicts."""
    url = (f"{base_url.rstrip('/')}/ovirt-engine/api"
           f"/hosts/{host_id}/nics")
    try:
        data = olvm_request("GET", url, p, verify=verify, proxies=proxies)
        nics = ensure_list(data.get("host_nic"))
        logging.debug(f"Oracle KVM host NICs for {host_id}: {len(nics)} nics")
        return nics
    except Exception as e:
        logging.warning(f"Oracle KVM: failed to get NICs for host {host_id}: {e}")
        return []


def parse_host_mac_and_ip(nics):
    """Extract the management MAC and IP from the host NIC list.

    Returns (mac, ip).
    """
    mac = None
    ip_address = None

    for nic in nics:
        nic_ip_block = nic.get("ip", {})
        nic_ip = nic_ip_block.get("address", "") if nic_ip_block else ""
        nic_mac = nic.get("mac", {}).get("address", "")

        if nic_ip and not nic_ip.startswith("127."):
            ip_address = nic_ip
            if nic_mac:
                mac = normalize_mac(nic_mac)
            break
        elif nic_mac and not mac:
            mac = normalize_mac(nic_mac)

    return mac, ip_address


def parse_host_properties(host, cluster_map=None):
    """Extract Connect properties from a single oVirt host dict."""
    props = {}

    props["connect_oraclekvm_host_id"] = host.get("id", "")
    props["connect_oraclekvm_host_name"] = host.get("name", "")
    props["connect_oraclekvm_host_status"] = host.get("status", "unknown")
    props["connect_oraclekvm_host_online"] = host.get("status", "") == "up"
    props["connect_oraclekvm_host_address"] = host.get("address", "")

    cpu = host.get("cpu", {})
    if cpu:
        props["connect_oraclekvm_host_cpu_model"] = cpu.get("name", "")
        topo = cpu.get("topology", {})
        sockets = int(topo.get("sockets", 1))
        cores = int(topo.get("cores", 1))
        threads = int(topo.get("threads", 1))
        props["connect_oraclekvm_host_cpu_cores"] = sockets * cores * threads
    else:
        props["connect_oraclekvm_host_cpu_model"] = ""
        props["connect_oraclekvm_host_cpu_cores"] = 0

    mem_bytes = int(host.get("memory", 0))
    props["connect_oraclekvm_host_memory_mb"] = bytes_to_mb(mem_bytes)

    os_block = host.get("os", {})
    if os_block:
        os_type = os_block.get("type", "")
        os_ver = os_block.get("version", {})
        if os_ver:
            full_ver = os_ver.get("full_version", "")
            if full_ver:
                props["connect_oraclekvm_host_os"] = f"{os_type} {full_ver}"
            else:
                props["connect_oraclekvm_host_os"] = os_type
        else:
            props["connect_oraclekvm_host_os"] = os_type
    else:
        props["connect_oraclekvm_host_os"] = ""

    cluster_ref = host.get("cluster", {})
    cluster_id = cluster_ref.get("id", "") if cluster_ref else ""
    if cluster_map and cluster_id in cluster_map:
        props["connect_oraclekvm_host_cluster"] = cluster_map[cluster_id]
    else:
        props["connect_oraclekvm_host_cluster"] = cluster_id

    spm = host.get("spm", {})
    props["connect_oraclekvm_host_spm_status"] = spm.get("status", "none") if spm else "none"

    # VDSM version
    ver = host.get("version", {})
    if ver:
        major = ver.get("major", "")
        minor = ver.get("minor", "")
        build = ver.get("build", "")
        revision = ver.get("revision", "")
        props["connect_oraclekvm_host_version"] = f"{major}.{minor}.{build}.{revision}"
    else:
        props["connect_oraclekvm_host_version"] = ""

    return props


# ---------------------------------------------------------------------------
# Cluster lookup helper
# ---------------------------------------------------------------------------

def get_cluster_map(base_url, p, verify=True, proxies=None):
    """Return a dict mapping cluster IDs to cluster names."""
    url = f"{base_url.rstrip('/')}/ovirt-engine/api/clusters"
    try:
        data = olvm_request("GET", url, p, verify=verify, proxies=proxies)
        clusters = ensure_list(data.get("cluster"))
        return {c.get("id", ""): c.get("name", "") for c in clusters}
    except Exception:
        return {}


def get_host_map(base_url, p, verify=True, proxies=None):
    """Return a dict mapping host IDs to host names."""
    hosts = get_all_hosts(base_url, p, verify=verify, proxies=proxies)
    return {h.get("id", ""): h.get("name", "") for h in hosts}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def bytes_to_mb(b):
    """Convert bytes to megabytes (integer)."""
    try:
        return int(int(b) / (1024 * 1024))
    except (ValueError, TypeError):
        return 0


def bytes_to_gb(b):
    """Convert bytes to gigabytes (integer)."""
    try:
        return int(int(b) / (1024 * 1024 * 1024))
    except (ValueError, TypeError):
        return 0


def parse_timestamp(ts_str):
    """Parse an ISO-8601 / epoch timestamp to epoch seconds (int).

    Forescout date properties expect epoch in SECONDS.
    oVirt returns creation_time as epoch-ms integer or ISO string.
    """
    if ts_str is None:
        return 0
    try:
        val = int(ts_str)
        # If value looks like epoch ms (> year 2100 in seconds), convert to seconds
        if val > 4102444800:
            return val // 1000
        return val
    except (ValueError, TypeError):
        pass
    # Try ISO-8601 parse
    try:
        from datetime import datetime, timezone
        # oVirt format: 2024-01-15T10:30:00.000+00:00 or similar
        ts_str = str(ts_str).replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts_str)
        return int(dt.timestamp())
    except Exception:
        return 0


def format_uptime_from_start(start_time_str):
    """Given a start_time ISO string, return human-readable uptime."""
    try:
        from datetime import datetime, timezone
        start_str = str(start_time_str).replace("Z", "+00:00")
        start_dt = datetime.fromisoformat(start_str)
        now = datetime.now(timezone.utc)
        delta = now - start_dt
        total_seconds = int(delta.total_seconds())
        if total_seconds < 0:
            return ""
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        return " ".join(parts)
    except Exception:
        return ""
