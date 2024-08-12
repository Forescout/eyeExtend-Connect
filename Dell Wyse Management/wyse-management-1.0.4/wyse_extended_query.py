import requests
import json
from datetime import datetime
import logging
import math


# CONFIGURATION
logging.info('===>Starting Wyse Management Suite Extended Property Resolve Script for Host')

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params.get("connect_dellwysemanagementsuite_url", '')
token = params.get('connect_authorization_token', '')
id = params.get('connect_dellwysemanagementsuite_id', '')

# ***** START - AUTH API CONFIGURATION ***** #
headers = { 'X-Auth-Token': f'{token}' }

#initialize response 
response = {
    "properties": {
         "connect_dellwysemanagementsuite_device_details_extended": {},
         "connect_dellwysemanagementsuite_device_details_extended_status": {}
    }
}

# Make API Call
try:
    logging.debug(f'Requesting extended data for ID: {id}')
    api_request_url = f"{url}/wms-api/wms/v1/Systems/{id}"
    resp = requests.get(api_request_url, headers=headers, verify=ssl_verify)
    if(resp.status_code == 200):
        response_json = resp.json()
        logging.debug(json.dumps(response_json))

        # Process host data
        response['properties']['connect_dellwysemanagementsuite_device_details_extended'] = {
                "power_state": response_json.get("PowerState", 'Unknown'),
                "name": response_json.get("Name", ''),
                "manufacturer": response_json.get("Manufacturer", ''),
                "id": response_json.get("Id", ''),
                "description": response_json.get("Description", ''),
                "bios_version": response_json.get("BiosVersion", '')
        }

        # Set online status if we have affirmative status to use
        if("PowerState" in response_json):
            if(response_json.get("PowerState", 'Unknown') == "On"):
                response['properties']["online"] = True
            else:
                response['properties']["online"] = False
        
        # Process status data
        if("Status" in response_json):
            response['properties']['connect_dellwysemanagementsuite_device_details_extended_status'] = {
                "health": response_json["Status"].get('Health', ''),
                "health_rollup": response_json["Status"].get('HealthRollup', ''),
                "state": response_json["Status"].get('State', '')
            }

        # Update last check in time if Oem data if present
        #if("Oem" in response_json):
        #    if("Dell_Device_Summary" in response_json["Oem"]):
        #        if("LastCheckin" in response_json["Oem"]["Dell_Device_Summary"]):
        #            response['properties']['connect_dellwysemanagementsuite_extended_last_check_in'] = math.floor(datetime.strptime(response_json["Oem"]["Dell_Device_Summary"]['LastCheckin'], "%a %b %d %H:%M:%S %Z %Y").timestamp())

    else:
        response['error'] = "Non-200 API Status code received. Error: " + json.dumps(resp.json())
        logging.error("Non-200 API Status code received. Error: " + json.dumps(resp.json()))

except Exception as e:
        response['error'] = f'Error request: {str(e)}'
        logging.error(f'Error request: {str(e)}')

logging.info('===>Ending Wyse Management Suite Extended Property Resolve Script for Host')
logging.debug(json.dumps(response))