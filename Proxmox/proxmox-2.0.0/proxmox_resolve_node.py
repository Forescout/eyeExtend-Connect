"""
Proxmox Connect App - Node Resolve Script
Resolves PVE host properties for a specific endpoint by matching MAC or IP
against Proxmox cluster nodes.
"""

import requests

# params and response are pre-injected by the Connect framework

# Extract connection settings
base_url = params.get("connect_proxmox_url", "")
token_id = params.get("connect_proxmox_token_id", "")
token_secret = params.get("connect_proxmox_token_secret", "")

# Host identifiers from Forescout
host_mac = params.get("mac", "")
host_ip = params.get("ip", "")

# Build proxy settings
proxies = proxmox_lib.get_proxies_from_params(params)

response = {}
properties = {}

try:
    # Get all nodes
    nodes = proxmox_lib.get_cluster_nodes(
        base_url=base_url,
        token_id=token_id,
        token_secret=token_secret,
        verify=ssl_verify,
        proxies=proxies
    )

    matched_node = None

    for node_info in nodes:
        node_name = node_info.get("node", "")
        if not node_name:
            continue

        # Get network interfaces to match by MAC/IP
        try:
            net_ifaces = proxmox_lib.get_node_network(
                base_url=base_url,
                node=node_name,
                token_id=token_id,
                token_secret=token_secret,
                verify=ssl_verify,
                proxies=proxies
            )
        except Exception:
            continue

        node_mac, node_ip = proxmox_lib.parse_node_management_interface(net_ifaces)

        matched = False
        if host_mac and node_mac and host_mac.upper() == node_mac.upper():
            matched = True
        elif host_ip and node_ip and host_ip == node_ip:
            matched = True

        if matched:
            matched_node = node_info
            node_status = node_info.get("status", "unknown")

            properties["connect_proxmox_pve_hostname"] = node_name
            properties["connect_proxmox_pve_status"] = node_status
            properties["connect_proxmox_pve_memory_gb"] = proxmox_lib.bytes_to_gb(
                node_info.get("maxmem", 0))
            properties["connect_proxmox_pve_disk_gb"] = proxmox_lib.bytes_to_gb(
                node_info.get("maxdisk", 0))
            properties["connect_proxmox_pve_uptime"] = node_info.get("uptime", 0)

            # Get detailed node status
            try:
                status_data = proxmox_lib.get_node_status(
                    base_url=base_url,
                    node=node_name,
                    token_id=token_id,
                    token_secret=token_secret,
                    verify=ssl_verify,
                    proxies=proxies
                )
                cpuinfo = status_data.get("cpuinfo", {})
                cores = cpuinfo.get("cores", 0)
                sockets = cpuinfo.get("sockets", 1)
                properties["connect_proxmox_pve_cpu_model"] = cpuinfo.get(
                    "model", "")
                properties["connect_proxmox_pve_cpu_cores"] = cores * sockets
                properties["connect_proxmox_pve_cpu_sockets"] = sockets
                properties["connect_proxmox_pve_kernel"] = status_data.get(
                    "kversion", "")
                properties["connect_proxmox_pve_version"] = status_data.get(
                    "pveversion", "")
            except Exception as status_err:
                logging.warning(
                    f"Proxmox resolve_node: could not get status for "
                    f"{node_name}: {str(status_err)}")

            # Get pending updates
            updates = proxmox_lib.get_node_pending_updates(
                base_url=base_url,
                node=node_name,
                token_id=token_id,
                token_secret=token_secret,
                verify=ssl_verify,
                proxies=proxies
            )
            properties["connect_proxmox_pve_updates_available"] = len(updates) > 0

            break

    if properties:
        response["properties"] = properties
    else:
        response["error"] = (
            f"No Proxmox PVE node found matching MAC={host_mac} or IP={host_ip}"
        )

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["error"] = f"Proxmox API HTTP Error {status_code}"
except requests.exceptions.ConnectionError as e:
    response["error"] = f"Could not connect to Proxmox API: {str(e)}"
except requests.exceptions.RequestException as e:
    response["error"] = f"Proxmox API request error: {str(e)}"
except Exception as e:
    logging.exception(e)
    response["error"] = f"Unexpected error during Proxmox node resolve: {str(e)}"
