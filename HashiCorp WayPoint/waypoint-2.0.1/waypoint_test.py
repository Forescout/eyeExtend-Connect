"""
WayPoint Connection Test
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

    # Step 1: Authenticate
    # Use base URL directly: https://charter-amc-uat.ivanticloud.com/api
    token_url = url_call + "/rest/authentication/login"

    # Build payload exactly as Postman sends it
    payload = '{"tenant":"' + tenant + '","username":"' + account_username + '","password":"' + account_password + '","role":"' + account_role + '"}'
    payload_bytes = payload.encode('utf-8')

    logging.debug("Auth URL: " + token_url)
    logging.debug("Payload: " + payload.replace(account_password, "***"))
    logging.debug("Payload bytes length: " + str(len(payload_bytes)))

    auth_request = urllib.request.Request(token_url)
    auth_request.add_header('Content-Type', 'application/json')
    auth_request.data = payload_bytes

    auth_resp = urllib.request.urlopen(auth_request, context=ssl_context)
    raw_token = auth_resp.read().decode('utf-8').strip()

    # Strip quotes if present
    if raw_token.startswith('"') and raw_token.endswith('"'):
        raw_token = raw_token[1:-1]

    if not raw_token:
        raise ValueError("Auth returned empty token")

    # Step 2: Test API call
    tablename = params.get("connect_waypoint_ci_configurationitem", "CI__Printers")
    test_url = url_call + "/odata/businessobject/" + tablename

    api_request = urllib.request.Request(test_url)
    api_request.add_header('Authorization', raw_token)
    api_request.add_header('Accept', 'application/json')

    api_resp = urllib.request.urlopen(api_request, context=ssl_context)
    api_data = json.loads(api_resp.read())
    record_count = len(api_data.get('value', []))

    response["succeeded"] = True
    response["result_msg"] = (
        "Successfully connected to WayPoint API.\n"
        "Authentication: OK\n"
        "Table: " + tablename + "\n"
        "Records: " + str(record_count)
    )

except urllib.error.HTTPError as e:
    error_body = ""
    try:
        error_body = e.read().decode('utf-8')
    except Exception:
        pass
    response["succeeded"] = False
    response["result_msg"] = (
        "HTTP " + str(e.code) + " from " + str(e.url) +
        " | PayloadLen: " + str(len(payload_bytes)) +
        " | Body: " + error_body[:250]
    )

except Exception as e:
    response["succeeded"] = False
    response["result_msg"] = "Error: " + str(e) + " | AuthURL: " + token_url
