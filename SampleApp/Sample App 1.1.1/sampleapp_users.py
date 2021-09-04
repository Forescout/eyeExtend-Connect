import urllib.request
from connectproxyserver import ConnectProxyServer, ProxyProtocol
from urllib.request import HTTPError, URLError

# CONFIGURATION
url = params.get("connect_sampleapp_url")  # Server URL

response = {}
logging.debug("SampleApp instance cache for user")
# Check if we have valid auth token or not before processing.
if params.get("connect_authorization_token"):
    # ***** PART 2 - QUERY FOR USERS  ***** #
    jwt_token = params.get("connect_authorization_token")
    try:
        get_users_url = url + "/users/v2/"
        device_headers = {"Content-Type": "application/json; charset=utf-8",
                          "Authorization": "Bearer " + str(jwt_token)}

        # Create proxy server
        proxy_server = ConnectProxyServer(params)
        https_handler = urllib.request.HTTPSHandler(context=ssl_context)
        # Pass to use what HTTPS or HTTP or both in the protocol, pass down the ssl_context
        opener = proxy_server.get_urllib_request_opener(ProxyProtocol.all, https_handler)
        # Get users to save as app instance cache
        get_user_request = urllib.request.Request(get_users_url, headers=device_headers)
        # Use urlopen
        get_user_response = urllib.request.urlopen(get_user_request)
        request_response = json.loads(get_user_response.read())
        logging.debug("Response json: {}".format(json.dumps(request_response)))
        response_obj = {}

        for user_data in request_response.get("page_items"):
            user = {}
            email = user_data["email"]
            user["id"] = user_data["id"]
            user["first_name"] = user_data["first_name"]
            user["last_name"] = user_data["last_name"]
            response_obj[email] = user
        # For app instance cache, use the 'connect_app_instance_cache' to be the response key.
        # The value needs to be a string. It can be a json string containing different fields or any other format,
        # depending on how you want to use the data in other scripts.
        response["connect_app_instance_cache"] = json.dumps(response_obj)
        logging.debug("response: {}".format(response))
    except HTTPError as e:
        response["error"] = f"Could not connect to SampleApp. Response code: {e.code}."
    except URLError as e:
        response["error"] = f"Could not connect to SampleApp. {e.reason}."
    except Exception as e:
        response["error"] = f"Could not connect to SampleApp. {e}."
else:
    # In the response, put 'error' to indicate the error message.
    # 'connect_app_instance_cache' is optional when it has error.
    # if connect_app_instance_cache is in the response object, it will overwrite previous cache value.
    # Otherwise, the previous cache value will remain the same.
    response["connect_app_instance_cache"] = "{}"
    response["error"] = "No handler token found."
