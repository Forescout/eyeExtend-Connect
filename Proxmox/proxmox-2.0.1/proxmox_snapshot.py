"""
Proxmox Connect App - Snapshot Action
Creates a point-in-time snapshot of a VM or LXC container.
Useful for compliance/forensics before remediation actions.
"""

import requests

base_url = params.get("connect_proxmox_url", "")
token_id = params.get("connect_proxmox_token_id", "")
token_secret = params.get("connect_proxmox_token_secret", "")

vmid = params.get("connect_proxmox_vmid")
node = params.get("connect_proxmox_node", "")
guest_type = params.get("connect_proxmox_type", "")

# Action parameters
snapshot_name = params.get("connect_proxmox_snapshot_name", "")
snapshot_description = params.get("connect_proxmox_snapshot_description", "")

proxies = proxmox_lib.get_proxies_from_params(params)

response = {}

try:
    if not vmid or not node or not guest_type:
        response["succeeded"] = False
        response["troubleshooting"] = "Missing guest identification properties (vmid, node, or type)."
    elif not snapshot_name:
        response["succeeded"] = False
        response["troubleshooting"] = "Snapshot name is required."
    else:
        logging.info(f"Proxmox action: creating snapshot '{snapshot_name}' "
                     f"for {guest_type}/{vmid} on {node}")
        proxmox_lib.create_snapshot(
            base_url=base_url, node=node, guest_type=guest_type,
            vmid=vmid, snapname=snapshot_name,
            token_id=token_id, token_secret=token_secret,
            description=snapshot_description,
            verify=ssl_verify, proxies=proxies
        )
        response["succeeded"] = True
        logging.info(f"Proxmox action: snapshot '{snapshot_name}' "
                     f"for {guest_type}/{vmid} succeeded")

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["succeeded"] = False
    response["troubleshooting"] = (
        f"Proxmox API HTTP Error {status_code}. "
        f"Check API token has VM.Snapshot privilege."
    )
    logging.error(f"Proxmox snapshot failed: HTTP {status_code}")
except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["troubleshooting"] = f"Failed to create snapshot for {guest_type}/{vmid}: {str(e)}"
