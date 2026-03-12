"""
OpenShift Virt Connect App - Shared Library
Provides helper functions for KubeVirt API communication on OpenShift.
Library files cannot access params directly - all values must be passed as arguments.
"""

import requests
import re
import math


# --- Proxy Helpers ---

def build_proxies(proxy_enable, proxy_ip, proxy_port, proxy_user="", proxy_pass=""):
    """Build a proxies dict for the requests library from Connect proxy settings."""
    if proxy_enable != "true":
        return None
    if proxy_user:
        proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
    else:
        proxy_url = f"http://{proxy_ip}:{proxy_port}"
    return {"http": proxy_url, "https": proxy_url}


def get_proxies_from_params(params):
    """Extract proxy settings from params and build a proxies dict."""
    return build_proxies(
        params.get("connect_proxy_enable", ""),
        params.get("connect_proxy_ip", ""),
        params.get("connect_proxy_port", ""),
        params.get("connect_proxy_username", ""),
        params.get("connect_proxy_password", "")
    )


# --- Auth & Request Helpers ---

def get_auth_header(token):
    """Build the Bearer authorization header for Kubernetes API requests.

    Args:
        token: ServiceAccount bearer token

    Returns:
        dict with Authorization and Accept headers
    """
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


def kube_request(method, base_url, endpoint, token, verify=True, proxies=None,
                 json_body=None):
    """Make an authenticated request to the Kubernetes/OpenShift API.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        base_url: Cluster API URL (e.g. https://api.mycluster.example.com:6443)
        endpoint: API path (e.g. /apis/kubevirt.io/v1/virtualmachines)
        token: ServiceAccount bearer token
        verify: SSL verification setting
        proxies: Proxy dict for requests
        json_body: JSON body for POST/PUT/PATCH requests

    Returns:
        requests.Response object
    """
    url = f"{base_url.rstrip('/')}{endpoint}"
    headers = get_auth_header(token)
    resp = requests.request(method.upper(), url, headers=headers,
                            verify=verify, proxies=proxies, json=json_body)
    resp.raise_for_status()
    return resp


# --- API Discovery Helpers ---

def get_api_version(base_url, token, verify=True, proxies=None):
    """Test connectivity by fetching cluster version info.

    Returns:
        dict with version data from the Kubernetes API
    """
    resp = kube_request("GET", base_url, "/version", token,
                        verify=verify, proxies=proxies)
    return resp.json()


def get_all_vms(base_url, token, verify=True, proxies=None):
    """Get all VirtualMachine resources across all namespaces.

    Handles Kubernetes list pagination via the 'continue' token.

    Returns:
        list of VM resource dicts
    """
    all_vms = []
    endpoint = "/apis/kubevirt.io/v1/virtualmachines?limit=500"

    while endpoint:
        resp = kube_request("GET", base_url, endpoint, token,
                            verify=verify, proxies=proxies)
        data = resp.json()
        items = data.get("items", [])
        all_vms.extend(items)

        # Handle pagination
        metadata = data.get("metadata", {})
        continue_token = metadata.get("continue", "")
        if continue_token:
            endpoint = (
                f"/apis/kubevirt.io/v1/virtualmachines"
                f"?limit=500&continue={continue_token}"
            )
        else:
            endpoint = None

    return all_vms


def get_all_vmis(base_url, token, verify=True, proxies=None):
    """Get all VirtualMachineInstance resources across all namespaces.

    VMIs represent running VM instances and contain runtime info like
    IP addresses, MAC addresses, node placement, and guest OS info.

    Returns:
        list of VMI resource dicts
    """
    all_vmis = []
    endpoint = "/apis/kubevirt.io/v1/virtualmachineinstances?limit=500"

    while endpoint:
        resp = kube_request("GET", base_url, endpoint, token,
                            verify=verify, proxies=proxies)
        data = resp.json()
        items = data.get("items", [])
        all_vmis.extend(items)

        metadata = data.get("metadata", {})
        continue_token = metadata.get("continue", "")
        if continue_token:
            endpoint = (
                f"/apis/kubevirt.io/v1/virtualmachineinstances"
                f"?limit=500&continue={continue_token}"
            )
        else:
            endpoint = None

    return all_vmis


def get_vmi(base_url, namespace, name, token, verify=True, proxies=None):
    """Get a specific VirtualMachineInstance by namespace and name.

    Returns:
        VMI resource dict, or None if not found (404)
    """
    endpoint = f"/apis/kubevirt.io/v1/namespaces/{namespace}/virtualmachineinstances/{name}"
    try:
        resp = kube_request("GET", base_url, endpoint, token,
                            verify=verify, proxies=proxies)
        return resp.json()
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None
        raise


def get_vm(base_url, namespace, name, token, verify=True, proxies=None):
    """Get a specific VirtualMachine by namespace and name.

    Returns:
        VM resource dict, or None if not found (404)
    """
    endpoint = f"/apis/kubevirt.io/v1/namespaces/{namespace}/virtualmachines/{name}"
    try:
        resp = kube_request("GET", base_url, endpoint, token,
                            verify=verify, proxies=proxies)
        return resp.json()
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None
        raise


# --- VM Action Helpers ---

def vm_subresource_action(base_url, namespace, name, action, token,
                          verify=True, proxies=None):
    """Execute a subresource action on a VirtualMachine.

    Supported actions: start, stop, restart, pause, unpause

    Args:
        base_url: Cluster API URL
        namespace: VM namespace
        name: VM name
        action: One of 'start', 'stop', 'restart', 'pause', 'unpause'
        token: Bearer token
        verify: SSL verification
        proxies: Proxy dict
    """
    # pause and unpause are on the VMI subresource, not VM
    if action in ("pause", "unpause"):
        endpoint = (
            f"/apis/subresources.kubevirt.io/v1"
            f"/namespaces/{namespace}/virtualmachineinstances/{name}/{action}"
        )
    else:
        endpoint = (
            f"/apis/subresources.kubevirt.io/v1"
            f"/namespaces/{namespace}/virtualmachines/{name}/{action}"
        )
    kube_request("PUT", base_url, endpoint, token,
                 verify=verify, proxies=proxies, json_body={})


# --- Data Extraction Helpers ---

def extract_mac_from_vm(vm):
    """Extract MAC address from VM spec interfaces.

    Looks in spec.template.spec.domain.devices.interfaces for a macAddress field.

    Args:
        vm: VM resource dict

    Returns:
        MAC as 12-char uppercase hex string (Forescout format), or None
    """
    spec = vm.get("spec", {})
    template = spec.get("template", {})
    domain_spec = template.get("spec", {})
    devices = domain_spec.get("domain", {}).get("devices", {})
    interfaces = devices.get("interfaces", [])

    for iface in interfaces:
        mac = iface.get("macAddress", "")
        if mac:
            return normalize_mac(mac)

    return None


def extract_mac_from_vmi(vmi):
    """Extract MAC address from VMI status interfaces.

    Args:
        vmi: VMI resource dict

    Returns:
        MAC as 12-char uppercase hex string (Forescout format), or None
    """
    if not vmi:
        return None

    status = vmi.get("status", {})
    interfaces = status.get("interfaces", [])
    for iface in interfaces:
        mac = iface.get("mac", "")
        if mac:
            return normalize_mac(mac)

    return None


def extract_ip_from_vmi(vmi):
    """Extract the primary IPv4 address from VMI status interfaces.

    Args:
        vmi: VMI resource dict

    Returns:
        IPv4 address string, or None
    """
    if not vmi:
        return None

    status = vmi.get("status", {})
    interfaces = status.get("interfaces", [])
    for iface in interfaces:
        ip = iface.get("ipAddress", "")
        if ip and not ip.startswith("127.") and ":" not in ip:
            return ip
        # Check ipAddresses list for IPv4
        ip_list = iface.get("ipAddresses", [])
        for addr in ip_list:
            if addr and not addr.startswith("127.") and ":" not in addr:
                return addr

    return None


def extract_all_ips_from_vmi(vmi):
    """Extract all IP addresses from VMI status interfaces as a comma-separated string.

    Args:
        vmi: VMI resource dict

    Returns:
        Comma-separated IP string, or empty string
    """
    if not vmi:
        return ""

    ips = []
    status = vmi.get("status", {})
    interfaces = status.get("interfaces", [])
    for iface in interfaces:
        ip_list = iface.get("ipAddresses", [])
        for addr in ip_list:
            if addr and addr not in ips:
                ips.append(addr)
        # Fallback: single ipAddress field
        if not ip_list:
            ip = iface.get("ipAddress", "")
            if ip and ip not in ips:
                ips.append(ip)

    return ", ".join(ips)


def extract_vm_properties(vm, vmi=None):
    """Extract Connect App properties from a VM and optional VMI.

    Args:
        vm: VM resource dict
        vmi: VMI resource dict (may be None if VM is stopped)

    Returns:
        dict of Connect App property tags to values
    """
    metadata = vm.get("metadata", {})
    spec = vm.get("spec", {})
    template = spec.get("template", {})
    template_spec = template.get("spec", {})
    domain = template_spec.get("domain", {})
    labels = metadata.get("labels", {})
    annotations = metadata.get("annotations", {})

    # CPU cores — check VM spec first, then VMI spec if running
    cpu_cores = domain.get("cpu", {}).get("cores", 0)
    if cpu_cores == 0 and vmi:
        # Fallback: check VMI spec for actual allocated cores
        vmi_spec = vmi.get("spec", {})
        vmi_domain = vmi_spec.get("domain", {})
        cpu_cores = vmi_domain.get("cpu", {}).get("cores", 0)

    # Memory — parse Kubernetes resource quantity (e.g., "2Gi", "512Mi", "1G")
    memory_str = domain.get("resources", {}).get("requests", {}).get("memory", "")
    if not memory_str:
        memory_str = domain.get("memory", {}).get("guest", "")
    if not memory_str and vmi:
        # Fallback: check VMI spec for actual allocated memory
        vmi_spec = vmi.get("spec", {})
        vmi_domain = vmi_spec.get("domain", {})
        memory_str = vmi_domain.get("memory", {}).get("guest", "")
    memory_mb = parse_k8s_memory_to_mb(memory_str)

    # Determine running state
    running = spec.get("running")
    if running is None:
        run_strategy = spec.get("runStrategy", "")
        running = run_strategy in ("Always", "RerunOnFailure")

    # VMI-derived fields
    vmi_phase = "Stopped"
    node_name = ""
    guest_os = ""
    ip_addresses = ""
    if vmi:
        vmi_status = vmi.get("status", {})
        vmi_phase = vmi_status.get("phase", "Unknown")
        node_name = vmi_status.get("nodeName", "")
        guest_os_info = vmi_status.get("guestOSInfo", {})
        guest_os = guest_os_info.get("prettyName", "") or guest_os_info.get("name", "")
        ip_addresses = extract_all_ips_from_vmi(vmi)

    # Creation date — ISO 8601 to epoch seconds
    creation_ts = metadata.get("creationTimestamp", "")
    creation_epoch = iso_to_epoch(creation_ts)

    # Labels as serialized string
    label_str = ", ".join(f"{k}={v}" for k, v in labels.items()) if labels else ""

    properties = {
        "connect_openshiftvirt_vm_name": metadata.get("name", ""),
        "connect_openshiftvirt_namespace": metadata.get("namespace", ""),
        "connect_openshiftvirt_status": vmi_phase,
        "connect_openshiftvirt_node": node_name,
        "connect_openshiftvirt_cpu_cores": cpu_cores,
        "connect_openshiftvirt_memory_mb": memory_mb,
        "connect_openshiftvirt_os_type": labels.get("vm.kubevirt.io/os", ""),
        "connect_openshiftvirt_creation_date": creation_epoch,
        "connect_openshiftvirt_labels": label_str,
        "connect_openshiftvirt_running": bool(running),
        "connect_openshiftvirt_guest_os": guest_os,
        "connect_openshiftvirt_template": annotations.get(
            "vm.kubevirt.io/template", ""),
        "connect_openshiftvirt_description": annotations.get("description", ""),
        "connect_openshiftvirt_ip_addresses": ip_addresses,
    }

    return properties


# --- Utility Helpers ---

def normalize_mac(mac_str):
    """Convert any MAC format to Forescout 12-char uppercase hex.

    Args:
        mac_str: MAC in any format (colon-separated, dash-separated, etc.)

    Returns:
        12-char uppercase hex string (e.g. "001122334455"), or None
    """
    if not mac_str:
        return None
    cleaned = mac_str.replace(":", "").replace("-", "").replace(".", "").upper()
    if len(cleaned) == 12 and all(c in "0123456789ABCDEF" for c in cleaned):
        return cleaned
    return None


def parse_k8s_memory_to_mb(mem_str):
    """Parse Kubernetes memory quantity to megabytes.

    Supports: Gi, Mi, Ki, G, M, K, Ti, and plain bytes.

    Args:
        mem_str: Kubernetes resource quantity string (e.g. "2Gi", "512Mi")

    Returns:
        Integer megabytes
    """
    if not mem_str:
        return 0

    mem_str = str(mem_str).strip()

    match = re.match(r'^(\d+(?:\.\d+)?)\s*(Ti|Gi|Mi|Ki|T|G|M|K|)?$', mem_str)
    if not match:
        return 0

    value = float(match.group(1))
    unit = match.group(2) or ""

    multipliers = {
        "Ti": 1024 * 1024,
        "Gi": 1024,
        "Mi": 1,
        "Ki": 1.0 / 1024,
        "T": 1000000,
        "G": 1000,
        "M": 1,
        "K": 0.001,
        "": 1.0 / 1048576,  # plain bytes to MB
    }

    return math.floor(value * multipliers.get(unit, 0))


def iso_to_epoch(iso_str):
    """Convert ISO 8601 timestamp to epoch seconds.

    Handles format: 2024-01-15T10:30:00Z

    Args:
        iso_str: ISO 8601 datetime string

    Returns:
        Integer epoch seconds, or 0 on failure
    """
    if not iso_str:
        return 0
    try:
        # Parse ISO 8601 without relying on datetime.fromisoformat (Py3.11 compatible)
        # Format: YYYY-MM-DDTHH:MM:SSZ
        iso_str = iso_str.rstrip("Z").split("+")[0].split(".")[0]
        parts = iso_str.split("T")
        if len(parts) != 2:
            return 0
        date_parts = parts[0].split("-")
        time_parts = parts[1].split(":")
        if len(date_parts) != 3 or len(time_parts) != 3:
            return 0

        year = int(date_parts[0])
        month = int(date_parts[1])
        day = int(date_parts[2])
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        second = int(time_parts[2])

        # Calculate epoch using the formula for days since epoch
        days = 0
        for y in range(1970, year):
            days += 366 if _is_leap(y) else 365
        month_days = [31, 28 + (1 if _is_leap(year) else 0),
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        for m in range(month - 1):
            days += month_days[m]
        days += day - 1

        return days * 86400 + hour * 3600 + minute * 60 + second
    except (ValueError, IndexError):
        return 0


def _is_leap(year):
    """Check if a year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def build_vmi_index(vmis):
    """Build a lookup dict of VMIs keyed by (namespace, name).

    Args:
        vmis: list of VMI resource dicts

    Returns:
        dict mapping (namespace, name) to VMI dict
    """
    index = {}
    for vmi in vmis:
        meta = vmi.get("metadata", {})
        ns = meta.get("namespace", "")
        name = meta.get("name", "")
        if ns and name:
            index[(ns, name)] = vmi
    return index


# --- Node Helpers ---

def get_all_nodes(base_url, token, verify=True, proxies=None):
    """Get all Node resources from the cluster.

    Handles Kubernetes list pagination via the 'continue' token.

    Returns:
        list of Node resource dicts
    """
    all_nodes = []
    endpoint = "/api/v1/nodes?limit=500"

    while endpoint:
        resp = kube_request("GET", base_url, endpoint, token,
                            verify=verify, proxies=proxies)
        data = resp.json()
        all_nodes.extend(data.get("items", []))

        # Check for pagination continue token
        metadata = data.get("metadata", {})
        cont = metadata.get("continue")
        if cont:
            endpoint = f"/api/v1/nodes?limit=500&continue={cont}"
        else:
            endpoint = None

    return all_nodes


def extract_node_ip(node):
    """Extract the primary IP address from a Node.

    Checks addresses in this order:
    1. InternalIP
    2. ExternalIP
    3. Hostname (fallback)

    Args:
        node: Node resource dict

    Returns:
        IP address string, or None
    """
    status = node.get("status", {})
    addresses = status.get("addresses", [])

    # Try InternalIP first
    for addr in addresses:
        if addr.get("type") == "InternalIP":
            return addr.get("address")

    # Try ExternalIP
    for addr in addresses:
        if addr.get("type") == "ExternalIP":
            return addr.get("address")

    # Try Hostname as fallback
    for addr in addresses:
        if addr.get("type") == "Hostname":
            return addr.get("address")

    return None


def extract_node_role(node):
    """Extract node role from labels.

    Checks for these labels:
    - node-role.kubernetes.io/master
    - node-role.kubernetes.io/worker
    - node-role.kubernetes.io/infra

    Args:
        node: Node resource dict

    Returns:
        Role string (e.g., "master", "worker", "infra") or empty string
    """
    labels = node.get("metadata", {}).get("labels", {})
    roles = []

    if "node-role.kubernetes.io/master" in labels or \
       "node-role.kubernetes.io/control-plane" in labels:
        roles.append("master")
    if "node-role.kubernetes.io/worker" in labels:
        roles.append("worker")
    if "node-role.kubernetes.io/infra" in labels:
        roles.append("infra")

    return ", ".join(roles) if roles else ""


def get_node_status(node):
    """Get the Ready condition status from a Node.

    Args:
        node: Node resource dict

    Returns:
        "Ready", "NotReady", or "Unknown"
    """
    status = node.get("status", {})
    conditions = status.get("conditions", [])

    for cond in conditions:
        if cond.get("type") == "Ready":
            status_val = cond.get("status", "")
            if status_val == "True":
                return "Ready"
            elif status_val == "False":
                return "NotReady"
            return "Unknown"

    return "Unknown"


def parse_k8s_cpu_to_cores(cpu_str):
    """Parse Kubernetes CPU quantity to number of cores.

    Supports: millicores (e.g., "500m"), plain cores (e.g., "4")

    Args:
        cpu_str: Kubernetes CPU quantity string

    Returns:
        Float number of cores
    """
    if not cpu_str:
        return 0

    cpu_str = str(cpu_str).strip()

    # Check for millicores (e.g., "500m")
    if cpu_str.endswith("m"):
        try:
            millicores = int(cpu_str[:-1])
            # Preserve fractional cores for allocatable values like "79500m".
            return millicores / 1000.0
        except ValueError:
            return 0

    # Plain cores (e.g., "4")
    try:
        return float(cpu_str)
    except ValueError:
        return 0


def parse_k8s_memory_to_gb(mem_str):
    """Parse Kubernetes memory quantity to gigabytes.

    Supports: Gi, Mi, Ki, G, M, K, Ti, and plain bytes.

    Args:
        mem_str: Kubernetes resource quantity string

    Returns:
        Integer gigabytes
    """
    if not mem_str:
        return 0

    mem_str = str(mem_str).strip()

    match = re.match(r'^(\d+(?:\.\d+)?)\s*(Ti|Gi|Mi|Ki|T|G|M|K|)?$', mem_str)
    if not match:
        return 0

    value = float(match.group(1))
    unit = match.group(2) or ""

    multipliers = {
        "Ti": 1024,
        "Gi": 1,
        "Mi": 1.0 / 1024,
        "Ki": 1.0 / (1024 * 1024),
        "T": 1000,
        "G": 1,
        "M": 0.001,
        "K": 0.000001,
        "": 1.0 / (1024 * 1024 * 1024),  # plain bytes to GB
    }

    return math.floor(value * multipliers.get(unit, 0))


def extract_node_properties(node, vm_count=0):
    """Extract Connect App properties from a Node.

    Args:
        node: Node resource dict
        vm_count: Number of VMs running on this node

    Returns:
        dict of Connect App property tags to values
    """
    metadata = node.get("metadata", {})
    spec = node.get("spec", {})
    status = node.get("status", {})
    labels = metadata.get("labels", {})

    # Capacity and allocatable resources
    capacity = status.get("capacity", {})
    allocatable = status.get("allocatable", {})

    cpu_capacity = parse_k8s_cpu_to_cores(capacity.get("cpu", ""))
    cpu_allocatable = parse_k8s_cpu_to_cores(allocatable.get("cpu", ""))
    memory_capacity_gb = parse_k8s_memory_to_gb(capacity.get("memory", ""))
    memory_allocatable_gb = parse_k8s_memory_to_gb(allocatable.get("memory", ""))

    # Node info
    node_info = status.get("nodeInfo", {})

    # Labels and taints as strings
    label_str = ", ".join(f"{k}={v}" for k, v in labels.items()) if labels else ""

    taints = spec.get("taints", [])
    taint_str = ", ".join(
        f"{t.get('key')}={t.get('value')}:{t.get('effect')}"
        for t in taints
    ) if taints else ""

    # Schedulable status (inverse of unschedulable)
    schedulable = not spec.get("unschedulable", False)

    properties = {
        "connect_openshiftvirt_node_name": metadata.get("name", ""),
        "connect_openshiftvirt_node_role": extract_node_role(node),
        "connect_openshiftvirt_node_status": get_node_status(node),
        "connect_openshiftvirt_node_cpu_capacity": cpu_capacity,
        "connect_openshiftvirt_node_cpu_allocatable": cpu_allocatable,
        "connect_openshiftvirt_node_memory_capacity_gb": memory_capacity_gb,
        "connect_openshiftvirt_node_memory_allocatable_gb": memory_allocatable_gb,
        "connect_openshiftvirt_node_os_image": node_info.get("osImage", ""),
        "connect_openshiftvirt_node_kernel_version": node_info.get("kernelVersion", ""),
        "connect_openshiftvirt_node_container_runtime": node_info.get("containerRuntimeVersion", ""),
        "connect_openshiftvirt_node_kubelet_version": node_info.get("kubeletVersion", ""),
        "connect_openshiftvirt_node_labels": label_str,
        "connect_openshiftvirt_node_taints": taint_str,
        "connect_openshiftvirt_node_vm_count": vm_count,
        "connect_openshiftvirt_node_schedulable": schedulable,
    }

    return properties


def cordon_node(base_url, node_name, token, verify=True, proxies=None):
    """Cordon a node (mark as unschedulable).

    Args:
        base_url: Cluster API URL
        node_name: Node name
        token: ServiceAccount bearer token
        verify: SSL verification setting
        proxies: Proxy dict for requests

    Returns:
        requests.Response object
    """
    patch_body = {
        "spec": {
            "unschedulable": True
        }
    }

    headers = get_auth_header(token)
    headers["Content-Type"] = "application/strategic-merge-patch+json"

    url = f"{base_url.rstrip('/')}/api/v1/nodes/{node_name}"
    resp = requests.patch(url, headers=headers, json=patch_body,
                          verify=verify, proxies=proxies)
    resp.raise_for_status()
    return resp


def uncordon_node(base_url, node_name, token, verify=True, proxies=None):
    """Uncordon a node (mark as schedulable).

    Args:
        base_url: Cluster API URL
        node_name: Node name
        token: ServiceAccount bearer token
        verify: SSL verification setting
        proxies: Proxy dict for requests

    Returns:
        requests.Response object
    """
    patch_body = {
        "spec": {
            "unschedulable": False
        }
    }

    headers = get_auth_header(token)
    headers["Content-Type"] = "application/strategic-merge-patch+json"

    url = f"{base_url.rstrip('/')}/api/v1/nodes/{node_name}"
    resp = requests.patch(url, headers=headers, json=patch_body,
                          verify=verify, proxies=proxies)
    resp.raise_for_status()
    return resp


def drain_node(base_url, node_name, token, verify=True, proxies=None):
    """Drain a node by cordoning it and evicting pods/VMs.

    Note: Full drain implementation requires iterating pods and creating
    Eviction resources. This is a simplified version that cordons the node.
    For production use, consider implementing full pod eviction logic.

    Args:
        base_url: Cluster API URL
        node_name: Node name
        token: ServiceAccount bearer token
        verify: SSL verification setting
        proxies: Proxy dict for requests

    Returns:
        requests.Response object from cordon operation
    """
    # First cordon the node
    return cordon_node(base_url, node_name, token, verify, proxies)
