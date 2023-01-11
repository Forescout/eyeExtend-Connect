import requests

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
site = params["connect_viakoo_site"] 
username = params["connect_viakoo_username"] 
password = params["connect_viakoo_password"] 


# ***** START - AUTH API CONFIGURATION ***** #
# Production
authentication_url = "https://login.viakoo.com/56463212-d9a4-444f-a60e-7e4559df14de/B2C_1A_ROPC_SIGNUP_SIGNIN/oauth2/v2.0/token"
client_id = "9f1dcd5f-6e57-432d-bb73-e0f77be938db"

login_parameters = {
    "username": username,
    "password": password,
    "grant_type": "password",
    "scope": "openid https://login.viakoo.com/14c6161a-eecc-4a31-97fd-cccb1f7a1841/com.viakoo.com:read",
    "response_type": "token",
    "client_id": client_id,
    "p": "B2C_1A_ROPC_SIGNUP_SIGNIN"
}

response = {}
with requests.Session() as request_session:
    logging.info("Starting auth request")
    # Making an API call to get the JWT token
    resp_auth = request_session.post(authentication_url, params=login_parameters)

    logging.debug("response: {}".format(resp_auth))

    # Like the action response, the response object must have a "succeeded" field to denote success. It can also optionally have 
    # a "result_msg" field to display a custom test result message.
    if resp_auth.status_code == requests.codes.ok:
        response["success"] = True
        response["token"] = resp_auth.json()['access_token']
    else:
        response["success"] = False
        response["token"] = ""