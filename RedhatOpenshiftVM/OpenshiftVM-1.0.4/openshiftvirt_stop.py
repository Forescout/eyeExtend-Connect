"""
OpenShift Virt Connect App - Stop VM Action
Stops a running VirtualMachine via the KubeVirt subresource API.
"""

import requests

base_url = params.get("connect_openshiftvirt_url", "")
token = params.get("connect_openshiftvirt_token", "")

vm_name = params.get("connect_openshiftvirt_vm_name", "")
namespace = params.get("connect_openshiftvirt_namespace", "")

proxies = openshiftvirt_lib.get_proxies_from_params(params)

response = {}

try:
    if not vm_name or not namespace:
        response["succeeded"] = False
        response["troubleshooting"] = "Missing VM identification properties (vm_name or namespace)."
    else:
        logging.info(f"OpenShift Virt action: stopping VM {namespace}/{vm_name}")
        openshiftvirt_lib.vm_subresource_action(
            base_url=base_url, namespace=namespace, name=vm_name,
            action="stop", token=token,
            verify=ssl_verify, proxies=proxies
        )
        response["succeeded"] = True
        logging.info(f"OpenShift Virt action: stop VM {namespace}/{vm_name} succeeded")

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["succeeded"] = False
    response["troubleshooting"] = (
        f"OpenShift API HTTP Error {status_code}. "
        f"Check ServiceAccount RBAC: needs 'update' on virtualmachines/stop subresource."
    )
    logging.error(f"OpenShift Virt stop failed: HTTP {status_code}")
except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["troubleshooting"] = f"Failed to stop VM {namespace}/{vm_name}: {str(e)}"
