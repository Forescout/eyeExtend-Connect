"""
OPNSense Connect App - Poll/Discovery Script
Two-phase discovery per controller:
  Phase A: Discovers the OPNSense firewall itself as an endpoint (management interface MAC/IP).
  Phase B: Reads the ARP table to discover all endpoints seen by the firewall.
MAC and IP are written to Forescout core properties ($mac, $ip).
ARP-sourced endpoints get hostname properties when available.

Multi-instance: Iterates over all comma-separated controllers and combines
endpoints into a single list. Each endpoint is tagged with its source firewall URL.
"""

import requests

# params and response are pre-injected by the Connect framework

# Parse all configured controllers (supports comma-separated multi-instance)
controllers = opnsense_lib.get_all_controllers(params)

# Build proxy settings
proxies = opnsense_lib.get_proxies_from_params(params)

response = {}
endpoints = []

logging.info(f"OPNSense poll: starting discovery for {len(controllers)} controller(s)")

for ctrl in controllers:
    base_url = ctrl["url"]
    api_key = ctrl["api_key"]
    api_secret = ctrl["api_secret"]
    lan_interface_hint = ctrl["lan_interface"]

    logging.info(f"OPNSense poll: processing controller {base_url}")

    try:
        # ========================================================
        # Phase A: Discover the firewall itself as an endpoint
        # ========================================================
        logging.info(f"OPNSense poll: ({base_url}) Phase A - firewall endpoint discovery")

        fw_mac = None
        fw_ip = None

        try:
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
            logging.info(f"OPNSense poll: ({base_url}) firewall management interface "
                         f"mac={fw_mac} ip={fw_ip}")
        except Exception as iface_err:
            logging.warning(
                f"OPNSense poll: ({base_url}) could not get interface info: {str(iface_err)}"
            )

        # Get hostname for the firewall
        fw_hostname = ""
        try:
            sys_info = opnsense_lib.get_system_information(
                base_url=base_url,
                api_key=api_key,
                api_secret=api_secret,
                verify=ssl_verify,
                proxies=proxies
            )
            fw_hostname = sys_info.get("name", "") or sys_info.get("hostname", "") or ""
        except Exception as sysinfo_err:
            logging.warning(
                f"OPNSense poll: ({base_url}) could not get system information: "
                f"{str(sysinfo_err)}"
            )

        if fw_mac or fw_ip:
            fw_props = {
                "connect_opnsense_fw_hostname": fw_hostname,
                "connect_opnsense_fw_url": base_url,
                "connect_opnsense_controller_ip": base_url,
                "online": True
            }

            # -- Firmware version --
            try:
                firmware = opnsense_lib.get_firmware_info(
                    base_url=base_url, api_key=api_key, api_secret=api_secret,
                    verify=ssl_verify, proxies=proxies
                )
                fw_props["connect_opnsense_fw_firmware_version"] = (
                    firmware.get("product_version", "") or ""
                )
            except Exception as e:
                logging.warning(f"OPNSense poll: ({base_url}) firmware_info failed: {str(e)}")

            # -- CPU type --
            try:
                cpu_info = opnsense_lib.get_cpu_type(
                    base_url=base_url, api_key=api_key, api_secret=api_secret,
                    verify=ssl_verify, proxies=proxies
                )
                if isinstance(cpu_info, list) and cpu_info:
                    fw_props["connect_opnsense_fw_cpu_type"] = str(cpu_info[0])
                elif isinstance(cpu_info, str):
                    fw_props["connect_opnsense_fw_cpu_type"] = cpu_info
                elif isinstance(cpu_info, dict):
                    fw_props["connect_opnsense_fw_cpu_type"] = (
                        cpu_info.get("cpu_type", "") or
                        cpu_info.get("model", "") or
                        str(cpu_info)
                    )
                else:
                    fw_props["connect_opnsense_fw_cpu_type"] = str(cpu_info)
            except Exception as e:
                logging.warning(f"OPNSense poll: ({base_url}) cpu_type failed: {str(e)}")

            # -- Memory (from system_resources endpoint) --
            try:
                resources = opnsense_lib.get_system_resources(
                    base_url=base_url, api_key=api_key, api_secret=api_secret,
                    verify=ssl_verify, proxies=proxies
                )
                mem_data = resources.get("memory", {})
                if isinstance(mem_data, dict):
                    total_bytes = opnsense_lib.safe_int(mem_data.get("total", 0))
                    used_bytes = opnsense_lib.safe_int(mem_data.get("used", 0))
                    fw_props["connect_opnsense_fw_memory_total_mb"] = opnsense_lib.bytes_to_mb(
                        total_bytes
                    )
                    if total_bytes > 0:
                        fw_props["connect_opnsense_fw_memory_used_pct"] = int(
                            (used_bytes / total_bytes) * 100
                        )
                    else:
                        fw_props["connect_opnsense_fw_memory_used_pct"] = 0
                else:
                    fw_props["connect_opnsense_fw_memory_total_mb"] = 0
                    fw_props["connect_opnsense_fw_memory_used_pct"] = 0
            except Exception as e:
                logging.warning(f"OPNSense poll: ({base_url}) system_resources failed: {str(e)}")

            # -- Disk usage --
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
                                    fw_props["connect_opnsense_fw_disk_used_pct"] = int(
                                        used_pct
                                    )
                                else:
                                    fw_props["connect_opnsense_fw_disk_used_pct"] = (
                                        opnsense_lib.parse_pct(str(used_pct))
                                    )
                                fw_props["connect_opnsense_fw_disk_total_gb"] = (
                                    opnsense_lib.parse_size_gb(size_str)
                                )
                                break
            except Exception as e:
                logging.warning(f"OPNSense poll: ({base_url}) disk failed: {str(e)}")

            # -- Temperature --
            try:
                temp_data = opnsense_lib.get_system_temperature(
                    base_url=base_url, api_key=api_key, api_secret=api_secret,
                    verify=ssl_verify, proxies=proxies
                )
                if isinstance(temp_data, list) and temp_data:
                    temps = []
                    for sensor in temp_data:
                        if isinstance(sensor, dict):
                            name = sensor.get("device", "") or sensor.get("type", "")
                            temp_val = sensor.get("temperature", "")
                            if name and temp_val:
                                temps.append(f"{name}: {temp_val}")
                    fw_props["connect_opnsense_fw_temperature"] = (
                        "; ".join(temps) if temps else ""
                    )
                elif isinstance(temp_data, dict):
                    temps = []
                    for key, val in temp_data.items():
                        if isinstance(val, (int, float, str)):
                            temps.append(f"{key}: {val}")
                    fw_props["connect_opnsense_fw_temperature"] = (
                        "; ".join(temps) if temps else ""
                    )
                else:
                    fw_props["connect_opnsense_fw_temperature"] = ""
            except Exception as e:
                logging.warning(f"OPNSense poll: ({base_url}) temperature failed: {str(e)}")

            # -- Uptime --
            try:
                time_data = opnsense_lib.get_system_time(
                    base_url=base_url, api_key=api_key, api_secret=api_secret,
                    verify=ssl_verify, proxies=proxies
                )
                fw_props["connect_opnsense_fw_uptime"] = (
                    time_data.get("uptime", "") or ""
                )
            except Exception as e:
                logging.warning(f"OPNSense poll: ({base_url}) system_time failed: {str(e)}")

            # -- PF state count --
            try:
                pf_data = opnsense_lib.get_pf_states(
                    base_url=base_url, api_key=api_key, api_secret=api_secret,
                    verify=ssl_verify, proxies=proxies
                )
                fw_props["connect_opnsense_fw_pf_states"] = opnsense_lib.safe_int(
                    pf_data.get("current", 0)
                )
            except Exception as e:
                logging.warning(f"OPNSense poll: ({base_url}) pf_states failed: {str(e)}")

            # -- Interface list with IP addresses --
            try:
                iface_list = []
                # interfaces_info was already fetched in Phase A for MAC/IP
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
                fw_props["connect_opnsense_fw_interfaces"] = iface_list
            except Exception as e:
                logging.warning(
                    f"OPNSense poll: ({base_url}) interface list failed: {str(e)}"
                )

            fw_endpoint = {"properties": fw_props}
            if fw_mac:
                fw_endpoint["mac"] = fw_mac
            if fw_ip:
                fw_endpoint["ip"] = fw_ip

            endpoints.append(fw_endpoint)
            logging.info(f"OPNSense poll: ({base_url}) added firewall endpoint "
                         f"hostname={fw_hostname} mac={fw_mac} ip={fw_ip} "
                         f"with {len(fw_props)} properties")
        else:
            logging.warning(f"OPNSense poll: ({base_url}) could not identify "
                            f"firewall management interface")

        # ========================================================
        # Phase B: ARP table discovery
        # ========================================================
        logging.info(f"OPNSense poll: ({base_url}) Phase B - ARP table discovery")

        arp_entries = opnsense_lib.get_arp_table(
            base_url=base_url,
            api_key=api_key,
            api_secret=api_secret,
            verify=ssl_verify,
            proxies=proxies
        )

        logging.info(f"OPNSense poll: ({base_url}) ARP table returned "
                     f"{len(arp_entries)} entries")

        arp_count = 0
        for entry in arp_entries:
            if not isinstance(entry, dict):
                continue

            # Skip expired entries
            expired = entry.get("expired", False)
            if expired and str(expired).lower() in ("true", "1", "yes"):
                continue

            arp_ip = entry.get("ip", "")
            arp_mac_raw = entry.get("mac", "")
            arp_mac = opnsense_lib.normalize_mac(arp_mac_raw)

            # Must have at least a MAC or IP
            if not arp_mac and not arp_ip:
                continue

            # Skip if this is the firewall itself
            if fw_mac and arp_mac and arp_mac == fw_mac:
                continue
            if fw_ip and arp_ip and arp_ip == fw_ip:
                continue

            # Build client endpoint properties
            arp_props = {
                "connect_opnsense_client_seen_by": fw_hostname,
                "connect_opnsense_controller_ip": base_url,
                "online": True
            }

            hostname = entry.get("hostname", "")
            if hostname:
                arp_props["connect_opnsense_client_hostname"] = hostname

            endpoint = {"properties": arp_props}

            if arp_mac:
                endpoint["mac"] = arp_mac
            if arp_ip:
                endpoint["ip"] = arp_ip

            endpoints.append(endpoint)
            arp_count += 1

        logging.info(f"OPNSense poll: ({base_url}) discovered {arp_count} ARP endpoints")

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else "unknown"
        logging.error(f"OPNSense poll: ({base_url}) HTTP {status_code}")
    except requests.exceptions.ConnectionError as e:
        logging.error(f"OPNSense poll: ({base_url}) connection error: {str(e)}")
    except requests.exceptions.RequestException as e:
        logging.error(f"OPNSense poll: ({base_url}) request error: {str(e)}")
    except Exception as e:
        logging.exception(e)
        logging.error(f"OPNSense poll: ({base_url}) unexpected error: {str(e)}")

logging.info(f"OPNSense poll: returning {len(endpoints)} total endpoints "
             f"across {len(controllers)} controller(s)")
response["endpoints"] = endpoints
