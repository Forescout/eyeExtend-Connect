"""
Proxmox Connect App - Cancel Set Tags (Restore Previous Tags)
Restores the previous tags saved in the cookie by the Set Tags action.
"""

import requests

base_url = params.get("connect_proxmox_url", "")
token_id = params.get("connect_proxmox_token_id", "")
token_secret = params.get("connect_proxmox_token_secret", "")

vmid = params.get("connect_proxmox_vmid")
node = params.get("connect_proxmox_node", "")
guest_type = params.get("connect_proxmox_type", "")

# Previous tags stored by the set_tags action
old_tags = params.get("cookie", "")

proxies = proxmox_lib.get_proxies_from_params(params)

response = {}

try:
    if not vmid or not node or not guest_type:
        response["succeeded"] = False
        response["troubleshooting"] = "Missing guest identification properties."
    else:
        logging.info(f"Proxmox cancel-set_tags: restoring tags on {guest_type}/{vmid} "
                     f"to '{old_tags}'")
        proxmox_lib.set_guest_tags(
            base_url=base_url, node=node, guest_type=guest_type,
            vmid=vmid, tags=old_tags,
            token_id=token_id, token_secret=token_secret,
            verify=ssl_verify, proxies=proxies
        )
        response["succeeded"] = True

except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["troubleshooting"] = f"Failed to restore tags on {guest_type}/{vmid}: {str(e)}"
