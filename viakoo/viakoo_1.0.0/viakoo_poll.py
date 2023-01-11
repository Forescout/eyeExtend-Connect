import requests
import socket

# CONFIGURATION
site = params["connect_viakoo_site"] 
username = params["connect_viakoo_username"] 
password = params["connect_viakoo_password"] 

 
response = {}
if "connect_authorization_token" in params and params["connect_authorization_token"] != "":
    auth_token = params["connect_authorization_token"]

    with requests.Session() as request_session:
        endpoints=[]

        device_headers = {
                "Authorization": "Bearer " + str(auth_token),
                "Host" : socket.gethostbyname(socket.gethostname())
            }

        message_info = viakoo_library.validate_site(request_session, device_headers, site)
    
        if message_info['site_id']:
            site_id = message_info['site_id']

            for type in viakoo_library.DEVICE_TYPES:
                list_parameters = {
                    "id": site_id,
                    "type": type
                }

                device_headers['Content-Type'] = 'application/x-www-form-urlencoded'

                resp_poll = request_session.post("{}/{}".format(viakoo_library.API_URL, viakoo_library.LIST_ENDPOINT), data=list_parameters, headers=device_headers)

                if resp_poll.status_code == requests.codes.ok:
                    resp_json = resp_poll.json()

                    #logging.debug(resp_json)

                    if 'components' in resp_json:
                        for device in resp_json["components"]:
                            #logging.debug("Working on device {}".format(device))
                            endpoint = {}
                            device_mac = "".join(device["macAddress"].split(":")).lower()
                            endpoint["mac"] = device_mac
                            properties = {}
                            for key, value in device.items():
                                #logging.debug("{} : {}".format(key, value))

                                if key in viakoo_library.FIELD_RESOLVE_MAP and key is not "macAddress":
                                    #logging.debug("Adding property {} to the endpoint".format(key))
                                    properties[viakoo_library.FIELD_RESOLVE_MAP[key]] = value
                                
                                #Set the IP address if possible
                                if key == "ipAddress":
                                    endpoint['ip'] = value

                            endpoint["properties"] = properties

                            logging.debug(endpoint)

                            endpoints.append(endpoint)
                    else:
                        response["error"] = resp_json["message"]
                
                response["endpoints"] = endpoints
        else:
            response["error"] = message_info['response']
else:
    response["error"] = "Unauthorized"