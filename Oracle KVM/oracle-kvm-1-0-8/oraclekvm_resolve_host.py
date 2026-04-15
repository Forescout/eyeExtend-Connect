"""
Oracle KVM Connect App - Host Resolve Script
Resolves hypervisor host properties for a specific endpoint by matching MAC or IP
against OLVM hosts.
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

    hosts = oraclekvm_lib.get_all_hosts(
        base_url, params, verify=ssl_verify, proxies=proxies
    )

    matched = False

    for host in hosts:
        host_id = host.get("id", "")
        if not host_id:
            continue

        host_nics = oraclekvm_lib.extract_host_nics_inline(host)

        if not host_nics:
            host_nics = oraclekvm_lib.get_host_nics(
                base_url, host_id, params, verify=ssl_verify, proxies=proxies
            )

        mac, ip_address = oraclekvm_lib.parse_host_mac_and_ip(host_nics)

        if host_mac and mac and host_mac.upper() == mac.upper():
            matched = True
        elif host_ip and ip_address and host_ip == ip_address:
            matched = True

        if matched:
            properties = oraclekvm_lib.parse_host_properties(
                host, cluster_map=cluster_map
            )
            break

    if properties:
        response["properties"] = properties
    else:
        response["error"] = (
            f"No Oracle KVM host found matching MAC={host_mac} or IP={host_ip}"
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
    response["error"] = f"Unexpected error during Oracle KVM host resolve: {str(e)}"
