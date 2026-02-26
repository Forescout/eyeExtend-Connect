"""
Proxmox Connect App - Shared Library
Provides helper functions for Proxmox VE API communication.
Library files cannot access params directly - all values must be passed as arguments.
"""

import requests
import re
import math


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


def get_auth_header(token_id, token_secret):
    """Build the PVEAPIToken authorization header for Proxmox API requests.

    Args:
        token_id: Full token ID in format USER@REALM!TOKENID
        token_secret: The UUID secret for the token

    Returns:
        dict with Authorization header
    """
    return {"Authorization": f"PVEAPIToken={token_id}={token_secret}"}


def proxmox_request(method, base_url, endpoint, token_id, token_secret,
                    verify=True, proxies=None, data=None):
    """Make an authenticated request to the Proxmox API.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        base_url: Proxmox server URL (e.g. https://pve.example.com:8006)
        endpoint: API path (e.g. /api2/json/cluster/resources)
        token_id: Full token ID
        token_secret: Token UUID secret
        verify: SSL verification setting
        proxies: Proxy dict for requests
        data: Form-encoded data dict for POST/PUT requests

    Returns:
        requests.Response object
    """
    url = f"{base_url.rstrip('/')}{endpoint}"
    headers = get_auth_header(token_id, token_secret)
    resp = requests.request(method.upper(), url, headers=headers,
                            verify=verify, proxies=proxies, data=data)
    resp.raise_for_status()
    return resp


def test_connection(base_url, token_id, token_secret, verify=True, proxies=None):
    """Test connectivity to Proxmox by fetching version info.

    Returns:
        dict with version data (version, release, repoid)
    """
    resp = proxmox_request("GET", base_url, "/api2/json/version",
                           token_id, token_secret, verify=verify, proxies=proxies)
    return resp.json().get("data", {})


def get_cluster_resources(base_url, token_id, token_secret, verify=True, proxies=None):
    """Get all VMs and LXC containers cluster-wide.

    Returns:
        list of guest dicts from the Proxmox API
    """
    resp = proxmox_request("GET", base_url, "/api2/json/cluster/resources?type=vm",
                           token_id, token_secret, verify=verify, proxies=proxies)
    return resp.json().get("data", [])


def get_guest_config(base_url, node, guest_type, vmid, token_id, token_secret,
                     verify=True, proxies=None):
    """Get configuration for a specific VM or LXC container.

    Args:
        guest_type: "qemu" or "lxc"

    Returns:
        dict with guest configuration
    """
    endpoint = f"/api2/json/nodes/{node}/{guest_type}/{vmid}/config"
    resp = proxmox_request("GET", base_url, endpoint, token_id, token_secret,
                           verify=verify, proxies=proxies)
    return resp.json().get("data", {})


def get_guest_interfaces(base_url, node, guest_type, vmid, token_id, token_secret,
                         verify=True, proxies=None):
    """Get network interfaces for a guest.

    For qemu VMs, uses the guest agent endpoint (requires agent installed).
    For lxc containers, uses the interfaces endpoint.

    Returns:
        list of interface dicts, or empty list on failure
    """
    if guest_type == "qemu":
        endpoint = f"/api2/json/nodes/{node}/qemu/{vmid}/agent/network-get-interfaces"
    else:
        endpoint = f"/api2/json/nodes/{node}/lxc/{vmid}/interfaces"

    try:
        resp = proxmox_request("GET", base_url, endpoint, token_id, token_secret,
                               verify=verify, proxies=proxies)
        data = resp.json().get("data", {})
        if guest_type == "qemu":
            return data.get("result", []) if isinstance(data, dict) else []
        else:
            return data if isinstance(data, list) else []
    except Exception:
        return []


def get_guest_osinfo(base_url, node, vmid, token_id, token_secret,
                     verify=True, proxies=None):
    """Get detailed OS information from the QEMU guest agent.

    Only works for QEMU VMs with the guest agent installed and running.

    Returns:
        dict with OS info (pretty-name, version-id, etc.), or empty dict on failure
    """
    endpoint = f"/api2/json/nodes/{node}/qemu/{vmid}/agent/get-osinfo"
    try:
        resp = proxmox_request("GET", base_url, endpoint, token_id, token_secret,
                               verify=verify, proxies=proxies)
        data = resp.json().get("data", {})
        return data.get("result", {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


def parse_mac_from_net_config(net_config, guest_type):
    """Extract MAC address from a Proxmox net0 config string.

    For qemu (VMs):
        "virtio=AA:BB:CC:DD:EE:FF,bridge=vmbr0,firewall=1"
        The model type (virtio, e1000, etc.) directly has the MAC as its value.

    For lxc (containers):
        "name=eth0,bridge=vmbr0,hwaddr=AA:BB:CC:DD:EE:FF,ip=dhcp,type=veth"
        The MAC is in the hwaddr= field.

    Args:
        net_config: The net0 config string from Proxmox
        guest_type: "qemu" or "lxc"

    Returns:
        MAC address as 12-char uppercase hex string (Forescout format), or None
    """
    if not net_config:
        return None

    mac = None
    if guest_type == "lxc":
        match = re.search(r'hwaddr=([0-9A-Fa-f:]{17})', net_config)
        if match:
            mac = match.group(1)
    else:
        match = re.search(r'(?:virtio|e1000|rtl8139|vmxnet3)=([0-9A-Fa-f:]{17})', net_config)
        if match:
            mac = match.group(1)

    if mac:
        return mac.replace(":", "").upper()
    return None


def parse_ip_from_interfaces(interfaces, guest_type):
    """Extract the primary IPv4 address from interface data.

    For qemu (via guest agent):
        [{"name": "eth0", "ip-addresses": [{"ip-address": "10.0.0.5", "ip-address-type": "ipv4"}]}]

    For lxc:
        [{"name": "eth0", "inet": "10.0.0.5/24", "hwaddr": "AA:BB:CC:DD:EE:FF"}]

    Returns:
        IPv4 address string or None
    """
    if not interfaces:
        return None

    for iface in interfaces:
        name = iface.get("name", "")
        if name == "lo":
            continue

        if guest_type == "qemu":
            ip_addresses = iface.get("ip-addresses", [])
            for addr in ip_addresses:
                if addr.get("ip-address-type") == "ipv4":
                    ip = addr.get("ip-address", "")
                    if ip and not ip.startswith("127."):
                        return ip
        else:
            inet = iface.get("inet", "")
            if inet:
                ip = inet.split("/")[0]
                if ip and not ip.startswith("127."):
                    return ip

    return None


def parse_ip_from_config(config, guest_type):
    """Extract the configured static IP from a Proxmox guest config.

    For lxc: net0 contains "ip=10.0.0.5/24" or "ip=dhcp"
    For qemu: ipconfig0 contains "ip=10.0.0.5/24,gw=10.0.0.1"

    Returns:
        IPv4 address string or None (returns None for dhcp/dhcp6)
    """
    if not config:
        return None

    if guest_type == "lxc":
        net0 = config.get("net0", "")
        if net0:
            match = re.search(r'ip=(\d+\.\d+\.\d+\.\d+)', net0)
            if match:
                return match.group(1)
    else:
        ipconfig0 = config.get("ipconfig0", "")
        if ipconfig0:
            match = re.search(r'ip=(\d+\.\d+\.\d+\.\d+)', ipconfig0)
            if match:
                return match.group(1)

    return None


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


# --- Node (PVE Host) Helpers ---


def get_cluster_nodes(base_url, token_id, token_secret, verify=True, proxies=None):
    """Get all PVE nodes cluster-wide.

    Returns:
        list of node dicts from the Proxmox API
    """
    resp = proxmox_request("GET", base_url, "/api2/json/cluster/resources?type=node",
                           token_id, token_secret, verify=verify, proxies=proxies)
    return resp.json().get("data", [])


def get_node_status(base_url, node, token_id, token_secret, verify=True, proxies=None):
    """Get detailed status for a specific PVE node.

    Returns:
        dict with cpuinfo, kversion, pveversion, memory, rootfs, etc.
    """
    endpoint = f"/api2/json/nodes/{node}/status"
    resp = proxmox_request("GET", base_url, endpoint, token_id, token_secret,
                           verify=verify, proxies=proxies)
    return resp.json().get("data", {})


def get_node_network(base_url, node, token_id, token_secret, verify=True, proxies=None):
    """Get network interfaces for a PVE node.

    Returns:
        list of network interface dicts
    """
    endpoint = f"/api2/json/nodes/{node}/network"
    resp = proxmox_request("GET", base_url, endpoint, token_id, token_secret,
                           verify=verify, proxies=proxies)
    return resp.json().get("data", [])


def get_node_pending_updates(base_url, node, token_id, token_secret,
                             verify=True, proxies=None):
    """Get list of pending package updates for a PVE node.

    Requires Sys.Modify privilege. Returns empty list on permission error.

    Returns:
        list of package update dicts, or empty list on failure
    """
    endpoint = f"/api2/json/nodes/{node}/apt/update"
    try:
        resp = proxmox_request("GET", base_url, endpoint, token_id, token_secret,
                               verify=verify, proxies=proxies)
        return resp.json().get("data", [])
    except Exception:
        return []


def parse_node_management_interface(network_interfaces):
    """Extract the management interface MAC and IP from node network data.

    Strategy:
    1. Find the bridge or interface with a gateway (management interface)
    2. Get its IP from the address/cidr field
    3. Find the physical port's MAC via bridge_ports, or use the interface's own MAC

    Args:
        network_interfaces: list of interface dicts from get_node_network()

    Returns:
        (mac, ip) tuple — either or both may be None
    """
    if not network_interfaces:
        return None, None

    # Index interfaces by name for quick lookup
    iface_by_name = {}
    for iface in network_interfaces:
        name = iface.get("iface", "")
        if name:
            iface_by_name[name] = iface

    # Find the interface with a gateway (management interface)
    mgmt_iface = None
    for iface in network_interfaces:
        if iface.get("gateway"):
            mgmt_iface = iface
            break

    # Fallback: look for vmbr0
    if not mgmt_iface:
        mgmt_iface = iface_by_name.get("vmbr0")

    if not mgmt_iface:
        return None, None

    # Get IP address
    ip = None
    address = mgmt_iface.get("address", "")
    if address:
        ip = address
    elif mgmt_iface.get("cidr"):
        ip = mgmt_iface["cidr"].split("/")[0]

    # Get MAC - try bridge_ports first to find the physical NIC
    mac = None
    bridge_ports = mgmt_iface.get("bridge_ports", "")
    if bridge_ports:
        # bridge_ports can be a single interface or space-separated list
        port_name = bridge_ports.split()[0]
        port_iface = iface_by_name.get(port_name, {})
        # Physical NICs have their MAC in various fields
        mac_raw = port_iface.get("hwaddr", "") or port_iface.get("address", "")
        if mac_raw and ":" in mac_raw and len(mac_raw) == 17:
            mac = mac_raw.replace(":", "").upper()

    # Fallback: use the management interface's own MAC if available
    if not mac:
        mac_raw = mgmt_iface.get("hwaddr", "")
        if mac_raw and ":" in mac_raw and len(mac_raw) == 17:
            mac = mac_raw.replace(":", "").upper()

    return mac, ip


# --- Action Helpers ---

def change_guest_status(base_url, node, guest_type, vmid, action,
                        token_id, token_secret, verify=True, proxies=None):
    """Change the power state of a VM or container.

    Args:
        action: One of "start", "stop", "shutdown", "reboot", "suspend", "resume"

    Returns:
        UPID task string from Proxmox
    """
    endpoint = f"/api2/json/nodes/{node}/{guest_type}/{vmid}/status/{action}"
    resp = proxmox_request("POST", base_url, endpoint, token_id, token_secret,
                           verify=verify, proxies=proxies)
    return resp.json().get("data", "")


def create_snapshot(base_url, node, guest_type, vmid, snapname,
                    token_id, token_secret, description="",
                    verify=True, proxies=None):
    """Create a snapshot of a VM or container.

    Args:
        snapname: Name for the snapshot (alphanumeric, no spaces)
        description: Optional snapshot description

    Returns:
        UPID task string from Proxmox
    """
    endpoint = f"/api2/json/nodes/{node}/{guest_type}/{vmid}/snapshot"
    data = {"snapname": snapname}
    if description:
        data["description"] = description
    resp = proxmox_request("POST", base_url, endpoint, token_id, token_secret,
                           verify=verify, proxies=proxies, data=data)
    return resp.json().get("data", "")


def set_guest_tags(base_url, node, guest_type, vmid, tags,
                   token_id, token_secret, verify=True, proxies=None):
    """Set tags on a VM or container. Replaces all existing tags.

    Args:
        tags: Semicolon-separated tag string (e.g. "tag1;tag2")
    """
    endpoint = f"/api2/json/nodes/{node}/{guest_type}/{vmid}/config"
    data = {"tags": tags}
    proxmox_request("PUT", base_url, endpoint, token_id, token_secret,
                    verify=verify, proxies=proxies, data=data)


def get_guest_tags(base_url, node, guest_type, vmid,
                   token_id, token_secret, verify=True, proxies=None):
    """Get current tags for a VM or container.

    Returns:
        Tag string (semicolon-separated) or empty string
    """
    config = get_guest_config(base_url, node, guest_type, vmid,
                              token_id, token_secret, verify=verify,
                              proxies=proxies)
    return config.get("tags", "") or ""
