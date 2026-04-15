"""
Oracle KVM Connect App - Resolve Script
Resolves VM properties for a specific endpoint by matching MAC or IP
against OLVM virtual machines.
"""

import requests

# params and response are pre-injected by the Connect framework

base_url = params.get("connect_oraclekvm_url", "").rstrip("/")

host_mac = params.get("mac", "")
host_ip = params.get("ip", "")

proxies = oraclekvm_lib.get_proxies_from_params(params)

response = {}
properties = {}

try:
    cluster_map = oraclekvm_lib.get_cluster_map(
        base_url, params, verify=ssl_verify, proxies=proxies
    )
    host_map = oraclekvm_lib.get_host_map(
        base_url, params, verify=ssl_verify, proxies=proxies
    )

    vms = oraclekvm_lib.get_all_vms(
        base_url, params, verify=ssl_verify, proxies=proxies
    )

    matched = False

    for vm in vms:
        vm_id = vm.get("id", "")
        if not vm_id:
            continue

        reported_devices = oraclekvm_lib.extract_vm_reported_devices_inline(vm)
        nics = oraclekvm_lib.extract_vm_nics_inline(vm)

        if not reported_devices and not nics:
            reported_devices = oraclekvm_lib.get_vm_reported_devices(
                base_url, vm_id, params, verify=ssl_verify, proxies=proxies
            )
            nics = oraclekvm_lib.get_vm_nics(
                base_url, vm_id, params, verify=ssl_verify, proxies=proxies
            )

        mac, ip_address = oraclekvm_lib.parse_vm_mac_and_ip(
            reported_devices, nics
        )

        if host_mac and mac and host_mac.upper() == mac.upper():
            matched = True
        elif host_ip and ip_address and host_ip == ip_address:
            matched = True

        if matched:
            properties = oraclekvm_lib.parse_vm_properties(
                vm, cluster_map=cluster_map, host_map=host_map
            )
            break

    if properties:
        response["properties"] = properties
    else:
        response["error"] = (
            f"No Oracle KVM VM found matching MAC={host_mac} or IP={host_ip}"
        )

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["error"] = f"OLVM API HTTP Error {status_code}"
except requests.exceptions.ConnectionError as e:
    response["error"] = f"Could not connect to OLVM API: {str(e)}"
except requests.exceptions.RequestException as e:
    response["error"] = f"OLVM API request error: {str(e)}"
except Exception as e:
    logging.exception(e)
    response["error"] = f"Unexpected error during Oracle KVM resolve: {str(e)}"
