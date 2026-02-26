"""
Proxmox Connect App - Cancel Suspend (Resume)
Undoes a Suspend action by resuming the QEMU VM.
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
    if not vmid or not node:
        response["succeeded"] = False
        response["troubleshooting"] = "Missing guest identification properties."
    else:
        logging.info(f"Proxmox cancel-suspend: resuming qemu/{vmid} on {node}")
        proxmox_lib.change_guest_status(
            base_url=base_url, node=node, guest_type="qemu",
            vmid=vmid, action="resume",
            token_id=token_id, token_secret=token_secret,
            verify=ssl_verify, proxies=proxies
        )
        response["succeeded"] = True

except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["troubleshooting"] = f"Failed to cancel suspend (resume) qemu/{vmid}: {str(e)}"
