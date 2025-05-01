###############################################################################
# Test script.                                                                #
###############################################################################

logging.debug('Checking authorization token.')
response = {}
r = params.get("connect_authorization_token")
if r:
    response["succeeded"] = True
    response["result_msg"] = "Authorized."
else:
    response["succeeded"] = False
    response["result_msg"] = "Authoriztion token not found."
