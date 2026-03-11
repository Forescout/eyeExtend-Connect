"""
OPNSense Connect App - Cancel Add to Alias (Remove from Alias)
Undoes an Add to Alias action by removing the IP from the alias.

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
        logging.info(f"OPNSense cancel: removing {host_ip} from alias '{alias_name}'")

        # Remove the IP from the alias
        opnsense_lib.delete_from_alias(
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
        logging.info(f"OPNSense cancel: successfully removed {host_ip} from alias '{alias_name}'")

except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["troubleshooting"] = (
        f"Failed to remove {host_ip} from alias '{alias_name}': {str(e)}"
    )
