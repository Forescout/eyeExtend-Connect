# Test script for CounterACT
import logging
import requests

logging.info('===>Starting ServiceNow Onboarding Test Script')

# Server configuration fields will be available in the 'params' dictionary.
SNOW_HOSTNAME = params.get("connect_servicenowonboarding_snowinstance")  # Service Now API URL
SNOW_USERNAME = params.get("connect_servicenowonboarding_snowuserid")  # Service Now API UserID
SNOW_PASSWORD = params.get("connect_servicenowonboarding_snowpassword")  # Service Now API Password
SNOW_TABLE = params.get("connect_servicenowonboarding_snowtable")  # Service Now CI Table
SNOW_URL = f"https://{SNOW_HOSTNAME}/api/now/table/{SNOW_TABLE}"
FORESCOUT_USERNAME = params.get("connect_servicenowonboarding_dex_userid")  # FS DEX Username
FORESCOUT_ACCOUNT = params.get("connect_servicenowonboarding_dex_account")  # FS DEX Account Name
FORESCOUT_DEX_USERNAME = f"{FORESCOUT_USERNAME}@{FORESCOUT_ACCOUNT}"  # FS DEX Username
FORESCOUT_PASSWORD = params.get("connect_servicenowonboarding_dex_password")  # FS DEX Password
FORESCOUT_DEX_EM = params.get("connect_servicenowonboarding_dex_em")  # FS DEX url
FORESCOUT_API_URL_COMPLETE = f"https://{FORESCOUT_DEX_EM}/fsapi/niCore/Lists"



# Headers
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Query Parameters (Adjust as needed)
PARAMS = {
    "sysparm_fields": "mac_address,serial_number,category,install_status",
    "sysparm_query": "mac_addressISNOTEMPTY^serial_numberISNOTEMPTY^install_statusISNOTEMPTY^asset_tagISNOTEMPTY",
    "sysparm_limit": "5000"  # Adjust limit as required
}

# Make the API request
resp_snow = requests.get(SNOW_URL, auth=(SNOW_USERNAME, SNOW_PASSWORD), headers=HEADERS, params=PARAMS)

# Return the 'response' dictionary, must have a 'succeded' field.

response = {}
result = []


# Check response from ServiceNow

if resp_snow.status_code == 200:
    result.append("SNOW API Success")
else:
    result.append("SNOW Now API Failed")



# Update final test result
response["succeeded"] = True
response["result_msg"] = result
    


