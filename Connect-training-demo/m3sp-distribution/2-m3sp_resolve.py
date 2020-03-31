# Sample connect resolve scrip in simplest form
import uuid
import json
import urllib.request, urllib.error, urllib.parse
# import logging so that we can log to the python server at /usr/local/forescout/plugin/connect/python_logs
import logging

logging.info("=======>>>>>Starting m3sp resolve Script.")

# mapping between our App properties and the CT internal properties
# in this case, 'department' is returned from our remote host, and 'connect_m3sp_department' is the internal CT property name which must be unique & defined in 'properties.conf'
m3sp_to_ct_props_map = {
    "department": "connect_m3sp_department",
    "description": "connect_m3sp_description"
}

# CT will provide a params{} dictionary with the dependent properties you defined in 'properties.conf' & 'ssytem.conf' for each of your App's custom properties.
base_url = params['connect_m3sp_url']

payload = {
    'username' : params['connect_m3sp_username'],
    'password' : params['connect_m3sp_password']
    }

headers = {
    'Content-Type': "application/json",
    'charset': 'utf-8',
    'User-Agent': "FSCT/1.16.2020"
    }

# Authenticate
try:
    request = urllib.request.Request(base_url + '/api/authenticate', headers=headers, data=bytes(json.dumps(payload), encoding="utf-8"))
    resp = urllib.request.urlopen(request)
    jwt_token = json.loads(resp.read())['token']
    logging.info('=======>>>>>m3sp: Recieved Token: ' + jwt_token)
except:
    logging.info('=======>>>>>m3sp: ERROR Authenticating to Server!')

# Device headers with the authorization token
device_headers = {
    'Content-Type': "application/json",
    'charset': 'utf-8',
    'User-Agent': "FSCT/1.16.2020",
    'Authorization': 'Bearer ' + str(jwt_token)
    }

# CT will provide a params{} dictionary with the dependent properties you defined in 'properties.conf' for each of your App's custom properties.
logging.info("=======>>>>>m3sp: parameters supplied by CT: {}".format(params))

# Get info on the passed mac address from server
if "mac" in params:
    mac_addr = params["mac"]
    response = {}
    properties = {}
    logging.info("=======>>>>>m3sp: Resolving mac address: " + mac_addr)
    # Get device information
    try:
        request = urllib.request.Request(base_url + '/api/getdevice/' + mac_addr, headers=device_headers)
        resp = urllib.request.urlopen(request)
        request_response = json.loads(resp.read())
        if request_response:
            return_values = request_response[0]
            for key, value in return_values.items():
                if key in m3sp_to_ct_props_map:
                    properties[m3sp_to_ct_props_map[key]] = value
    except:
        response["error"] = "=======>>>>>m3sp: Error resolving mac address: " + mac_addr
        logging.info(response["error"])

    # All responses from scripts must contain the JSON object 'response'.
    # Host property resolve scriptswill need to populate a 'properties' JSON object within the
    # JSON object 'response'. The 'properties' object will be a key, value mapping between the CT
    # property name and the value of the property.
    response["properties"] = properties
    logging.info("=======>>>>>m3sp: response returned: {}".format(response))

else:
    response["error"] = "=======>>>>>m3sp: No mac address to query."
    logging.info(response["error"])
