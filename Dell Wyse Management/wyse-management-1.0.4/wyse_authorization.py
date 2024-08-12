import requests
import logging

logging.info('===>Starting Wyse Management Studio Authorization Script')

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params.get("connect_dellwysemanagementsuite_url")
baseURI = url + "/wms-api"
user = params.get("connect_dellwysemanagementsuite_username")
password = params.get("connect_dellwysemanagementsuite_password")

# ***** START - AUTH API CONFIGURATION ***** #
url = f"{baseURI}/wms/v1/SessionService/Sessions"
payload={
    "UserName": user,
    "Password": password
}

#initialize response
response = {}

# Make the API Call
try:
    # Make the API Call
    resp = requests.post(url, json=payload, verify=ssl_verify)

    # Return the 'response' dictionary, must have a 'succeded' field.

    if resp is None:
        response['succeeded'] = False
        response['result_msg'] = 'No response from Wyse Management Studio Service.'
    elif resp.status_code == 201 or resp.status_code == 204:
        response['succeeded'] = True
        response["token"] = resp.headers["X-Auth-Token"]
        response['result_msg'] = f'Successfully connected to Wyse Management Studio and acquired auth token: {resp.headers["X-Auth-Token"][:5]}...'
    elif resp.status_code == 406:
        response['succeeded'] = False
        response['error'] = f'Error Code {resp.status_code} received from Wyse Management Studio Service. Please check credentials!'
        logging.debug(resp.content)
    elif resp.status_code == 503:
        response['succeeded'] = False
        response['error'] = f'Error Code {resp.status_code} received from Wyse Management Studio Service. Is the Wyse API enabled?'
        logging.debug(resp.content)
    else:
        response['succeeded'] = False
        response['error'] = f'Error Code {resp.status_code} received from Wyse Management Studio Service.'
        logging.debug(resp.content)

except Exception as e:
    response['succeeded'] = False
    response['token'] = ''
    response['error'] = "Could not connect to Wyse Management Suite. Exception: " + str(e)
    response['result_msg'] = "Could not connect to Wyse Management Suite. Exception: " + str(e)

# logging response for debugging purposes - you might disable this option later.
# logging.debug(f'Authorization Script Returned Response: {response}')
logging.info('===>Ending Wyse Management Suite Authorization Script')