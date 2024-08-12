import json
import requests
import logging

logging.info('===>Starting Dell Wyse Management Suite Test Script')

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params.get("connect_dellwysemanagementsuite_url")
baseURI = url + "/wms-api"
user = params.get("connect_dellwysemanagementsuite_username")
password = params.get("connect_dellwysemanagementsuite_password")


# ***** START - AUTH API CONFIGURATION ***** #
auth_url = f"{baseURI}/wms/v1/SessionService/Sessions"
payload={
    "UserName": user,
    "Password": password
}

#initialize response
response = {}

# Make the API Call
try:
    # Make the API Call
    resp = requests.post(auth_url, json=payload, verify=ssl_verify)

    # Return the 'response' dictionary, must have a 'succeded' field.

    if resp is None:
        response['succeeded'] = False
        response['result_msg'] = 'No response from Wyse Management Suite Service.'
    elif resp.status_code == 200 or resp.status_code == 201:
        logging.debug("Succesfully authenticated to Wyse Management Suite")
        # Try making device inventory list request
        token = resp.headers["X-Auth-Token"]
        api_request_url = f"{baseURI}/wms/v1/Systems?$filter = status eq 'Online'"
        systems = requests.get(api_request_url, headers={'X-Auth-Token': token}, verify=ssl_verify)
        if(systems.status_code == 200):
            response_json = systems.json()
            logging.debug(json.dumps(response_json))
            response['succeeded'] = True
            response['result_msg'] = 'Successfully connected and queried Wyse Management Suite.'
        else:
            response['succeeded'] = False
            response['error'] = f'Error Code {systems.status_code} received from Wyse Management Suite Service on Systems List Call. Please check credentials!'
            logging.debug(systems.content)
    elif resp.status_code == 406:
        response['succeeded'] = False
        response['error'] = f'Error Code {resp.status_code} received from Wyse Management Suite Service. Please check credentials!'
        logging.debug(resp.content)
    elif resp.status_code == 503:
        response['succeeded'] = False
        response['error'] = f'Error Code {resp.status_code} received from Wyse Management Suite Service. Is the Wyse API enabled?'
        logging.debug(resp.content)
    else:
        response['succeeded'] = False
        response['error'] = f'Error Code {resp.status_code} received from Wyse Management Suite Service.'
        logging.debug(resp.content)

except Exception as e:
    response['succeeded'] = False
    response['error'] = "Could not connect to Wyse Management Suite. Exception: " + str(e)
    response['result_msg'] = "Could not connect to Wyse Management Suite. Exception: " + str(e)

logging.debug(response)
logging.info('===>Ending Wyse Management Suite Test Script')