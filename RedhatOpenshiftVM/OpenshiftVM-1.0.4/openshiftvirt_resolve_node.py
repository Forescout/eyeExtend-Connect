"""
OpenShift Virt Connect App - Resolve Node Script
Resolves properties for a specific OpenShift Node by matching IP address.
Called per-host when Forescout needs to refresh node properties.
"""

import requests

# params and response are pre-injected by the Connect framework

# Extract connection settings
base_url = params.get("connect_openshiftvirt_url", "")
token = params.get("connect_openshiftvirt_token", "")

# Host identifier from Forescout
host_ip = params.get("ip", "")

# Build proxy settings
proxies = openshiftvirt_lib.get_proxies_from_params(params)

response = {}
properties = {}

try:
    # Get all Nodes
    nodes = openshiftvirt_lib.get_all_nodes(
        base_url=base_url,
        token=token,
        verify=ssl_verify,
        proxies=proxies
    )

    # Get all VMIs to count VMs per node
    vmis = openshiftvirt_lib.get_all_vmis(
        base_url=base_url,
        token=token,
        verify=ssl_verify,
        proxies=proxies
    )

    # Count VMs per node
    vm_count_by_node = {}
    for vmi in vmis:
        node_name = vmi.get("status", {}).get("nodeName", "")
        if node_name:
            vm_count_by_node[node_name] = vm_count_by_node.get(node_name, 0) + 1

    matched = False

    for node in nodes:
        node_name = node.get("metadata", {}).get("name", "")

        if not node_name:
            continue

        # Try to match by IP
        node_ip = openshiftvirt_lib.extract_node_ip(node)

        if host_ip and node_ip and host_ip == node_ip:
            matched = True
            vm_count = vm_count_by_node.get(node_name, 0)
            properties = openshiftvirt_lib.extract_node_properties(node, vm_count)
            break

    if properties:
        response["properties"] = properties
    else:
        response["error"] = f"No OpenShift Node found matching IP={host_ip}"

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["error"] = f"OpenShift API HTTP Error {status_code}"
except requests.exceptions.ConnectionError as e:
    response["error"] = f"Could not connect to OpenShift API: {str(e)}"
except requests.exceptions.RequestException as e:
    response["error"] = f"OpenShift API request error: {str(e)}"
except Exception as e:
    logging.exception(e)
    response["error"] = f"Unexpected error during OpenShift Node resolve: {str(e)}"
