# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
jwt_token = params.get("connect_authorization_token")  # auth token

response = {}
# Like the action response, the response object must have a "succeeded" field to denote success.
# It can also optionally have a "result_msg" field to display a custom test result message.
if jwt_token:
    response["succeeded"] = True
    response["result_msg"] = "Successfully connected."
else:
    response["succeeded"] = False
    response["result_msg"] = "Could not connect to SampleApp server."
