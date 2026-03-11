"""
Twilio Connect App - Send SMS Action Script
Sends a text message to a specified phone number via the Twilio Messages API.

Action params (from policy configuration):
  - connect_twilio_to_number: Destination phone number (E.164 format)
  - connect_twilio_message_body: Text message content
"""

import requests

# params and response are pre-injected by the Connect framework

# Extract connection settings
account_sid = params.get("connect_twilio_account_sid", "")
auth_token = params.get("connect_twilio_auth_token", "")
from_number = params.get("connect_twilio_from_number", "")

# Extract action parameters
to_number = params.get("connect_twilio_to_number", "")
message_body = params.get("connect_twilio_message_body", "")

# Build proxy settings
proxies = twilio_lib.get_proxies_from_params(params)

response = {}

# Validate required parameters
if not to_number:
    response["succeeded"] = False
    response["troubleshooting"] = "To Phone Number is required."
elif not message_body:
    response["succeeded"] = False
    response["troubleshooting"] = "Message Body is required."
elif not from_number:
    response["succeeded"] = False
    response["troubleshooting"] = (
        "From Phone Number is not configured. "
        "Please set the Twilio phone number in the Connect App settings."
    )
else:
    try:
        # Send the SMS via Twilio API
        result = twilio_lib.send_sms(
            account_sid=account_sid,
            auth_token=auth_token,
            from_number=from_number,
            to_number=to_number,
            body=message_body,
            verify=ssl_verify,
            proxies=proxies
        )

        message_sid = result.get("sid", "unknown")
        message_status = result.get("status", "unknown")

        logging.info(
            f"Twilio SMS sent successfully. SID: {message_sid}, Status: {message_status}"
        )

        response["succeeded"] = True

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else "unknown"
        error_body = ""
        try:
            error_data = e.response.json()
            error_body = error_data.get("message", str(e))
        except Exception:
            error_body = str(e)

        logging.error(f"Twilio SMS failed with HTTP {status_code}: {error_body}")
        response["succeeded"] = False
        response["troubleshooting"] = f"Twilio API error (HTTP {status_code}): {error_body}"

    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection error sending Twilio SMS: {str(e)}")
        response["succeeded"] = False
        response["troubleshooting"] = (
            "Could not connect to Twilio API. Check network connectivity and proxy settings."
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error sending Twilio SMS: {str(e)}")
        response["succeeded"] = False
        response["troubleshooting"] = f"Request error: {str(e)}"
    except Exception as e:
        logging.exception(e)
        response["succeeded"] = False
        response["troubleshooting"] = f"Unexpected error: {str(e)}"
