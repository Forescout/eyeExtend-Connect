###############################################################################
# User blacklisting script.                                                   #
###############################################################################

# Get target user
user = params['connect_appgatesdp_user']
idp = params['connect_appgatesdp_idp']

# Initialize API object with app options
ag = appgate_api.appgate_api(params, ssl_verify)

# Prepare response dictionary
response = {"succeeded": False}

# If we have auth token, blacklist the user
if (params["connect_authorization_token"]):
    logging.debug('Trying to blacklist ' + user + '@' + idp)
    r = ag.blacklist_user(user=user,provider=idp,reason='Blacklisted by Forescout')
    if r == 200:
        logging.debug('Blacklisted ' + user + '@' + idp)
        t = ag.revoke_tokens(user=user,provider=idp,reason='Blacklisting')
        if t == 200:
            response["succeeded"] = True
        else:
            logging.debug('Failed to revoke tokens for ' + user + '@' + idp + '. Returned code: ' + str(t))
            response["troubleshooting"] = "User blacklisted, but could not revoke tokens"
    else:    
        logging.debug('Failed to blacklist ' + user + '@' + idp + '. Returned code: ' + str(r))
        response["troubleshooting"] = "Error disabling user: Received code " + str(r)
else:
    response["troubleshooting"] = "No authoriztion token present."