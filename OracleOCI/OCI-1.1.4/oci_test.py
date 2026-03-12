"""
OCI Connect App - Test Script
Validates connectivity by making a simple API call to OCI.
If region is specified, tests that region. If blank, discovers subscribed regions
and tests the first one.
Called when the operator clicks "Test" in the Forescout Connect Options dialog.
"""

import requests

# params, response, logging, ssl_verify are pre-injected by the Connect framework

region_param = params.get("connect_oci_region", "")
tenancy_ocid = params.get("connect_oci_tenancy_ocid", "")
user_ocid = params.get("connect_oci_user_ocid", "")
fingerprint = params.get("connect_oci_fingerprint", "")
private_key_pem = params.get("connect_oci_private_key", "")

proxies = oci_lib.get_proxies_from_params(params)

response = {}

try:
    # Determine target regions
    target_regions = oci_lib.get_target_regions(
        region_param, tenancy_ocid, user_ocid, fingerprint, private_key_pem,
        verify=ssl_verify, proxies=proxies
    )

    # Test connectivity by listing instances (limit=1) in the first region
    test_region = target_regions[0]
    resp = oci_lib.test_connection(
        region=test_region,
        tenancy_ocid=tenancy_ocid,
        user_ocid=user_ocid,
        fingerprint=fingerprint,
        private_key_pem=private_key_pem,
        verify=ssl_verify,
        proxies=proxies
    )

    if region_param:
        response["succeeded"] = True
        response["result_msg"] = (
            "Successfully connected to OCI region {}. "
            "API call returned HTTP {}."
        ).format(test_region, resp.status_code)
    else:
        region_names = ", ".join(target_regions)
        response["succeeded"] = True
        response["result_msg"] = (
            "Successfully connected to OCI. "
            "Discovered {} subscribed region(s): {}. "
            "API call returned HTTP {}."
        ).format(len(target_regions), region_names, resp.status_code)

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["succeeded"] = False
    if status_code == 401:
        response["result_msg"] = (
            "Authentication failed (HTTP 401). Please verify your Tenancy OCID, "
            "User OCID, Fingerprint, and Private Key are correct."
        )
    elif status_code == 404:
        response["result_msg"] = (
            "API endpoint not found (HTTP 404). Please verify the Region '{}' is correct."
        ).format(region_param)
    else:
        response["result_msg"] = "HTTP Error {} connecting to OCI.".format(status_code)

except requests.exceptions.ConnectionError:
    response["succeeded"] = False
    response["result_msg"] = (
        "Could not connect to OCI API. Please check the Region, "
        "network connectivity, and proxy settings."
    )

except requests.exceptions.RequestException as e:
    response["succeeded"] = False
    response["result_msg"] = "Request error connecting to OCI: {}".format(str(e))

except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["result_msg"] = "Unexpected error connecting to OCI: {}".format(str(e))
