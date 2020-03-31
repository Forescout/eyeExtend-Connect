# Sample connect resolve scrip in simplest form
import uuid
import json
import urllib.request, urllib.error, urllib.parse
# import logging so that we can log to the python server at /usr/local/forescout/plugin/connect/python_logs
import logging

logging.info("=======>>>>>Starting m3sp action Script.")

# CT will provide a params{} dictionary with the dependent properties you defined in 'properties.conf' for each of your App's custom properties.
logging.info("=======>>>>>m3sp: parameters supplied by CT: {}".format(params))

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

# ----   ACTION ----
device_info = {
    'malware_name' : params["connect_m3sp_malware_name"],
    'department' : params["connect_m3sp_malware_filetype"]
    }

response = {}

try:
    request = urllib.request.Request(base_url + '/api/senddata', headers=device_headers, data=bytes(json.dumps(device_info), encoding="utf-8"))
    resp = urllib.request.urlopen(request)
    request_response = json.loads(resp.read())
    if resp.getcode() == 200:
        response['succeeded'] = True
    else:
        response['succeeded'] = False
except:
    response['succeeded'] = False
    logging.info("=======>>>>>Error sending data, server reurned: " + resp.getcode())

logging.info("=======>>>>>Ending m3sp action Script.: {}".format(response))
