"""
Proxmox Connect App - Set Tags Action
Sets tags on a VM or LXC container. Replaces all existing tags.
Stores previous tags in cookie for undo.
"""

import requests

base_url = params.get("connect_proxmox_url", "")
token_id = params.get("connect_proxmox_token_id", "")
token_secret = params.get("connect_proxmox_token_secret", "")

vmid = params.get("connect_proxmox_vmid")
node = params.get("connect_proxmox_node", "")
guest_type = params.get("connect_proxmox_type", "")

# Action parameter
new_tags = params.get("connect_proxmox_new_tags", "")

proxies = proxmox_lib.get_proxies_from_params(params)

response = {}

try:
    if not vmid or not node or not guest_type:
        response["succeeded"] = False
        response["troubleshooting"] = "Missing guest identification properties (vmid, node, or type)."
    else:
        # Save current tags for undo
        old_tags = proxmox_lib.get_guest_tags(
            base_url=base_url, node=node, guest_type=guest_type,
            vmid=vmid, token_id=token_id, token_secret=token_secret,
            verify=ssl_verify, proxies=proxies
        )

        logging.info(f"Proxmox action: setting tags on {guest_type}/{vmid} "
                     f"from '{old_tags}' to '{new_tags}'")
        proxmox_lib.set_guest_tags(
            base_url=base_url, node=node, guest_type=guest_type,
            vmid=vmid, tags=new_tags,
            token_id=token_id, token_secret=token_secret,
            verify=ssl_verify, proxies=proxies
        )
        response["succeeded"] = True
        # Store previous tags for undo/cancel
        response["cookie"] = old_tags
        logging.info(f"Proxmox action: set tags on {guest_type}/{vmid} succeeded")

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["succeeded"] = False
    response["troubleshooting"] = (
        f"Proxmox API HTTP Error {status_code}. "
        f"Check API token has VM.Config.Options privilege."
    )
    logging.error(f"Proxmox set_tags failed: HTTP {status_code}")
except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["troubleshooting"] = f"Failed to set tags on {guest_type}/{vmid}: {str(e)}"
