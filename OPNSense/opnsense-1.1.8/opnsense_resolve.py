"""
OPNSense Connect App - Resolve Script
Enriches the OPNSense firewall endpoint with system telemetry data.
Called per-host when Forescout needs to refresh properties.
Only resolves properties for hosts that match the firewall management interface.

Multi-instance: Uses framework controller routing to connect to the correct firewall.
"""

import requests

# params and response are pre-injected by the Connect framework

# Extract connection settings via controller routing
ctrl = opnsense_lib.get_routed_controller(params)
base_url = ctrl["url"]
api_key = ctrl["api_key"]
api_secret = ctrl["api_secret"]
lan_interface_hint = ctrl["lan_interface"]

# Host identifiers from Forescout
host_mac = params.get("mac", "")
host_ip = params.get("ip", "")

# Build proxy settings
proxies = opnsense_lib.get_proxies_from_params(params)

response = {}
properties = {}

try:
    # Step 1: Verify this host is the firewall itself
    interfaces_info = opnsense_lib.get_interfaces_info(
        base_url=base_url,
        api_key=api_key,
        api_secret=api_secret,
        verify=ssl_verify,
        proxies=proxies
    )
    fw_mac, fw_ip = opnsense_lib.parse_management_interface(
        interfaces_info, lan_interface_hint=lan_interface_hint
    )

    is_firewall = False
    if host_mac and fw_mac and host_mac.upper() == fw_mac.upper():
        is_firewall = True
    elif host_ip and fw_ip and host_ip == fw_ip:
        is_firewall = True

    if not is_firewall:
        # Not the firewall itself - nothing to resolve for ARP-discovered endpoints
        # (ARP properties are set during polling, not resolve)
        response["error"] = (
            f"Host MAC={host_mac} IP={host_ip} is not the OPNSense firewall "
            f"(firewall is MAC={fw_mac} IP={fw_ip})"
        )
    else:
        # Step 2: Gather system telemetry

        # Tag this endpoint with its source firewall
        properties["connect_opnsense_fw_url"] = base_url

        # Hostname
        try:
            sys_info = opnsense_lib.get_system_information(
                base_url=base_url, api_key=api_key, api_secret=api_secret,
                verify=ssl_verify, proxies=proxies
            )
            properties["connect_opnsense_fw_hostname"] = (
                sys_info.get("name", "") or sys_info.get("hostname", "") or ""
            )
        except Exception as e:
            logging.warning(f"OPNSense resolve: system_information failed: {str(e)}")
            properties["connect_opnsense_fw_hostname"] = ""

        # Firmware version
        try:
            firmware = opnsense_lib.get_firmware_info(
                base_url=base_url, api_key=api_key, api_secret=api_secret,
                verify=ssl_verify, proxies=proxies
            )
            properties["connect_opnsense_fw_firmware_version"] = (
                firmware.get("product_version", "") or ""
            )
        except Exception as e:
            logging.warning(f"OPNSense resolve: firmware_info failed: {str(e)}")
            properties["connect_opnsense_fw_firmware_version"] = ""

        # CPU type
        try:
            cpu_info = opnsense_lib.get_cpu_type(
                base_url=base_url, api_key=api_key, api_secret=api_secret,
                verify=ssl_verify, proxies=proxies
            )
            # Response may be a string or dict
            if isinstance(cpu_info, list) and cpu_info:
                properties["connect_opnsense_fw_cpu_type"] = str(cpu_info[0])
            elif isinstance(cpu_info, str):
                properties["connect_opnsense_fw_cpu_type"] = cpu_info
            elif isinstance(cpu_info, dict):
                properties["connect_opnsense_fw_cpu_type"] = (
                    cpu_info.get("cpu_type", "") or
                    cpu_info.get("model", "") or
                    str(cpu_info)
                )
            else:
                properties["connect_opnsense_fw_cpu_type"] = str(cpu_info)
        except Exception as e:
            logging.warning(f"OPNSense resolve: cpu_type failed: {str(e)}")
            properties["connect_opnsense_fw_cpu_type"] = ""

        # Memory (from system_resources endpoint)
        try:
            resources = opnsense_lib.get_system_resources(
                base_url=base_url, api_key=api_key, api_secret=api_secret,
                verify=ssl_verify, proxies=proxies
            )
            mem_data = resources.get("memory", {})
            if isinstance(mem_data, dict):
                total_bytes = opnsense_lib.safe_int(mem_data.get("total", 0))
                used_bytes = opnsense_lib.safe_int(mem_data.get("used", 0))
                properties["connect_opnsense_fw_memory_total_mb"] = opnsense_lib.bytes_to_mb(
                    total_bytes
                )
                if total_bytes > 0:
                    properties["connect_opnsense_fw_memory_used_pct"] = int(
                        (used_bytes / total_bytes) * 100
                    )
                else:
                    properties["connect_opnsense_fw_memory_used_pct"] = 0
            else:
                properties["connect_opnsense_fw_memory_total_mb"] = 0
                properties["connect_opnsense_fw_memory_used_pct"] = 0
        except Exception as e:
            logging.warning(f"OPNSense resolve: system_resources failed: {str(e)}")
            properties["connect_opnsense_fw_memory_total_mb"] = 0
            properties["connect_opnsense_fw_memory_used_pct"] = 0

        # Disk usage
        try:
            disk = opnsense_lib.get_system_disk(
                base_url=base_url, api_key=api_key, api_secret=api_secret,
                verify=ssl_verify, proxies=proxies
            )
            devices = disk if isinstance(disk, list) else disk.get("devices", [])
            if isinstance(devices, list):
                for dev in devices:
                    if isinstance(dev, dict):
                        mountpoint = dev.get("mountpoint", "")
                        if mountpoint == "/":
                            size_str = (dev.get("blocks", "0") or
                                        dev.get("size", "0"))
                            used_pct = dev.get("used_pct", 0)
                            if isinstance(used_pct, (int, float)):
                                properties["connect_opnsense_fw_disk_used_pct"] = int(
                                    used_pct
                                )
                            else:
                                properties["connect_opnsense_fw_disk_used_pct"] = (
                                    opnsense_lib.parse_pct(str(used_pct))
                                )
                            properties["connect_opnsense_fw_disk_total_gb"] = (
                                opnsense_lib.parse_size_gb(size_str)
                            )
                            break
                else:
                    properties["connect_opnsense_fw_disk_total_gb"] = 0
                    properties["connect_opnsense_fw_disk_used_pct"] = 0
            else:
                properties["connect_opnsense_fw_disk_total_gb"] = 0
                properties["connect_opnsense_fw_disk_used_pct"] = 0
        except Exception as e:
            logging.warning(f"OPNSense resolve: disk failed: {str(e)}")
            properties["connect_opnsense_fw_disk_total_gb"] = 0
            properties["connect_opnsense_fw_disk_used_pct"] = 0

        # Temperature
        try:
            temp_data = opnsense_lib.get_system_temperature(
                base_url=base_url, api_key=api_key, api_secret=api_secret,
                verify=ssl_verify, proxies=proxies
            )
            if isinstance(temp_data, list) and temp_data:
                # Format as "sensor: temp" pairs
                temps = []
                for sensor in temp_data:
                    if isinstance(sensor, dict):
                        name = sensor.get("device", "") or sensor.get("type", "")
                        temp_val = sensor.get("temperature", "")
                        if name and temp_val:
                            temps.append(f"{name}: {temp_val}")
                properties["connect_opnsense_fw_temperature"] = "; ".join(temps) if temps else ""
            elif isinstance(temp_data, dict):
                temps = []
                for key, val in temp_data.items():
                    if isinstance(val, (int, float, str)):
                        temps.append(f"{key}: {val}")
                properties["connect_opnsense_fw_temperature"] = "; ".join(temps) if temps else ""
            else:
                properties["connect_opnsense_fw_temperature"] = ""
        except Exception as e:
            logging.warning(f"OPNSense resolve: temperature failed: {str(e)}")
            properties["connect_opnsense_fw_temperature"] = ""

        # Uptime
        try:
            time_data = opnsense_lib.get_system_time(
                base_url=base_url, api_key=api_key, api_secret=api_secret,
                verify=ssl_verify, proxies=proxies
            )
            properties["connect_opnsense_fw_uptime"] = (
                time_data.get("uptime", "") or ""
            )
        except Exception as e:
            logging.warning(f"OPNSense resolve: system_time failed: {str(e)}")
            properties["connect_opnsense_fw_uptime"] = ""

        # PF state count
        try:
            pf_data = opnsense_lib.get_pf_states(
                base_url=base_url, api_key=api_key, api_secret=api_secret,
                verify=ssl_verify, proxies=proxies
            )
            properties["connect_opnsense_fw_pf_states"] = opnsense_lib.safe_int(
                pf_data.get("current", 0)
            )
        except Exception as e:
            logging.warning(f"OPNSense resolve: pf_states failed: {str(e)}")
            properties["connect_opnsense_fw_pf_states"] = 0

        # Interface list with IP addresses
        try:
            iface_list = []
            # interfaces_info was already fetched above for firewall identification
            if interfaces_info:
                items = []
                if isinstance(interfaces_info, dict):
                    items = list(interfaces_info.values())
                elif isinstance(interfaces_info, list):
                    items = interfaces_info
                for iface in items:
                    if not isinstance(iface, dict):
                        continue
                    name = (iface.get("description", "") or
                            iface.get("identifier", "") or
                            iface.get("device", ""))
                    device = iface.get("device", "")
                    status = "up" if iface.get("status", "") == "up" else "down"
                    # Extract IPv4 address
                    ipv4_addr = ""
                    ipv4_list = iface.get("ipv4", [])
                    if isinstance(ipv4_list, list) and ipv4_list:
                        first = ipv4_list[0]
                        if isinstance(first, dict):
                            ipv4_addr = first.get("ipaddr", "")
                    if not ipv4_addr:
                        addr4 = iface.get("addr4", "")
                        if addr4:
                            ipv4_addr = addr4.split("/")[0]
                    # Extract IPv6 address
                    ipv6_addr = ""
                    ipv6_list = iface.get("ipv6", [])
                    if isinstance(ipv6_list, list) and ipv6_list:
                        first = ipv6_list[0]
                        if isinstance(first, dict):
                            ipv6_addr = first.get("ipaddr", "")
                    if not ipv6_addr:
                        addr6 = iface.get("addr6", "")
                        if addr6:
                            ipv6_addr = addr6.split("/")[0]
                    iface_list.append({
                        "name": name,
                        "device": device,
                        "status": status,
                        "ipv4": ipv4_addr,
                        "ipv6": ipv6_addr
                    })
            properties["connect_opnsense_fw_interfaces"] = iface_list
        except Exception as e:
            logging.warning(f"OPNSense resolve: interface list failed: {str(e)}")
            properties["connect_opnsense_fw_interfaces"] = []

        response["properties"] = properties

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["error"] = f"OPNSense API HTTP Error {status_code}"
except requests.exceptions.ConnectionError as e:
    response["error"] = f"Could not connect to OPNSense API: {str(e)}"
except requests.exceptions.RequestException as e:
    response["error"] = f"OPNSense API request error: {str(e)}"
except Exception as e:
    logging.exception(e)
    response["error"] = f"Unexpected error during OPNSense resolve: {str(e)}"
