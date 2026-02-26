"""
Proxmox Connect App - Test Script
Validates connectivity by fetching version information from the Proxmox VE API.
Called when the operator clicks "Test" in the Forescout Connect Options dialog.
"""

import requests

# params and response are pre-injected by the Connect framework

# Extract connection settings from params
base_url = params.get("connect_proxmox_url", "")
token_id = params.get("connect_proxmox_token_id", "")
token_secret = params.get("connect_proxmox_token_secret", "")

# Build proxy settings
proxies = proxmox_lib.get_proxies_from_params(params)

response = {}

try:
    # Test connectivity by fetching Proxmox version
    version_info = proxmox_lib.test_connection(
        base_url=base_url,
        token_id=token_id,
        token_secret=token_secret,
        verify=ssl_verify,
        proxies=proxies
    )

    pve_version = version_info.get("version", "unknown")
    pve_release = version_info.get("release", "unknown")

    response["succeeded"] = True
    response["result_msg"] = (
        f"Successfully connected to Proxmox VE. "
        f"Version: {pve_version} (Release: {pve_release})"
    )

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["succeeded"] = False
    if status_code == 401:
        response["result_msg"] = (
            "Authentication failed. Please verify your API Token ID and Secret."
        )
    elif status_code == 403:
        response["result_msg"] = (
            "Authorization failed. The API token may lack required permissions."
        )
    else:
        response["result_msg"] = f"HTTP Error {status_code} connecting to Proxmox."
except requests.exceptions.ConnectionError:
    response["succeeded"] = False
    response["result_msg"] = (
        "Could not connect to Proxmox API. Please check the Server URL, "
        "network connectivity, and proxy settings."
    )
except requests.exceptions.RequestException as e:
    response["succeeded"] = False
    response["result_msg"] = f"Request error connecting to Proxmox: {str(e)}"
except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["result_msg"] = f"Unexpected error connecting to Proxmox: {str(e)}"
