import requests
import logging


logging.info('===>Starting Dell Wyse Management Suite Action Script: Send Message')

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params.get("connect_dellwysemanagementsuite_url", '')
token = params.get('connect_authorization_token', '')
id = params.get('connect_dellwysemanagementsuite_id', None)
message = params.get('connect_dellwysemanagementsuite_message', None)

# ***** START - AUTH API CONFIGURATION ***** #
api_request_url = f"{url}/wms-api/wms/v1/Systems/{id}/Actions/Oem/DellWyse.SendMessage"
headers = {
  'X-Auth-Token': f'{token}'
}
payload = {
 "@odata.id": "/wms-api/wms/v1/Systems/1/Actions/Oem/SendMessageActionInfo",
 "@odata.type": "#ActionInfo.v1_0_6.ActionInfo",
 "Id": "SendMessageActionInfo",
 "Name": "Dell Wyse Send Message Action Info",
 "Parameters": [
        {
            "Name": "Message",
            "Required": True,
            "DataType": "String",
            "AllowableValues": [
                message
            ]
        }
    ]
}

#initialize response
response = {}

# Make the API Call
if id and message:
    try:
        # Make the API Call
        resp = requests.post(api_request_url, json=payload, verify=ssl_verify)

        # Return the 'response' dictionary, must have a 'succeded' field.

        if resp is None:
            response['succeeded'] = False
            response['troubleshooting'] = 'No response from Wyse Management Studio Service.'
        elif resp.status_code == 200 or resp.status_code == 204:
            response['succeeded'] = True
            # response['troubleshooting'] = 'Successfully sent message via Wyse Management Studio.'
        else:
            response['succeeded'] = False
            response['troubleshooting'] = f'Error Code {resp.status_code} received from Wyse Management Studio Service.'
            logging.debug(resp.content)

    except Exception as e:
        response['succeeded'] = False
        response['troubleshooting'] = "Could not connect to Wyse Management Suite. Exception: " + str(e)
else:
    response['succeeded'] = False
    response['troubleshooting'] = 'No Dell Wyse Management Studio ID or message provided! Has this device been discovered by the Connect App? Did you enter a message?'

logging.debug(response)
logging.info('===>Ending Wyse Management Action Script: Send Message')