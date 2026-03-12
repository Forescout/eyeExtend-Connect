"""
OpenShift Virt Connect App - Cancel Unpause (Pause)
Undoes an Unpause action by pausing the VM.
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
        response["troubleshooting"] = "Missing VM identification properties."
    else:
        logging.info(f"OpenShift Virt cancel-unpause: pausing VM {namespace}/{vm_name}")
        openshiftvirt_lib.vm_subresource_action(
            base_url=base_url, namespace=namespace, name=vm_name,
            action="pause", token=token,
            verify=ssl_verify, proxies=proxies
        )
        response["succeeded"] = True

except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["troubleshooting"] = f"Failed to cancel unpause (pause) VM {namespace}/{vm_name}: {str(e)}"
