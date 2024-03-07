from base64 import b64encode
import requests
import logging
import json

logging.info('===>Starting netskope Poll Script')
logging.debug('Params for Poll Script:')
logging.debug(params)

# Input Params
url = params.get("connect_netskope_url", '').strip()
if url.endswith('/'):
    Base_URL = f'{url}api/v1/clients'
else:
    Base_URL = f'{url}/api/v1/clients'

token = params.get("connect_netskope_token", '')
query = "host_info"

proxy_ip = params.get("connect_proxy_ip", '')
proxy_port = params.get("connect_proxy_port", '')
proxy_username = params.get("connect_proxy_username", '')
proxy_password = params.get("connect_proxy_password", '')

netskope_to_ct_props_map = {
    "client_version": "connect_netskope_client_version",
    "device_id": "connect_netskope_device_id",
    "device_make": "connect_netskope_device_make",
    "device_model": "connect_netskope_device_model",
    "hostname": "connect_netskope_hostname",
    "last_hostinfo_update_timestamp": "connect_netskope_last_hostinfo_update_timestamp",
    "managementid": "connect_netskope_managementid",
    "migrated_revision": "connect_netskope_migrated_revision",
    "nsdeviceuid": "connect_netskope_nsdeviceuid",
    "os": "connect_netskope_os",
    "os_version": "connect_netskope_os_version",
    "serialnumber": "connect_netskope_serialnumber",
    "npa_status": "connect_netskope_npa_status",
    "service_name": "connect_netskope_service_name",
    "status": "connect_netskope_status",
    "last_event_timestamp": "connect_netskope_last_event_timestamp",
    "users": {
        'username': 'connect_netskope_username',
        'device_classification_status': 'connect_netskope_device_classification_status'
    }
}

response = {}

# Construct the query parameters
params = {'token': token, 'query': query}

# Make a GET request to the API endpoint, passing the query parameters
result = requests.get(Base_URL, params=params)

#if result.status_code == 200:
result = result.json()

macAddresses = list()

for device in result.get('data', []):
    # Extract the list of MAC addresses for the current device
    macAddresses.append(device.get('attributes', {}).get('host_info', {}).get('macAddresses'))

logging.info(f'check 0: Result JSON and macAddress: {result}\n*****\n{macAddresses}')

response = {}

try:
    endpoints = []

    # Make a GET request to the API endpoint, passing the query parameters
    result = requests.get(Base_URL, params=params)

    if result.status_code == 200:
        result = result.json()
        logging.info(f'check 1: Result JSON: {result}')

        for device in result.get('data', []):
            # Extract the relevant information for each device
            attributes = device.get('attributes', {})
            host_info = attributes.get('host_info', {})
            mac_addresses = host_info.get('macAddresses', [])
            if mac_addresses:
                # Select the first MAC address from the list
                mac_address = mac_addresses[0]
                endpoint = {}
                endpoint['mac'] = mac_address.replace(':', '').lower()  # Remove colons from MAC address
                #endpoint['ip'] = ''  # You need to find a way to obtain the IP address
                properties = {}
                properties["connect_netskope_client_version"] = attributes.get("client_version", "")
                properties["connect_netskope_device_id"] = attributes.get("device_id", "")
                properties["connect_netskope_device_make"] = host_info.get("device_make", "")
                properties["connect_netskope_device_model"] = host_info.get("device_model", "")
                properties["connect_netskope_hostname"] = host_info.get("hostname", "")
                properties["connect_netskope_last_hostinfo_update_timestamp"] = host_info.get("last_hostinfo_update_timestamp", "")
                properties["connect_netskope_managementid"] = host_info.get("managementID", "")
                properties["connect_netskope_migrated_revision"] = attributes.get("migrated_revision", "")
                properties["connect_netskope_nsdeviceuid"] = host_info.get("nsdeviceuid", "")
                properties["connect_netskope_os"] = host_info.get("os", "")
                properties["connect_netskope_os_version"] = host_info.get("os_version", "")
                properties["connect_netskope_serialnumber"] = host_info.get("serialNumber", "")
                properties["connect_netskope_npa_status"] = attributes.get("last_event", {}).get("npa_status", "")
                properties["connect_netskope_service_name"] = attributes.get("last_event_service_name", "")
                properties["connect_netskope_status"] = attributes.get("last_event", {}).get("status_v2", "")
                properties["connect_netskope_last_event_timestamp"] = attributes.get("last_event", {}).get("timestamp", "")
                # Assuming there's only one user, you may need to adjust this part if there are multiple users
                if host_info.get('users'):
                    user = host_info['users'][0]
                    properties["connect_netskope_users"] = {
                        'username': user.get('username', ''),
                        'device_classification_status': user.get('device_classification_status', '')
                    }
                endpoint['properties'] = properties
                endpoints.append(endpoint)

    response['endpoints'] = endpoints
    
    logging.info(f'check 2: Response JSON: {response}')

except Exception as e:
    response['error'] = f'Error Exception happened while requesting Netskope API: {str(e)}'

logging.info(f'Final: Response JSON: {response}')
logging.info(f'Response: {response}')
logging.info('===>Ending Netskope Poll Script')

