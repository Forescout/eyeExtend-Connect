import requests
import socket

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
site = params["connect_viakoo_site"] 
username = params["connect_viakoo_username"] 
password = params["connect_viakoo_password"] 


# For properties and actions defined in the 'property.conf' file, CounterACT properties can be added as dependencies. These values will be
# found in the params dictionary if CounterACT was able to resolve the properties. If not, they will not be found in the params dictionary.
response = {}

if "connect_authorization_token" in params and params["connect_authorization_token"] != "":
    auth_token = params["connect_authorization_token"]

    mac = None
    if "mac" in params:
        mac = ':'.join(params["mac"][i:i+2] for i in range(0,12,2))
    
    ip = None
    if "ip" in params:
        ip = params["ip"]

    if ip or mac:
        # All responses from scripts must contain the JSON object 'response'. Host property resolve scripts will need to populate a
        # 'properties' JSON object within the JSON object 'response'. The 'properties' object will be a key, value mapping between the
        # CounterACT property name and the value of the property.
        with requests.Session() as request_session:
            device_headers = {
                "Authorization": "Bearer " + str(auth_token),
                "Host" : socket.gethostbyname(socket.gethostname())
            }

            message_info = viakoo_library.validate_site(request_session, device_headers, site)
        
            if message_info['site_id']:
                site_id = resp_site_check.json()["currentNav"]["id"]

                list_parameters = {
                    "id": site_id,
                    "type": viakoo_to_ct_props_map[classType]
                }

                logging.debug("Resolving parameters: {}".format(viakoo_to_ct_props_map[classType]))

                device_headers['Content-Type'] = 'application/x-www-form-urlencoded'

                resp_poll = request_session.post("{}/{}".format(viakoo_library.API_URL, viakoo_library.LIST_ENDPOINT), data=list_parameters, headers=device_headers)
                
                endpoint = {}
                if resp_poll.status_code == requests.codes.ok:
                    for device in resp_poll.json()['components']:
                        # Check if this device has the correct MAC or IP address we are looking for
                        device_mac = "".join(device["macAddress"].split(":")).lower()
                
                        if device_mac != mac and device['ipAddress'] != ip:
                            continue

                        endpoint['mac'] = mac
                        endpoint['ip'] = device['ipAddress']

                        properties = {}

                        for key, value in device.items():
                            if key in viakoo_library.FIELD_RESOLVE_MAP:
                                properties[viakoo_library.FIELD_RESOLVE_MAP[key]] = value

                        endpoint['properties'] = properties
                        
                        #Break out of the for loop once we have the info
                        break

                logging.debug(endpoint)

                response = endpoint
            else:
                response["error"] = message_info['response']
    else:
        response["error"] = "No mac address to query the endpoint for."
else:
    response["error"] = "Unauthorized"