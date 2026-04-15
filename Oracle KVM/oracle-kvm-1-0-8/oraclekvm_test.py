"""
Oracle KVM Connect App - Test Script
Verifies connectivity and authentication against the OLVM REST API.
"""

import requests

# params and response are pre-injected by the Connect framework

base_url = params.get("connect_oraclekvm_url", "").rstrip("/")

proxies = oraclekvm_lib.get_proxies_from_params(params)

response = {}

try:
    product_info = oraclekvm_lib.test_connection(
        base_url=base_url,
        p=params,
        verify=ssl_verify,
        proxies=proxies,
    )

    version = product_info.get("version", {})
    if version:
        major = version.get("major", "")
        minor = version.get("minor", "")
        build = version.get("build", "")
        ver_str = f"{major}.{minor}.{build}"
    else:
        ver_str = "unknown"

    product_name = product_info.get("name", "Oracle Virtualization Manager")
    response["succeeded"] = True
    response["result_msg"] = (
        f"Connected to {product_name} version {ver_str}"
    )
    logging.info(f"Oracle KVM test: connection successful — {product_name} {ver_str}")

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    if status_code == 401:
        response["succeeded"] = False
        response["result_msg"] = (
            "Authentication failed (HTTP 401). Check username, domain, and password."
        )
    elif status_code == 403:
        response["succeeded"] = False
        response["result_msg"] = (
            "Authorization denied (HTTP 403). User may lack required privileges."
        )
    else:
        response["succeeded"] = False
        response["result_msg"] = f"OLVM API returned HTTP {status_code}"
    logging.error(f"Oracle KVM test: HTTP error {status_code}")

except requests.exceptions.ConnectionError:
    response["succeeded"] = False
    response["result_msg"] = (
        f"Could not connect to {base_url}. Verify the URL and network connectivity."
    )
    logging.error("Oracle KVM test: connection error")

except Exception as e:
    response["succeeded"] = False
    response["result_msg"] = f"Test failed: {str(e)}"
    logging.error(f"Oracle KVM test error: {str(e)}")
