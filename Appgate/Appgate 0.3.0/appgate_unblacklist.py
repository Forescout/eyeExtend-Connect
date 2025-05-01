###############################################################################
# User unblacklisting script.                                                   #
###############################################################################

# Get target user
user = params['connect_appgatesdp_user']
idp = params['connect_appgatesdp_idp']

# Initialize API object with app options
ag = appgate_api.appgate_api(params, ssl_verify)

# Prepare response dictionary
response = { "succeeded": False }

# If we have auth token, remove the user from blacklist
if (params["connect_authorization_token"]):
    logging.debug('Trying to unblacklist ' + user + '@' + idp)
    r = ag.unblacklist_user(user=user,provider=idp)
    if r == 204:
        logging.debug('Unblacklisted ' + user + '@' + idp)
        response["succeeded"] = True
    else:    
        logging.debug('Failed to unblacklist ' + user + '@' + idp)
        response["troubleshooting"] = "Error disabling user: Received code " + str(r)
else:
    response["troubleshooting"] = "No authoriztion token present."