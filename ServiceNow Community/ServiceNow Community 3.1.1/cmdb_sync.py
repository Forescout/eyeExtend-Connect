import requests
import logging

snow_to_ct_props_map = {
    "tag": "connect_servicenowonboarding_tag",
    "serial": "connect_servicenowonboarding_serial",
    "status": "connect_servicenowonboarding_status"

}

# Server configuration fields will be available in the 'params' dictionary.
SNOW_HOSTNAME = params.get("connect_servicenowonboarding_snowinstance")  # ServiceNow API URL
SNOW_USERNAME = params.get("connect_servicenowonboarding_snowuserid")  # ServiceNow API UserID
SNOW_PASSWORD = params.get("connect_servicenowonboarding_snowpassword")  # ServiceNow API Password
SNOW_TABLE = params.get("connect_servicenowonboarding_snowtable")  # ServiceNow CI Table
SNOW_FILTER = params.get("connect_servicenowonboarding_installedonly")  # Filter on CI Install Status

SNOW_URL = f"https://{SNOW_HOSTNAME}/api/now/table/{SNOW_TABLE}"

response = {}
endpoints = []

# Headers
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Determine the query parameters
PARAMS = {
    "sysparm_fields": "mac_address,serial_number,category,install_status,asset_tag",
    "sysparm_limit": 100,  # Set limit to handle pagination
    "sysparm_offset": 0  # Start from the first record
}

if SNOW_FILTER == 'true':
    PARAMS["sysparm_query"] = "mac_addressISNOTEMPTY^serial_numberISNOTEMPTY^install_status=1^asset_tagISNOTEMPTY"
else:
    PARAMS["sysparm_query"] = "mac_addressISNOTEMPTY^serial_numberISNOTEMPTY^install_statusISNOTEMPTY^asset_tagISNOTEMPTY"

# Retrieve all records using pagination
all_records = []
while True:
    resp_snow = requests.get(SNOW_URL, auth=(SNOW_USERNAME, SNOW_PASSWORD), headers=HEADERS, params=PARAMS)
    
    if resp_snow.status_code != 200:
        logging.error("Error retrieving data from ServiceNow: %s", resp_snow.text)
        response['succeeded'] = False
        response["error"] = "Could not authenticate with ServiceNow"
        break
    
    data = resp_snow.json()
    records = data.get("result", [])
    
    if not records:
        break  # No more records to fetch
    
    all_records.extend(records)
    PARAMS["sysparm_offset"] += len(records)  # Move to the next batch

# Process all records
for record in all_records:
    
    mac_address = record.get('mac_address', 'N/A')
    mac_address = mac_address.replace(":", "").lower()
    serial_number = record.get('serial_number', 'N/A')
    install_status = record.get('install_status', 'N/A')
    asset_tag = record.get('asset_tag', 'N/A')

    new_endpoint = {}
    properties = {}
    properties["connect_servicenowonboarding_serial"] = serial_number
    properties["connect_servicenowonboarding_tag"] = asset_tag
    properties["connect_servicenowonboarding_status"] = install_status

    new_endpoint["mac"] = mac_address
    new_endpoint["properties"] = properties

    endpoints.append(new_endpoint)
    logging.debug(f"The endpoint data: {endpoints}")
response["endpoints"] = endpoints

