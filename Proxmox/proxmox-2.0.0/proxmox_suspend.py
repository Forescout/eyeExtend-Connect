"""
Proxmox Connect App - Suspend Action
Suspends a running QEMU VM (pauses execution, preserves state in memory).
Only supported for QEMU VMs, not LXC containers.
"""

import requests

base_url = params.get("connect_proxmox_url", "")
token_id = params.get("connect_proxmox_token_id", "")
token_secret = params.get("connect_proxmox_token_secret", "")

vmid = params.get("connect_proxmox_vmid")
node = params.get("connect_proxmox_node", "")
guest_type = params.get("connect_proxmox_type", "")

proxies = proxmox_lib.get_proxies_from_params(params)

response = {}

try:
    if not vmid or not node or not guest_type:
        response["succeeded"] = False
        response["troubleshooting"] = "Missing guest identification properties (vmid, node, or type)."
    elif guest_type != "qemu":
        response["succeeded"] = False
        response["troubleshooting"] = "Suspend is only supported for QEMU VMs, not LXC containers."
    else:
        logging.info(f"Proxmox action: suspending qemu/{vmid} on {node}")
        proxmox_lib.change_guest_status(
            base_url=base_url, node=node, guest_type="qemu",
            vmid=vmid, action="suspend",
            token_id=token_id, token_secret=token_secret,
            verify=ssl_verify, proxies=proxies
        )
        response["succeeded"] = True
        logging.info(f"Proxmox action: suspend qemu/{vmid} succeeded")

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["succeeded"] = False
    response["troubleshooting"] = f"Proxmox API HTTP Error {status_code}. Check API token has VM.PowerMgmt privilege."
    logging.error(f"Proxmox suspend failed: HTTP {status_code}")
except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["troubleshooting"] = f"Failed to suspend qemu/{vmid}: {str(e)}"
