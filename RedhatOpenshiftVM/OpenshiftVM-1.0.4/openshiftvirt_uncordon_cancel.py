"""
OpenShift Virt Connect App - Uncordon Node Cancel (Undo)
Cordons a node that was previously uncordoned.
"""

import requests

# params and response are pre-injected by the Connect framework

# Extract connection settings
base_url = params.get("connect_openshiftvirt_url", "")
token = params.get("connect_openshiftvirt_token", "")

# Extract node name from cookie
node_name = params.get("cookie", "")

# Build proxy settings
proxies = openshiftvirt_lib.get_proxies_from_params(params)

response = {}

try:
    if not node_name:
        response["succeeded"] = False
        response["result_msg"] = "Node name is required (from cookie)"
    else:
        # Cordon the node
        openshiftvirt_lib.cordon_node(
            base_url=base_url,
            node_name=node_name,
            token=token,
            verify=ssl_verify,
            proxies=proxies
        )

        response["succeeded"] = True
        response["result_msg"] = f"Successfully cordoned node {node_name} (undo uncordon)"

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["succeeded"] = False
    if status_code == 404:
        response["result_msg"] = f"Node {node_name} not found"
    else:
        response["result_msg"] = f"Failed to cordon node: HTTP {status_code}"

except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["result_msg"] = f"Error cordoning node: {str(e)}"
