import requests
import logging


logging.info('===>Starting Dell Wyse Management Suite Action Script: Shutdown')

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params.get("connect_dellwysemanagementsuite_url", '')
token = params.get('connect_authorization_token', '')
id = params.get('connect_dellwysemanagementsuite_id', None)

# ***** START - AUTH API CONFIGURATION ***** #
api_request_url = f"{url}/wms-api/wms/v1/Systems/{id}/Actions/Oem/DellWyse.Shutdown"
headers = {
  'X-Auth-Token': f'{token}'
}

#initialize response
response = {}

# Make the API Call
if id:
    try:
        # Make the API Call
        resp = requests.post(api_request_url, verify=ssl_verify)

        # Return the 'response' dictionary, must have a 'succeded' field.

        if resp is None:
            response['succeeded'] = False
            response['troubleshooting'] = 'No response from Wyse Management Studio Service.'
        elif resp.status_code == 200 or resp.status_code == 204:
            response['succeeded'] = True
            # response['troubleshooting'] = 'Successfully requested device shutdown to Wyse Management Studio.'
        else:
            response['succeeded'] = False
            response['troubleshooting'] = f'Error Code {resp.status_code} received from Wyse Management Studio Service.'
            logging.debug(resp.content)

    except Exception as e:
        response['succeeded'] = False
        response['troubleshooting'] = "Could not connect to Wyse Management Suite. Exception: " + str(e)
else:
    response['succeeded'] = False
    response['troubleshooting'] = 'No Dell Wyse Management Studio ID found! Has this device been discovered by the Connect App?'

logging.debug(response)
logging.info('===>Ending Wyse Management Action Script: Shutdown')