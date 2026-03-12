"""
OpenShift Virt Connect App - Test Script
Validates connectivity by fetching cluster version info from the Kubernetes API.
Called when the operator clicks "Test" in the Forescout Connect Options dialog.
"""

import requests

# params and response are pre-injected by the Connect framework

# Extract connection settings from params
base_url = params.get("connect_openshiftvirt_url", "")
token = params.get("connect_openshiftvirt_token", "")

# Build proxy settings
proxies = openshiftvirt_lib.get_proxies_from_params(params)

response = {}

try:
    # Test connectivity by fetching Kubernetes version
    version_info = openshiftvirt_lib.get_api_version(
        base_url=base_url,
        token=token,
        verify=ssl_verify,
        proxies=proxies
    )

    k8s_version = version_info.get("gitVersion", "unknown")
    platform = version_info.get("platform", "unknown")

    # Also verify KubeVirt API is available by listing VMs (first page only)
    openshiftvirt_lib.kube_request(
        "GET", base_url,
        "/apis/kubevirt.io/v1/virtualmachines?limit=1",
        token, verify=ssl_verify, proxies=proxies
    )

    response["succeeded"] = True
    response["result_msg"] = (
        f"Successfully connected to OpenShift cluster. "
        f"Kubernetes {k8s_version} ({platform}). KubeVirt API is available."
    )

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["succeeded"] = False
    if status_code == 401:
        response["result_msg"] = (
            "Authentication failed. Please verify the Service Account Token."
        )
    elif status_code == 403:
        response["result_msg"] = (
            "Authorization failed. The ServiceAccount may lack RBAC permissions "
            "to list kubevirt.io/v1 VirtualMachines."
        )
    elif status_code == 404:
        response["result_msg"] = (
            "KubeVirt API not found. Ensure OpenShift Virtualization operator "
            "is installed on the cluster."
        )
    else:
        response["result_msg"] = f"HTTP Error {status_code} connecting to OpenShift."
except requests.exceptions.ConnectionError:
    response["succeeded"] = False
    response["result_msg"] = (
        "Could not connect to OpenShift API. Please check the Cluster API URL, "
        "network connectivity, and proxy settings."
    )
except requests.exceptions.RequestException as e:
    response["succeeded"] = False
    response["result_msg"] = f"Request error connecting to OpenShift: {str(e)}"
except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["result_msg"] = f"Unexpected error connecting to OpenShift: {str(e)}"
