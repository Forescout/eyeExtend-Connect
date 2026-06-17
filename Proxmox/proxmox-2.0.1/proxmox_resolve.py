"""
Proxmox Connect App - Resolve Script
Resolves properties for a specific host by matching MAC or IP against Proxmox guests.
Called per-host when Forescout needs to refresh properties.
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
    # Get all guests
    guests = proxmox_lib.get_cluster_resources(
        base_url=base_url,
        token_id=token_id,
        token_secret=token_secret,
        verify=ssl_verify,
        proxies=proxies
    )

    matched = False

    for guest in guests:
        vmid = guest.get("vmid")
        node = guest.get("node", "")
        guest_type = guest.get("type", "")
        status = guest.get("status", "")
        is_running = status == "running"

        if not vmid or not node or guest_type not in ("qemu", "lxc"):
            continue

        # Get config to check MAC and static IP
        try:
            config = proxmox_lib.get_guest_config(
                base_url=base_url,
                node=node,
                guest_type=guest_type,
                vmid=vmid,
                token_id=token_id,
                token_secret=token_secret,
                verify=ssl_verify,
                proxies=proxies
            )
        except Exception:
            continue

        # Try to match by any configured MAC
        guest_macs = proxmox_lib.parse_macs_from_config(config, guest_type)
        host_mac_norm = host_mac.upper() if host_mac else ""

        if host_mac_norm and host_mac_norm in guest_macs:
            matched = True
        else:
            # Try to match by any IP (live interfaces for running, config for stopped)
            if host_ip:
                guest_ips = []
                if is_running:
                    try:
                        interfaces = proxmox_lib.get_guest_interfaces(
                            base_url=base_url,
                            node=node,
                            guest_type=guest_type,
                            vmid=vmid,
                            token_id=token_id,
                            token_secret=token_secret,
                            verify=ssl_verify,
                            proxies=proxies
                        )
                        guest_ips = proxmox_lib.parse_ips_from_interfaces(
                            interfaces, guest_type
                        )
                    except Exception:
                        pass

                # Add configured static IPs
                for config_ip in proxmox_lib.parse_ips_from_config(config, guest_type):
                    if config_ip not in guest_ips:
                        guest_ips.append(config_ip)

                if host_ip in guest_ips:
                    matched = True

        if matched:
            # Build properties
            properties["connect_proxmox_vmid"] = vmid
            properties["connect_proxmox_name"] = guest.get("name", "")
            properties["connect_proxmox_node"] = node
            properties["connect_proxmox_status"] = status
            properties["connect_proxmox_type"] = guest_type
            properties["connect_proxmox_os_type"] = config.get("ostype", "") or ""
            properties["connect_proxmox_cpu_cores"] = guest.get("maxcpu", 0)
            properties["connect_proxmox_memory_mb"] = proxmox_lib.bytes_to_mb(
                guest.get("maxmem", 0)
            )
            properties["connect_proxmox_disk_gb"] = proxmox_lib.bytes_to_gb(
                guest.get("maxdisk", 0)
            )
            properties["connect_proxmox_uptime"] = guest.get("uptime", 0)
            properties["connect_proxmox_tags"] = guest.get("tags", "") or ""
            properties["connect_proxmox_template"] = guest.get("template", 0) == 1
            properties["connect_proxmox_description"] = config.get("description", "") or ""

            # Get detailed OS from QEMU guest agent (running QEMU VMs only)
            guest_os = ""
            has_guest_agent = False
            if guest_type == "qemu" and is_running:
                osinfo = proxmox_lib.get_guest_osinfo(
                    base_url=base_url,
                    node=node,
                    vmid=vmid,
                    token_id=token_id,
                    token_secret=token_secret,
                    verify=ssl_verify,
                    proxies=proxies
                )
                if osinfo:
                    has_guest_agent = True
                    guest_os = osinfo.get("pretty-name", "") or ""
            properties["connect_proxmox_guest_os"] = guest_os
            properties["connect_proxmox_guest_agent"] = has_guest_agent

            break

    if properties:
        response["properties"] = properties
    else:
        response["error"] = (
            f"No Proxmox guest found matching MAC={host_mac} or IP={host_ip}"
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
    response["error"] = f"Unexpected error during Proxmox resolve: {str(e)}"
