"""
OpenShift Virt Connect App - Poll/Discovery Script
Discovers all VirtualMachines and Nodes from the OpenShift cluster.
VMs are identified by MAC address with IP when available.
Nodes are identified by their IP address.
"""

import requests

# params and response are pre-injected by the Connect framework

# Extract connection settings
base_url = params.get("connect_openshiftvirt_url", "")
token = params.get("connect_openshiftvirt_token", "")

# Build proxy settings
proxies = openshiftvirt_lib.get_proxies_from_params(params)

response = {}
endpoints = []

logging.info("OpenShift Virt poll: starting discovery")

try:
    # Step 1: Get all VMs across all namespaces
    vms = openshiftvirt_lib.get_all_vms(
        base_url=base_url,
        token=token,
        verify=ssl_verify,
        proxies=proxies
    )

    logging.info(f"OpenShift Virt poll: found {len(vms)} VirtualMachines")

    # Step 2: Get all running VMIs to correlate runtime info
    vmis = openshiftvirt_lib.get_all_vmis(
        base_url=base_url,
        token=token,
        verify=ssl_verify,
        proxies=proxies
    )

    logging.info(f"OpenShift Virt poll: found {len(vmis)} VirtualMachineInstances")

    # Build VMI lookup index by (namespace, name)
    vmi_index = openshiftvirt_lib.build_vmi_index(vmis)

    # Count VMs per node for node properties
    vm_count_by_node = {}
    for vmi in vmis:
        node_name = vmi.get("status", {}).get("nodeName", "")
        if node_name:
            vm_count_by_node[node_name] = vm_count_by_node.get(node_name, 0) + 1

    # Process VMs
    for vm in vms:
        metadata = vm.get("metadata", {})
        vm_name = metadata.get("name", "")
        namespace = metadata.get("namespace", "")

        logging.info(f"OpenShift Virt poll: processing VM {namespace}/{vm_name}")

        if not vm_name or not namespace:
            continue

        # Find corresponding VMI (if running)
        vmi = vmi_index.get((namespace, vm_name))
        is_running = vmi is not None and vmi.get("status", {}).get("phase") == "Running"

        # Extract properties from VM and VMI
        properties = openshiftvirt_lib.extract_vm_properties(vm, vmi)

        # Set Forescout core $online property based on VM status
        properties["online"] = is_running

        # Extract MAC address — try VMI status first, then VM spec
        mac = None
        if vmi:
            mac = openshiftvirt_lib.extract_mac_from_vmi(vmi)
        if not mac:
            mac = openshiftvirt_lib.extract_mac_from_vm(vm)

        # Extract IP from VMI (only available for running instances)
        ip_address = None
        if vmi:
            ip_address = openshiftvirt_lib.extract_ip_from_vmi(vmi)

        # Build endpoint with identifier
        endpoint = {"properties": properties}

        if mac:
            endpoint["mac"] = mac
        if ip_address:
            endpoint["ip"] = ip_address

        if "mac" not in endpoint and "ip" not in endpoint:
            logging.warning(
                f"OpenShift Virt poll: skipping VM {namespace}/{vm_name} - "
                f"no MAC or IP available"
            )
            continue

        logging.info(
            f"OpenShift Virt poll: adding VM endpoint {namespace}/{vm_name} "
            f"mac={mac} ip={ip_address} online={is_running}"
        )
        endpoints.append(endpoint)

    # Step 3: Get all Nodes
    nodes = openshiftvirt_lib.get_all_nodes(
        base_url=base_url,
        token=token,
        verify=ssl_verify,
        proxies=proxies
    )

    logging.info(f"OpenShift Virt poll: found {len(nodes)} Nodes")

    # Process Nodes
    for node in nodes:
        node_name = node.get("metadata", {}).get("name", "")

        logging.info(f"OpenShift Virt poll: processing Node {node_name}")

        if not node_name:
            continue

        # Extract node IP
        node_ip = openshiftvirt_lib.extract_node_ip(node)
        if not node_ip:
            logging.warning(
                f"OpenShift Virt poll: skipping Node {node_name} - no IP available"
            )
            continue

        # Get VM count for this node
        vm_count = vm_count_by_node.get(node_name, 0)

        # Extract node properties
        properties = openshiftvirt_lib.extract_node_properties(node, vm_count)

        # Nodes are always online (if we can query them)
        properties["online"] = True

        # Build endpoint with IP identifier
        endpoint = {
            "ip": node_ip,
            "properties": properties
        }

        logging.info(
            f"OpenShift Virt poll: adding Node endpoint {node_name} "
            f"ip={node_ip} vm_count={vm_count}"
        )
        endpoints.append(endpoint)

    logging.info(f"OpenShift Virt poll: returning {len(endpoints)} endpoints "
                 f"({len(vms)} VMs, {len(nodes)} Nodes)")
    response["endpoints"] = endpoints

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["error"] = f"OpenShift API HTTP Error {status_code}"
    logging.error(f"OpenShift Virt poll failed with HTTP {status_code}")
except requests.exceptions.ConnectionError as e:
    response["error"] = f"Could not connect to OpenShift API: {str(e)}"
    logging.error(f"OpenShift Virt poll connection error: {str(e)}")
except requests.exceptions.RequestException as e:
    response["error"] = f"OpenShift API request error: {str(e)}"
    logging.error(f"OpenShift Virt poll request error: {str(e)}")
except Exception as e:
    logging.exception(e)
    response["error"] = f"Unexpected error during OpenShift Virt poll: {str(e)}"
