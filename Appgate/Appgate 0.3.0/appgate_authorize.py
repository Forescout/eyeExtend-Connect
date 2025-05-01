###############################################################################
# Authoriztion script.                                                        #
###############################################################################

# Prepare response dictionary
response = {"token": "", "succeeded": False}

# Initialize API object with app options
ag = appgate_api.appgate_api(params, ssl_verify)

# Get the token.
r = ag.login()
if r:
    if (r['status_code'] == 200):
        response["succeeded"] = True 
        response["token"] = r['token']
        logging.debug('Authenticated to ' + ag.controller + ' as ' + ag.name)
    else:
        logging.debug('Failed to authenticate to ' + ag.controller + ' as ' + ag.name)
        response["error"] = f"Failed to authenticate. Response code {r['status_code']}"
else:
    response["error"] = "Failed to authenticate. HTTPS request failed."