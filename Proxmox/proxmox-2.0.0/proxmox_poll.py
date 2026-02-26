"""
Proxmox Connect App - Poll/Discovery Script
Discovers all VMs and LXC containers from the Proxmox VE cluster.
Returns endpoints identified by MAC address (from config) with IP when available.
MAC and IP are written to Forescout core properties ($mac, $ip).
Stopped guests are marked offline; running guests are marked online.
"""

import requests

# params and response are pre-injected by the Connect framework

# Extract connection settings
base_url = params.get("connect_proxmox_url", "")
token_id = params.get("connect_proxmox_token_id", "")
token_secret = params.get("connect_proxmox_token_secret", "")

# Build proxy settings
proxies = proxmox_lib.get_proxies_from_params(params)

response = {}
endpoints = []

logging.info("Proxmox poll: starting discovery")

try:
    # Step 1: Get all VMs and LXC containers cluster-wide (single API call)
    guests = proxmox_lib.get_cluster_resources(
        base_url=base_url,
        token_id=token_id,
        token_secret=token_secret,
        verify=ssl_verify,
        proxies=proxies
    )

    logging.info(f"Proxmox poll: cluster/resources returned {len(guests)} guests")

    if not guests:
        logging.warning("Proxmox poll: no guests returned from cluster/resources. "
                        "Check API token permissions (need Sys.Audit or VM.Audit).")

    for guest in guests:
        vmid = guest.get("vmid")
        node = guest.get("node", "")
        guest_type = guest.get("type", "")
        name = guest.get("name", "")
        status = guest.get("status", "")
        is_running = status == "running"

        logging.info(f"Proxmox poll: processing {guest_type}/{vmid} ({name}) "
                     f"on node={node} status={status}")

        if not vmid or not node or guest_type not in ("qemu", "lxc"):
            continue

        # Build properties from cluster/resources data
        properties = {
            "connect_proxmox_vmid": vmid,
            "connect_proxmox_name": name,
            "connect_proxmox_node": node,
            "connect_proxmox_status": status,
            "connect_proxmox_type": guest_type,
            "connect_proxmox_cpu_cores": guest.get("maxcpu", 0),
            "connect_proxmox_memory_mb": proxmox_lib.bytes_to_mb(guest.get("maxmem", 0)),
            "connect_proxmox_disk_gb": proxmox_lib.bytes_to_gb(guest.get("maxdisk", 0)),
            "connect_proxmox_uptime": guest.get("uptime", 0),
            "connect_proxmox_tags": guest.get("tags", "") or "",
            "connect_proxmox_template": guest.get("template", 0) == 1
        }

        # Step 2: Get config for MAC address, ostype, description, and static IP
        mac = None
        config = None
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

            # Extract MAC from net0 config
            net0 = config.get("net0", "")
            logging.info(f"Proxmox poll: {guest_type}/{vmid} net0={net0}")
            mac = proxmox_lib.parse_mac_from_net_config(net0, guest_type)

            # Extract ostype and description
            properties["connect_proxmox_os_type"] = config.get("ostype", "") or ""
            properties["connect_proxmox_description"] = config.get("description", "") or ""

        except Exception as config_err:
            logging.warning(
                f"Proxmox poll: could not get config for {guest_type}/{vmid}: "
                f"{str(config_err)}"
            )
            properties["connect_proxmox_os_type"] = ""
            properties["connect_proxmox_description"] = ""

        # Step 3: Get IP address
        ip_address = None
        if is_running:
            # For running guests, try live interfaces first
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
            ip_address = proxmox_lib.parse_ip_from_interfaces(interfaces, guest_type)

        # Fallback: get configured static IP from config (works for stopped guests too)
        if not ip_address and config:
            ip_address = proxmox_lib.parse_ip_from_config(config, guest_type)
            if ip_address:
                logging.info(f"Proxmox poll: {guest_type}/{vmid} using static IP "
                             f"from config: {ip_address}")

        # Step 4: Get detailed OS from QEMU guest agent (running QEMU VMs only)
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

        # Set Forescout core $online property based on Proxmox status
        properties["online"] = is_running

        # Step 5: Build endpoint with identifier
        endpoint = {"properties": properties}

        if mac:
            endpoint["mac"] = mac
        if ip_address:
            endpoint["ip"] = ip_address

        if "mac" not in endpoint and "ip" not in endpoint:
            logging.warning(
                f"Proxmox poll: skipping {guest_type}/{vmid} ({name}) - "
                f"no MAC or IP available"
            )
            continue

        logging.info(f"Proxmox poll: adding endpoint {guest_type}/{vmid} ({name}) "
                     f"mac={mac} ip={ip_address} online={is_running}")
        endpoints.append(endpoint)

    # --- Node (PVE Host) Discovery ---
    logging.info("Proxmox poll: starting PVE host node discovery")

    try:
        nodes = proxmox_lib.get_cluster_nodes(
            base_url=base_url,
            token_id=token_id,
            token_secret=token_secret,
            verify=ssl_verify,
            proxies=proxies
        )

        logging.info(f"Proxmox poll: cluster/resources returned {len(nodes)} nodes")

        for node_info in nodes:
            node_name = node_info.get("node", "")
            node_status = node_info.get("status", "unknown")

            if not node_name:
                continue

            logging.info(f"Proxmox poll: processing PVE node {node_name} "
                         f"status={node_status}")

            node_props = {
                "connect_proxmox_pve_hostname": node_name,
                "connect_proxmox_pve_status": node_status,
                "connect_proxmox_pve_memory_gb": proxmox_lib.bytes_to_gb(
                    node_info.get("maxmem", 0)),
                "connect_proxmox_pve_disk_gb": proxmox_lib.bytes_to_gb(
                    node_info.get("maxdisk", 0)),
                "connect_proxmox_pve_uptime": node_info.get("uptime", 0),
                "online": node_status == "online"
            }

            # Get detailed node status (CPU model, kernel, PVE version)
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
                node_props["connect_proxmox_pve_cpu_model"] = cpuinfo.get(
                    "model", "")
                node_props["connect_proxmox_pve_cpu_cores"] = cores * sockets
                node_props["connect_proxmox_pve_cpu_sockets"] = sockets
                node_props["connect_proxmox_pve_kernel"] = status_data.get(
                    "kversion", "")
                node_props["connect_proxmox_pve_version"] = status_data.get(
                    "pveversion", "")
            except Exception as status_err:
                logging.warning(
                    f"Proxmox poll: could not get status for node {node_name}: "
                    f"{str(status_err)}")

            # Get pending updates (graceful — may need Sys.Modify privilege)
            updates = proxmox_lib.get_node_pending_updates(
                base_url=base_url,
                node=node_name,
                token_id=token_id,
                token_secret=token_secret,
                verify=ssl_verify,
                proxies=proxies
            )
            node_props["connect_proxmox_pve_updates_available"] = len(updates) > 0

            # Get network interfaces for MAC and IP identification
            node_mac = None
            node_ip = None
            try:
                net_ifaces = proxmox_lib.get_node_network(
                    base_url=base_url,
                    node=node_name,
                    token_id=token_id,
                    token_secret=token_secret,
                    verify=ssl_verify,
                    proxies=proxies
                )
                node_mac, node_ip = proxmox_lib.parse_node_management_interface(
                    net_ifaces)
            except Exception as net_err:
                logging.warning(
                    f"Proxmox poll: could not get network for node {node_name}: "
                    f"{str(net_err)}")

            # Build node endpoint
            node_endpoint = {"properties": node_props}

            if node_mac:
                node_endpoint["mac"] = node_mac
            if node_ip:
                node_endpoint["ip"] = node_ip

            if "mac" not in node_endpoint and "ip" not in node_endpoint:
                logging.warning(
                    f"Proxmox poll: skipping PVE node {node_name} - "
                    f"no MAC or IP available")
                continue

            logging.info(
                f"Proxmox poll: adding PVE node {node_name} "
                f"mac={node_mac} ip={node_ip}")
            endpoints.append(node_endpoint)

    except Exception as node_err:
        logging.warning(
            f"Proxmox poll: PVE host discovery failed: {str(node_err)}. "
            f"Guest discovery was not affected.")

    logging.info(f"Proxmox poll: returning {len(endpoints)} endpoints")
    response["endpoints"] = endpoints

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["error"] = f"Proxmox API HTTP Error {status_code}"
    logging.error(f"Proxmox poll failed with HTTP {status_code}")
except requests.exceptions.ConnectionError as e:
    response["error"] = f"Could not connect to Proxmox API: {str(e)}"
    logging.error(f"Proxmox poll connection error: {str(e)}")
except requests.exceptions.RequestException as e:
    response["error"] = f"Proxmox API request error: {str(e)}"
    logging.error(f"Proxmox poll request error: {str(e)}")
except Exception as e:
    logging.exception(e)
    response["error"] = f"Unexpected error during Proxmox poll: {str(e)}"
