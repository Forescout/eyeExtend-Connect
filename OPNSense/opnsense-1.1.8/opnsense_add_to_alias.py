"""
OPNSense Connect App - Add to Alias Action
Adds an endpoint IP address to an OPNSense firewall alias.
The alias must already exist on the firewall and be referenced by a firewall rule.

Multi-instance: Uses framework controller routing to connect to the correct firewall.
"""

import requests

# Extract connection settings via controller routing
ctrl = opnsense_lib.get_routed_controller(params)
base_url = ctrl["url"]
api_key = ctrl["api_key"]
api_secret = ctrl["api_secret"]

# Action parameters
alias_name = params.get("connect_opnsense_alias_name", "")
host_ip = params.get("ip", "")

proxies = opnsense_lib.get_proxies_from_params(params)

response = {}

try:
    if not alias_name:
        response["succeeded"] = False
        response["troubleshooting"] = "Missing alias name parameter."
    elif not host_ip:
        response["succeeded"] = False
        response["troubleshooting"] = "No IP address available for this endpoint."
    else:
        logging.info(f"OPNSense action: adding {host_ip} to alias '{alias_name}'")

        # Add the IP to the alias
        opnsense_lib.add_to_alias(
            base_url=base_url, api_key=api_key, api_secret=api_secret,
            alias_name=alias_name, address=host_ip,
            verify=ssl_verify, proxies=proxies
        )

        # Apply changes
        opnsense_lib.reconfigure_aliases(
            base_url=base_url, api_key=api_key, api_secret=api_secret,
            verify=ssl_verify, proxies=proxies
        )

        response["succeeded"] = True
        logging.info(f"OPNSense action: successfully added {host_ip} to alias '{alias_name}'")

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["succeeded"] = False
    if status_code == 404:
        response["troubleshooting"] = (
            f"Alias '{alias_name}' not found on the OPNSense firewall. "
            f"Create the alias first in the OPNSense web UI."
        )
    else:
        response["troubleshooting"] = (
            f"OPNSense API HTTP Error {status_code}. "
            f"Check API user has Firewall: Alias privileges."
        )
    logging.error(f"OPNSense add_to_alias failed: HTTP {status_code}")
except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["troubleshooting"] = (
        f"Failed to add {host_ip} to alias '{alias_name}': {str(e)}"
    )
