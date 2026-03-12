"""
OpenShift Virt Connect App - Resolve Script
Resolves properties for a specific host by matching MAC or IP against OpenShift VMs.
Called per-host when Forescout needs to refresh properties.
"""

import requests

# params and response are pre-injected by the Connect framework

# Extract connection settings
base_url = params.get("connect_openshiftvirt_url", "")
token = params.get("connect_openshiftvirt_token", "")

# Host identifiers from Forescout
host_mac = params.get("mac", "")
host_ip = params.get("ip", "")

# Build proxy settings
proxies = openshiftvirt_lib.get_proxies_from_params(params)

response = {}
properties = {}

try:
    # Get all VMs
    vms = openshiftvirt_lib.get_all_vms(
        base_url=base_url,
        token=token,
        verify=ssl_verify,
        proxies=proxies
    )

    # Get all running VMIs for runtime data
    vmis = openshiftvirt_lib.get_all_vmis(
        base_url=base_url,
        token=token,
        verify=ssl_verify,
        proxies=proxies
    )
    vmi_index = openshiftvirt_lib.build_vmi_index(vmis)

    matched = False

    for vm in vms:
        metadata = vm.get("metadata", {})
        vm_name = metadata.get("name", "")
        namespace = metadata.get("namespace", "")

        if not vm_name or not namespace:
            continue

        vmi = vmi_index.get((namespace, vm_name))

        # Try to match by MAC
        vm_mac = None
        if vmi:
            vm_mac = openshiftvirt_lib.extract_mac_from_vmi(vmi)
        if not vm_mac:
            vm_mac = openshiftvirt_lib.extract_mac_from_vm(vm)

        if host_mac and vm_mac and host_mac.upper() == vm_mac.upper():
            matched = True
        elif host_ip and vmi:
            # Try to match by IP
            vm_ip = openshiftvirt_lib.extract_ip_from_vmi(vmi)
            if vm_ip and host_ip == vm_ip:
                matched = True

        if matched:
            properties = openshiftvirt_lib.extract_vm_properties(vm, vmi)
            break

    if properties:
        response["properties"] = properties
    else:
        response["error"] = (
            f"No OpenShift VM found matching MAC={host_mac} or IP={host_ip}"
        )

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["error"] = f"OpenShift API HTTP Error {status_code}"
except requests.exceptions.ConnectionError as e:
    response["error"] = f"Could not connect to OpenShift API: {str(e)}"
except requests.exceptions.RequestException as e:
    response["error"] = f"OpenShift API request error: {str(e)}"
except Exception as e:
    logging.exception(e)
    response["error"] = f"Unexpected error during OpenShift Virt resolve: {str(e)}"
