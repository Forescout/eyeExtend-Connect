"""
OpenShift Virt Connect App - Drain Node Action
Drains an OpenShift node by cordoning it and evicting pods/VMs for maintenance.
"""

import requests

# params and response are pre-injected by the Connect framework

# Extract connection settings
base_url = params.get("connect_openshiftvirt_url", "")
token = params.get("connect_openshiftvirt_token", "")

# Extract node identifier
node_name = params.get("connect_openshiftvirt_node_name", "")

# Build proxy settings
proxies = openshiftvirt_lib.get_proxies_from_params(params)

response = {}

try:
    if not node_name:
        response["succeeded"] = False
        response["result_msg"] = "Node name is required"
    else:
        # Drain the node (cordons and schedules evictions)
        openshiftvirt_lib.drain_node(
            base_url=base_url,
            node_name=node_name,
            token=token,
            verify=ssl_verify,
            proxies=proxies
        )

        response["succeeded"] = True
        response["result_msg"] = (
            f"Successfully drained node {node_name}. "
            f"Node is now cordoned and pods/VMs will be evicted."
        )

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["succeeded"] = False
    if status_code == 404:
        response["result_msg"] = f"Node {node_name} not found"
    elif status_code == 403:
        response["result_msg"] = "Forbidden: ServiceAccount lacks permission to update nodes"
    else:
        response["result_msg"] = f"Failed to drain node: HTTP {status_code}"

except requests.exceptions.ConnectionError as e:
    response["succeeded"] = False
    response["result_msg"] = f"Connection error: {str(e)}"

except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["result_msg"] = f"Error draining node: {str(e)}"
