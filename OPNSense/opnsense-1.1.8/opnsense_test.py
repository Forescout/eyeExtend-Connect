"""
OPNSense Connect App - Test Script
Validates connectivity by fetching firmware status from each configured OPNSense instance.
Called when the operator clicks "Test" in the Forescout Connect Options dialog.

Multi-instance: Tests all comma-separated controllers and reports per-controller results.
"""

import requests

# params and response are pre-injected by the Connect framework

# Parse all configured controllers (supports comma-separated multi-instance)
controllers = opnsense_lib.get_all_controllers(params)

# Build proxy settings
proxies = opnsense_lib.get_proxies_from_params(params)

response = {}
messages = []
all_succeeded = True

for ctrl in controllers:
    base_url = ctrl["url"]
    api_key = ctrl["api_key"]
    api_secret = ctrl["api_secret"]

    try:
        # Test connectivity by fetching firmware status
        firmware = opnsense_lib.test_connection(
            base_url=base_url,
            api_key=api_key,
            api_secret=api_secret,
            verify=ssl_verify,
            proxies=proxies
        )

        product_version = firmware.get("product_version", "unknown")
        product_name = firmware.get("product_name", "OPNSense")

        messages.append(
            f"({base_url}) Successfully connected to {product_name}. "
            f"Version: {product_version}"
        )

    except requests.exceptions.HTTPError as e:
        all_succeeded = False
        status_code = e.response.status_code if e.response is not None else "unknown"
        if status_code == 401:
            messages.append(
                f"({base_url}) Authentication failed. "
                f"Please verify your API Key and API Secret."
            )
        elif status_code == 403:
            messages.append(
                f"({base_url}) Authorization failed. "
                f"The API user may lack required permissions."
            )
        else:
            messages.append(
                f"({base_url}) HTTP Error {status_code} connecting to OPNSense."
            )
    except requests.exceptions.ConnectionError:
        all_succeeded = False
        messages.append(
            f"({base_url}) Could not connect to OPNSense API. Please check the "
            f"Firewall URL, network connectivity, and proxy settings."
        )
    except requests.exceptions.RequestException as e:
        all_succeeded = False
        messages.append(
            f"({base_url}) Request error connecting to OPNSense: {str(e)}"
        )
    except Exception as e:
        logging.exception(e)
        all_succeeded = False
        messages.append(
            f"({base_url}) Unexpected error connecting to OPNSense: {str(e)}"
        )

response["succeeded"] = all_succeeded
response["result_msg"] = "\n".join(messages)
