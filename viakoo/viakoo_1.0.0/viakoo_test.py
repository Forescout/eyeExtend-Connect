import requests
import socket

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
site = params["connect_viakoo_site"] 
username = params["connect_viakoo_username"] 
password = params["connect_viakoo_password"] 


# Actions Parameters 
# 

response = {}
response["succeeded"] = False

if "connect_authorization_token" in params and params["connect_authorization_token"] != "":
    auth_token = params["connect_authorization_token"]
    with requests.Session() as request_session:
        device_headers = {
                "Authorization": "Bearer " + str(auth_token),
                "Host" : socket.gethostbyname(socket.gethostname())
            }


        message_info = viakoo_library.validate_site(request_session, device_headers, site)

        response["result_msg"] = message_info['response']
        
        if message_info["site_id"]:
            response["succeeded"] = True
else:
    response["result_msg"] = "Could not connect to Viakoo server."