"""
Oracle KVM Connect App - Poll/Discovery Script
Discovers all VMs and hypervisor hosts from the OLVM cluster.
Returns endpoints identified by MAC address (from reported devices / NICs) with IP.
MAC and IP are written to Forescout core properties ($mac, $ip).
"""

import requests

# params and response are pre-injected by the Connect framework

base_url = params.get("connect_oraclekvm_url", "").rstrip("/")

proxies = oraclekvm_lib.get_proxies_from_params(params)

response = {}
endpoints = []

logging.info("Oracle KVM poll: starting discovery")

try:
    # Pre-fetch cluster and host name maps for friendly names
    cluster_map = oraclekvm_lib.get_cluster_map(
        base_url, params, verify=ssl_verify, proxies=proxies
    )
    host_map = oraclekvm_lib.get_host_map(
        base_url, params, verify=ssl_verify, proxies=proxies
    )

    # -----------------------------------------------------------------------
    # VM Discovery
    # -----------------------------------------------------------------------
    vms = oraclekvm_lib.get_all_vms(
        base_url, params, verify=ssl_verify, proxies=proxies
    )
    logging.info(f"Oracle KVM poll: retrieved {len(vms)} VMs")

    for vm in vms:
        vm_id = vm.get("id", "")
        vm_name = vm.get("name", "")

        if not vm_id:
            continue

        # Extract MAC and IP from inline-followed data (no extra API calls)
        reported_devices = oraclekvm_lib.extract_vm_reported_devices_inline(vm)
        nics = oraclekvm_lib.extract_vm_nics_inline(vm)

        # Fallback: if follow didn't inline the data, fetch individually
        if not reported_devices and not nics:
            logging.debug(f"Oracle KVM poll: VM {vm_id} no inline NIC data, fetching individually")
            reported_devices = oraclekvm_lib.get_vm_reported_devices(
                base_url, vm_id, params, verify=ssl_verify, proxies=proxies
            )
            nics = oraclekvm_lib.get_vm_nics(
                base_url, vm_id, params, verify=ssl_verify, proxies=proxies
            )

        mac, ip_address = oraclekvm_lib.parse_vm_mac_and_ip(
            reported_devices, nics
        )

        if not mac and not ip_address:
            logging.warning(
                f"Oracle KVM poll: skipping VM {vm_id} ({vm_name}) — "
                f"no MAC or IP available"
            )
            continue

        # Build properties
        properties = oraclekvm_lib.parse_vm_properties(
            vm, cluster_map=cluster_map, host_map=host_map
        )
        is_running = vm.get("status", "") == "up"
        properties["online"] = is_running

        endpoint = {"properties": properties}
        if mac:
            endpoint["mac"] = mac
        if ip_address:
            endpoint["ip"] = ip_address

        logging.debug(
            f"Oracle KVM poll: adding VM {vm_id} ({vm_name}) "
            f"mac={mac} ip={ip_address} online={is_running}"
        )
        endpoints.append(endpoint)

    # -----------------------------------------------------------------------
    # Host Discovery
    # -----------------------------------------------------------------------
    logging.info("Oracle KVM poll: starting host discovery")

    hosts = oraclekvm_lib.get_all_hosts(
        base_url, params, verify=ssl_verify, proxies=proxies
    )
    logging.info(f"Oracle KVM poll: retrieved {len(hosts)} hosts")

    for host in hosts:
        host_id = host.get("id", "")
        host_name = host.get("name", "")

        if not host_id:
            continue

        # Extract MAC and IP from inline-followed NIC data
        host_nics = oraclekvm_lib.extract_host_nics_inline(host)

        # Fallback: if follow didn't inline the data, fetch individually
        if not host_nics:
            logging.info(f"Oracle KVM poll: host {host_id} has no inline NIC data, fetching individually")
            host_nics = oraclekvm_lib.get_host_nics(
                base_url, host_id, params, verify=ssl_verify, proxies=proxies
            )

        mac, ip_address = oraclekvm_lib.parse_host_mac_and_ip(host_nics)

        if not mac and not ip_address:
            logging.warning(
                f"Oracle KVM poll: skipping host {host_id} ({host_name}) — "
                f"no MAC or IP available"
            )
            continue

        host_props = oraclekvm_lib.parse_host_properties(
            host, cluster_map=cluster_map
        )
        host_props["online"] = host.get("status", "") == "up"

        host_endpoint = {"properties": host_props}
        if mac:
            host_endpoint["mac"] = mac
        if ip_address:
            host_endpoint["ip"] = ip_address

        logging.info(
            f"Oracle KVM poll: adding host {host_id} ({host_name}) "
            f"mac={mac} ip={ip_address}"
        )
        endpoints.append(host_endpoint)

    logging.info(f"Oracle KVM poll: returning {len(endpoints)} endpoints")
    response["endpoints"] = endpoints

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["error"] = f"OLVM API HTTP Error {status_code}"
    logging.error(f"Oracle KVM poll failed with HTTP {status_code}")
except requests.exceptions.ConnectionError as e:
    response["error"] = f"Could not connect to OLVM API: {str(e)}"
    logging.error(f"Oracle KVM poll connection error: {str(e)}")
except requests.exceptions.RequestException as e:
    response["error"] = f"OLVM API request error: {str(e)}"
    logging.error(f"Oracle KVM poll request error: {str(e)}")
except Exception as e:
    logging.exception(e)
    response["error"] = f"Unexpected error during Oracle KVM poll: {str(e)}"
