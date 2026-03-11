"""
Twilio Connect App - Test Script
Validates connectivity by fetching account information from the Twilio API.
Called when the operator clicks "Test" in the Forescout Connect Options dialog.
"""

import requests

# params and response are pre-injected by the Connect framework

# Extract connection settings from params
account_sid = params.get("connect_twilio_account_sid", "")
auth_token = params.get("connect_twilio_auth_token", "")

# Build proxy settings
proxies = twilio_lib.get_proxies_from_params(params)

response = {}

try:
    # Test connectivity by fetching account information
    account_info = twilio_lib.test_connection(
        account_sid=account_sid,
        auth_token=auth_token,
        verify=ssl_verify,
        proxies=proxies
    )

    # Check that the account is active
    account_status = account_info.get("status", "unknown")
    friendly_name = account_info.get("friendly_name", "Unknown")

    if account_status == "active":
        response["succeeded"] = True
        response["result_msg"] = (
            f"Successfully connected to Twilio. "
            f"Account: {friendly_name} (Status: {account_status})"
        )
    else:
        response["succeeded"] = False
        response["result_msg"] = (
            f"Connected to Twilio but account is not active. "
            f"Account: {friendly_name} (Status: {account_status})"
        )

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    response["succeeded"] = False
    if status_code == 401:
        response["result_msg"] = (
            "Authentication failed. Please verify your Account SID and Auth Token."
        )
    else:
        response["result_msg"] = f"HTTP Error {status_code} connecting to Twilio."
except requests.exceptions.ConnectionError:
    response["succeeded"] = False
    response["result_msg"] = (
        "Could not connect to Twilio API. Please check network connectivity and proxy settings."
    )
except requests.exceptions.RequestException as e:
    response["succeeded"] = False
    response["result_msg"] = f"Request error connecting to Twilio: {str(e)}"
except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["result_msg"] = f"Unexpected error connecting to Twilio: {str(e)}"
