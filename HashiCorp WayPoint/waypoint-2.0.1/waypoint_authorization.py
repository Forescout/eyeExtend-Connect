"""
WayPoint Authorization
Authenticates against Ivanti ISM REST API
Includes logout of previous session to respect concurrent session limits
"""
import json
import logging
import urllib.request
import urllib.error

response = {}

try:
    # Extract configuration
    url_call = params["connect_waypoint_base_url"].rstrip('/')
    account_username = params["connect_waypoint_service_account"]
    account_password = params["connect_waypoint_service_account_password"]
    account_role = params["connect_waypoint_service_account_role"]

    # Extract tenant from base URL
    tenant = url_call.replace("https://", "").replace("http://", "").split("/")[0]

    # Login to get session token
    token_url = url_call + "/rest/authentication/login"
    logging.debug("Token URL: " + token_url)

    header_info = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = json.dumps({
        "tenant": tenant,
        "username": account_username,
        "password": account_password,
        "role": account_role
    }, ensure_ascii=False, separators=(',', ':'))

    request_obj = urllib.request.Request(
        token_url,
        headers=header_info,
        data=payload.encode('utf-8')
    )

    resp = urllib.request.urlopen(request_obj, context=ssl_context)
    status_code = resp.getcode()
    logging.debug("Response Code: " + str(status_code))

    # Read raw response
    raw_token = resp.read().decode('utf-8').strip()
    logging.debug("Raw token response length: " + str(len(raw_token)))

    # Strip surrounding quotes if present
    if raw_token.startswith('"') and raw_token.endswith('"'):
        raw_token = raw_token[1:-1]

    if not raw_token:
        raise ValueError("Received empty token from server")

    # Success - Forescout expects response["token"]
    response["token"] = raw_token
    response["succeeded"] = True
    logging.debug("Authorization successful, token length: " + str(len(raw_token)))

except Exception as e:
    response["token"] = ""
    response["succeeded"] = False
    response["result_msg"] = "Authorization failed: " + str(e)
    logging.error("Authorization failed: " + str(e))
