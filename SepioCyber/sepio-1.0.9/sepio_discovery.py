import hashlib
import logging
import requests
import time
from requests.exceptions import HTTPError, SSLError, RequestException
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logging.info("Sepio Discovery Script Started")

base_url = params['connect_sepio_url'].strip()

if not base_url.startswith('http://') and not base_url.startswith('https://'):
    base_url = 'https://' + base_url

if not base_url.endswith('/prime/webui/Auth/LocalLogin'):
     SEPIO_API_AUTH_URL = f"{base_url.rstrip('/')}/prime/webui/Auth/LocalLogin"
else:
    SEPIO_API_AUTH_URL = base_url

logging.info(f'Sepio URL: {SEPIO_API_AUTH_URL}')

parsed_url = urlparse(SEPIO_API_AUTH_URL)
hostname = parsed_url.hostname
protocol = parsed_url.scheme

SEPIO_ASSETS_API_URL = f'{protocol}://{hostname}/sepio-data'
PAGE_SIZE = int(params['connect_sepio_records_per_page'])
WAIT_TIME = int(params['connect_sepio_wait_time']) 
SEPIO_API_USERNAME = params['connect_sepio_username']
SEPIO_API_PASSWORD = params['connect_sepio_password']
DORMANT_DEVICE_CREATION = params['connect_sepio_dormant']
POTENTIAL_UNMANAGED_SWITCH = params['connect_sepio_potential_unmanaged_switch']
ASSETS_QUERY = """
query GetDiscoveredAssets($pageNum: Int!, $pageSize: Int!) {
  conditionalTable(
    query: {
      filters: [
        {
          index: 0
          field: "riskLevel"
          expression: "Exact"
          value: "2,3,4,5,6,7,8,9"
          op: "AND"
          conditionTypeValue: "multiple"
          is_userattribute: false
        }
      ]
      systemFilters: [
        {
          index: 0
          field: "icon"
          expression: "NotExact"
          value: "50"
          op: "AND"
          conditionTypeValue: "multiple"
        }
        {
          index: 1
          field: "type"
          expression: "NotExact"
          value: "6"
          op: "AND"
          conditionTypeValue: "multiple"
        }
        {
          index: 2
          field: "hierarchy"
          expression: "NotExact"
          value: "1"
          op: "AND"
          conditionTypeValue: "multiple"
        }
      ]
      globalSearch: ""
    }
    pagination: { pageNumber: $pageNum, pageSize: $pageSize, sortBy: "riskLevel_desc" }
  ) {
    data {
      id
      mac
      key
      model
      iconDescription
      isOnline
      type
      locations {
        displayString
      }
      indicatorViewDetails {
        subType
        riskIndicationString
        description
        risk
      }
    }
  }
}
"""

subtype = {
    'connect_sepio_potential_unmanaged_switch': 'Potential Unmanaged Switch',
    'connect_sepio_active_network_threat': 'Active Network Threat',
    'connect_sepio_inactive_network_threat': 'Inactive Network Threat',
    'connect_sepio_communication_anomaly': 'Communication Anomaly',
    'connect_sepio_dna_anomaly': 'Asset DNA Anomaly',
    'connect_sepio_reputation': 'Bad Reputation',
    'connect_sepio_common_vulnerabilities': 'Common Vulnerabilities and Exposures (CVE)',
    'connect_sepio_extended_idleness': 'Extended Idleness',
    'connect_sepio_low_speed': 'Low Speed On High Speed Port',
    'connect_sepio_rare_device': 'Rare Device',
    'connect_sepio_risky_child_connected': 'Risky Child Connected',
    'connect_sepio_unexpected_speed': 'Unexpected speed',
    'connect_sepio_unsupervised_host': 'Unsupervised Host',
    'connect_sepio_unsupervised_network_infrastructure': 'Unsupervised Network Infrastructure'
}

# Array containing subtype filter criteria
subtype_filter = []
# Check which params are set to true and add to subtype_filter array
for param_key, sub_type in subtype.items():
    if params[param_key] == 'true':
        subtype_filter.append(sub_type)

logging.info(f'Sepio Asset URL: {SEPIO_ASSETS_API_URL}')
logging.info(f"Sub-indicator filter: {subtype_filter}")
logging.info(f"Dormant Device Creation is set to: {DORMANT_DEVICE_CREATION}")
logging.info(f"Connecting to: {SEPIO_API_AUTH_URL}")
logging.info(f'API Configuration - Page Size: {PAGE_SIZE}, Wait Time: {WAIT_TIME}')


# Generate MAC addresses for devices without MAC addresses using asset_id
def random_mac(asset_id, slap='6'):

    if not asset_id:
        return None
    
    # Create a hash of the asset_id
    hash_object = hashlib.sha256(asset_id.encode('utf-8'))
    hash_hex = hash_object.hexdigest()

    # Use the first 12 characters of the hash for the MAC address
    random = f"{hash_hex[:12].upper()}"

    # Apply the 'slap' character at a specific position 2 it will pass the 6
    random = random[:1] + slap + random[2:]

    return random



def fetch_sepio_token():
    headers = {'Content-Type': 'application/json'}
    body = {"username": SEPIO_API_USERNAME, "password": SEPIO_API_PASSWORD}

    try:
        logging.info(f'SSL verification is set to: {ssl_verify}')

        response = requests.post(SEPIO_API_AUTH_URL, headers=headers, json=body, timeout=120, verify=ssl_verify)

        if response.status_code != 200:
            logging.error(f"Response headers: {dict(response.headers)}")

            # Parse and log the response body
            try:
                logging.error(f'Response body: {response.json()}')
            except ValueError:
                logging.error(f'Response text: {response.text}')


        response.raise_for_status()
        response_data = response.json()
        token = response_data.get('token')
        expiresAtstr = response_data.get('expiresAt')

        if not token:
            logging.error('Token was not found in the response.')
            return None
        
        # Parse the token expiration to determine when a renewal is required
        try:
            if 'Z' in expiresAtstr:
                expiresAt = datetime.strptime(expiresAtstr, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            else:
                expiresAt = datetime.fromisoformat(expiresAtstr).astimezone(timezone.utc)
        except Exception as e:
            logging.error(f'Error parsing expiresAt: {e}')
            expiresAt = datetime.now(timezone.utc) + timedelta(minutes=15)

        logging.info(f'Token expires at: {expiresAt}')
        
        return token, expiresAt
        
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except SSLError as ssl_err:
        logging.error(f"SSL error occurred: {ssl_err}")
    except RequestException as req_err:
        logging.error(f"Error occurred: {req_err}")
    except Exception as err:
        logging.error(f"An unexpected error occurred: {err}")
    return None

def fetch_assets_data(token, expiresAt):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    all_assets = []
    page_number = 1
    allowed_types = {2, 3, 8, 9, 10}
    assets_added = 0

    # Iteration through pages to retrieve all filtered assets
    while True:

        # Check if the token will expire within 5 minutes and trigger renewal if needed
        now = datetime.now(timezone.utc)
        if expiresAt - now < timedelta(minutes=5):
            logging.info(f'Token is expiring soon (in less than 5 minutes). Triggering refresh.')
            new_token, new_expiresAt = fetch_sepio_token()
            if new_token:
                token = new_token
                expiresAt = new_expiresAt
                headers['Authorization'] = f'Bearer {token}'
                logging.info('Token refreshed successfully')
            else:
                logging.info('Failed to fetch new token')
        
        variables = {
            "pageNum": page_number,
            "pageSize": PAGE_SIZE
        }

        payload = {
            "operationName": "GetDiscoveredAssets",
            "variables": variables,
            "query": ASSETS_QUERY
        }

        try:

            for attempt in range(3):
                logging.info(f'SSL verification is set to: {ssl_verify}')

                try:
                    response = requests.post(SEPIO_ASSETS_API_URL, headers=headers, json=payload, timeout=120, verify=ssl_verify)

                except requests.RequestException as e:
                    logging.error(f"Network error on attempt {attempt + 1}: {e}")
                    time.sleep(1)
                    continue

                logging.info(f"Response status: {response.status_code}, Page: {page_number}, Page Size: {PAGE_SIZE}")
                # logging.info(f"Response headers: {dict(response.headers)}")

                if response.status_code == 200:
                    break

                logging.info(f"Attempt {attempt + 1} failed. Retrying in 1s")
                logging.error(f"Response headers: {dict(response.headers)}")
                
                # Parse and log the response body
                try:
                    logging.error(f'Response body: {response.json()}')
                except ValueError:
                    logging.error(f'Response text: {response.text}')

                time.sleep(1);
            else:
                logging.error("Failed to get 200 response after 3 attempts. Stopping.")
                break


            response.raise_for_status()
            response_data = response.json()

            # Validate JSON structure
            if 'data' in response_data:

                conditional_table = response_data.get('data', {}).get('conditionalTable', {})
                assets_on_page = conditional_table.get('data', [])
                
                # If no assets are found on the current page, end the pagination loop
                if not assets_on_page:
                    logging.info(f"No assets found on page {page_number}. Ending pagination.")
                    break

                # Process each asset on the current page
                for item in assets_on_page:
                    real_mac = item.get('mac').lower()
                    asset_id = item.get('id')
                    key = item.get('key')
                    model = item.get('model')
                    iconDescription = item.get('iconDescription')
                    is_online = item.get('isOnline')
                    types = item.get('type')

                    if DORMANT_DEVICE_CREATION == "false" and real_mac.lower() == "dormant device":
                        logging.debug(f"Skipping dormant device: {asset_id}")
                        continue
                    
                    # Filter out assets that don't have the allowed types
                    if types not in allowed_types:
                        # logging.info(f"Skipping asset with ID {asset_id} due to disallowed type: {type}")
                        continue
                    
                    # Skip if the device dont have a MAC and is_online: false
                    if not real_mac and not is_online:
                        # logging.info(f"Skipping device with asset_id {asset_id}, it is offline and has no MAC address. {is_online}")
                        continue

                    if real_mac.lower() == "dormant device" or not real_mac:
                        random_macs = random_mac(asset_id).lower()
                            # logging.info(f"Generated real_mac for {asset_id}: {random_macs}")
                    else:
                        random_macs = ""


                    risk_score = None
                    description = ""
                    subIndicationString = ""
                    riskIndicationString = ""
                    displayString = ""

                    # Check if indicatorViewDetails exists and is a list
                    if 'indicatorViewDetails' in item and isinstance(item['indicatorViewDetails'], list):
                            if len(item['indicatorViewDetails']) == 0 and real_mac and real_mac.lower() != "dormant device":
                                # logging.info(
                                #     f"Skipping asset with ID {asset_id} because 'indicatorViewDetails' is empty and it has a real_mac.")
                                continue

                            # If indicatorViewDetails has items, collect all 'riskIndicationString' values
                            elif len(item['indicatorViewDetails']) > 0:
                                # Extract and join all 'riskIndicationString' values with a comma separator
                                riskIndicationStrings = [
                                    detail.get('riskIndicationString', '')
                                    for detail in item['indicatorViewDetails']
                                    if detail.get('riskIndicationString')
                                ]

                                # Join the list into a single string
                                riskIndicationString = ", ".join(riskIndicationStrings)

                                # Retrieve other details from the first element

                                risk_details = item['indicatorViewDetails'][0]
                                risk_score = risk_details.get('risk', None)

                                if not isinstance(risk_score, int):
                                   logging.info(f"Invalid risk score type {type(risk_score)} for asset {asset_id}")


                                subDescription = [
                                info.get('description') for info in item.get('indicatorViewDetails', [])
                                if 'description' in info
                                    ]
                                
                                description = ",".join(subDescription) if subDescription else ""

                                subIndication = [
                                info.get('subType') for info in item.get('indicatorViewDetails', [])
                                if 'subType' in info
                                    ]

                                subIndicationString = ",".join(subIndication) if subIndication else ""

                                contains_potential_unmanaged_switch = any(
                                    datas.get('subType') == "Potential Unmanaged Switch"
                                    for datas in item['indicatorViewDetails']
                                )

                                if random_macs and real_mac.lower() != "dormant device":
                                    if POTENTIAL_UNMANAGED_SWITCH == 'false':
                                        logging.info(f"Potential Unmanaged Switch is false")
                                        continue
                                    elif POTENTIAL_UNMANAGED_SWITCH == 'true' and not contains_potential_unmanaged_switch:
                                        logging.info(f'Skipping no Potential Unmanaged Switch found')
                                        continue

                                
                                contains_subtype_filter = any(
                                    datas.get('subType') in subtype_filter
                                    for datas in item['indicatorViewDetails']
                                )

 
                                # Skip the asset if it has a MAC address but no relevant indications
                                if real_mac and real_mac.lower() != "dormant device" and (not subtype_filter or not contains_subtype_filter):
                                    # logging.info(
                                    #     f"Skipping asset with ID {asset_id} as it has a MAC address but no threat or DNA anomaly indication."
                                    # )
                                    continue

                    else:
                            logging.info(f"No 'indicatorViewDetails' or unexpected format for asset ID {asset_id}")

                    display_string = [
                            loc.get('displayString') for loc in item.get('locations', [])
                            if 'displayString' in loc
                        ]

                    displayString = ",".join(display_string) if display_string else ""

                    # Create the asset dictionary and add it to the list
                    asset = {
                        'mac': random_macs,
                        'real_mac': real_mac,
                        'key': key,
                        'model': model,
                        'risk': risk_score,
                        'description': description,
                        'subIndicationString': subIndicationString,
                        'riskIndicationString': riskIndicationString,
                        'iconDescription': iconDescription,
                        'displayString': displayString                     
                    }

                    logging.debug(f"MAC Addresses - Real: {asset['real_mac']} | Random: {asset['mac']}")

                    assets_added += 1
                    
                    all_assets.append(asset)

                # Wait time between API page requests 
                if WAIT_TIME > 0 and WAIT_TIME <= 120000:
                    # Convert milliseconds to seconds
                    seconds = WAIT_TIME / 1000
                    logging.info(f"Waiting {seconds} seconds ({WAIT_TIME} milliseconds) before next page request")
                    time.sleep(seconds)

                # Move to the next page
                page_number += 1

            else:
                logging.error("No 'data' found in the response.")
                break

        except HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            break
        except SSLError as ssl_err:
            logging.error(f"SSL error occurred: {ssl_err}")
            break
        except RequestException as req_err:
            logging.error(f"Error occurred: {req_err}")
            break
        except Exception as err:
            logging.error(f"An unexpected error occurred: {err}")
            break

    logging.info(f"Total assets processed: {assets_added}")

    return all_assets


token, expiresAt = fetch_sepio_token()

if token:
    assets = fetch_assets_data(token, expiresAt)
    logging.info(f'Number of assets: {len(assets)}')
else:
    logging.error("Failed to retrieve authentication token")

     
response = {"endpoints": []}
try:
   
                for asset in assets:
                    random_macs = asset['mac']
                    real_mac = asset['real_mac']
                    key = asset.get('key')
                    model = asset.get('model')
                    risk = asset.get('risk')
                    description = asset.get('description')
                    subIndicationString = asset.get('subIndicationString')
                    riskIndicationString = asset.get('riskIndicationString')
                    iconDescription = asset.get('iconDescription')
                    displayString = asset.get('displayString')

                    # Create current time in GMT and convert it to a UNIX timestamp
                    current_time_gmt = datetime.now(timezone.utc)
                    timestamp = str(int(current_time_gmt.timestamp()))


                    if real_mac and real_mac.lower() != "dormant device":
                     # Use the real_mac if it exists and is not "Dormant Device"
                     mac = {"mac": real_mac}
                     mac_field = {}  # Do not set `connect_sepio_macrandom` if real MAC is present
                    else:
                         # Use random_macs if real_mac is missing or is "Dormant Device"
                        mac = {"mac": random_macs}
                        mac_field = {"connect_sepio_macrandom": random_macs}

                                            
                    endpoint = {
                       **mac,
                       "properties": {
                       "connect_sepio_department": "Sepio",
                       **mac_field,
                       "connect_sepio_asset_id": key,
                       "connect_sepio_model": model,
                       **({"connect_sepio_riskscore": risk} if risk is not None else {}),
                       "connect_sepio_description": description, 
                       "connect_sepio_subindicationstring": subIndicationString, 
                       "connect_sepio_riskindicationstring": riskIndicationString, 
                       "connect_sepio_classification": iconDescription, 
                       "connect_sepio_locations": displayString, 
                       "connect_sepio_timestamp": timestamp 
                       }
                     }
                    
                                       
                    response['endpoints'].append(endpoint)

                    logging.debug(f"Exporting assets: {endpoint}")
        

except Exception as e:
    response["error"] = "Could not retrieve endpoints."
    logging.error(f"Error occurred while processing assets: {str(e)}")

logging.info("Assets processing completed.")


