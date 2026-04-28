import hashlib
import logging
import requests
import time
from requests.exceptions import HTTPError, SSLError, RequestException
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logging.info("Sepio Discovery Started")

base_url = params["connect_sepio_url"].strip()

if not base_url.startswith("http://") and not base_url.startswith("https://"):
    base_url = "https://" + base_url

if not base_url.endswith("/prime/webui/Auth/LocalLogin"):
     SEPIO_API_AUTH_URL = f"{base_url.rstrip('/')}/prime/webui/Auth/LocalLogin"
else:
    SEPIO_API_AUTH_URL = base_url

parsed_url = urlparse(SEPIO_API_AUTH_URL)
hostname = parsed_url.hostname
protocol = parsed_url.scheme

SEPIO_ASSETS_API_URL = f"{protocol}://{hostname}/sepio-data"
PAGE_SIZE = int(params["connect_sepio_records_per_page"])
WAIT_TIME = int(params["connect_sepio_wait_time"]) 
SEPIO_API_USERNAME = params["connect_sepio_username"]
SEPIO_API_PASSWORD = params["connect_sepio_password"]
DORMANT_DEVICE_CREATION = params["connect_sepio_dormant"]
POTENTIAL_UNMANAGED_SWITCH = params["connect_sepio_potential_unmanaged_switch"]
ONLINE_ONLY = params["connect_sepio_online_only"]

subtype = {
    "connect_sepio_potential_unmanaged_switch": "Potential Unmanaged Switch",
    "connect_sepio_active_network_threat": "Active Network Threat",
    "connect_sepio_inactive_network_threat": "Inactive Network Threat",
    "connect_sepio_communication_anomaly": "Communication Anomaly",
    "connect_sepio_dna_anomaly": "Asset DNA Anomaly",
    "connect_sepio_reputation": "Bad Reputation",
    "connect_sepio_common_vulnerabilities": "Common Vulnerabilities and Exposures (CVE)",
    "connect_sepio_extended_idleness": "Extended Idleness",
    "connect_sepio_low_speed": "Low Speed On High Speed Port",
    "connect_sepio_rare_device": "Rare Device",
    "connect_sepio_risky_child_connected": "Risky Child Connected",
    "connect_sepio_unexpected_speed": "Unexpected speed",
    "connect_sepio_unsupervised_host": "Unsupervised Host",
    "connect_sepio_unsupervised_network_infrastructure": "Unsupervised Network Infrastructure"
}

# List containing subtype filter criteria
subtype_filter = []
# Check which params are set to true and add to subtype_filter list 
for param_key, sub_type in subtype.items():
    if params[param_key] == "true":
        subtype_filter.append(sub_type)

logging.info(f"Sepio URL: {SEPIO_API_AUTH_URL}")
logging.info(f"Sepio Asset URL: {SEPIO_ASSETS_API_URL}")
logging.info(f"Sub-indicator filter: {subtype_filter}")
logging.info(f"Dormant Device Creation is set to: {DORMANT_DEVICE_CREATION}")
logging.info(f"Connecting to: {SEPIO_API_AUTH_URL}")
logging.info(f"API Configuration - Page Size: {PAGE_SIZE}, Wait Time: {WAIT_TIME}")
logging.info(f"Online Only: {ONLINE_ONLY}")

# Generate MAC addresses for devices without MAC addresses using asset_id
def generate_random_mac(asset_id, slap="6"):

    if not asset_id:
        return None
    
    # Create a hash of the asset_id
    hash_object = hashlib.sha256(asset_id.encode("utf-8"))
    hash_hex = hash_object.hexdigest()

    # Use the first 12 characters of the hash for the MAC address
    random = f"{hash_hex[:12].upper()}"

    random = random[:1] + slap + random[2:]

    return random

def fetch_sepio_token():
    headers = {"Content-Type": "application/json"}
    body = {"username": SEPIO_API_USERNAME, "password": SEPIO_API_PASSWORD}

    try:
        logging.info(f"SSL verification is set to: {ssl_verify}")

        response = requests.post(SEPIO_API_AUTH_URL, headers=headers, json=body, timeout=120, verify=ssl_verify)

        if response.status_code != 200:
            logging.error(f"Response headers: {dict(response.headers)}")

            try:
                logging.error(f"Response body: {response.json()}")
            except ValueError:
                logging.error(f"Response text: {response.text}")

        response.raise_for_status()
        response_data = response.json()
        token = response_data.get("token")
        expires_at_str = response_data.get("expiresAt")

        if not token:
            logging.error("Token was not found in the response")
            return None
        
        # Parse the token expiration to determine when a renewal is required
        try:
            if "Z" in expires_at_str:
                expires_at = datetime.strptime(expires_at_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            else:
                expires_at = datetime.fromisoformat(expires_at_str).astimezone(timezone.utc)
        except Exception as error:
            logging.error(f"Error parsing expiration time: {error}")
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        logging.info(f"Token expires at: {expires_at}")
        return token, expires_at 
        
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except SSLError as ssl_err:
        logging.error(f"SSL error occurred: {ssl_err}")
    except RequestException as req_err:
        logging.error(f"Error occurred: {req_err}")
    except Exception as error:
        logging.error(f"An unexpected error occurred: {error}")
    return None


def build_assets_query(page_number):
    asset_filter = []
    filter_index = 0

    if ONLINE_ONLY == "true":
        asset_filter.append({
            "index": filter_index,
            "field": "isOnline",
            "expression": "Exact",
            "value": "true",
            "op": "AND",
            "conditionTypeValue": "single",
            "is_userattribute": False,
        })
        filter_index += 1

    asset_filter.append({
            "index": filter_index,
            "field": "type",
            "expression": "Exact",
            "value": "2,3,8,9,10",
            "op": "AND",
            "conditionTypeValue": "multiple",
            "is_userattribute": False,
    })

    filter_index += 1 
        
    asset_filter.append({
            "index": filter_index,
            "field": "riskLevel",
            "expression": "Exact",
            "value": "2,3,4,5,6,7,8,9",
            "op": "AND",
            "conditionTypeValue": "multiple",
            "is_userattribute": False,
    })

    filter_index += 1

    system_filter = [
        {
            "index": 0,
            "field": "icon",
            "expression": "NotExact",
            "value": "50",
            "op": "AND",
            "conditionTypeValue": "multiple"
        }, {
            "index": 1,
            "field": "type",
            "expression": "NotExact",
            "value": "6",
            "op": "AND",
            "conditionTypeValue": "multiple"
        }, {
            "index": 2,
            "field": "hierarchy",
            "expression": "NotExact",
            "value": "1",
            "op": "AND",
            "conditionTypeValue": "multiple"
           }
        ]

    graphql_query = """
query GetDiscoveredAssets(
  $pageNum: Int!,
  $pageSize: Int!,
  $filters: [ConditionalRowFilterInput],
  $systemFilters: [ConditionalRowFilterInput]
) {
  conditionalTable(
    query: {
      filters: $filters,
      systemFilters: $systemFilters,
      globalSearch: ""
    }
    pagination: {
      pageNumber: $pageNum,
      pageSize: $pageSize,
      sortBy: "riskLevel_desc"
    }
  ) {
    data {
      id
      mac
      key
      isRiskAccepted
      model
      iconDescription
      isOnline
      riskLevel
      statusDescription
      firstSeen
      lastSeen
      locations {
        displayString
      }
      indicatorViewDetails {
        subType
        riskIndicationString
        description
      }
    }
  }
}
"""

    assets_query = {
        "query": graphql_query,
        "variables": {
             "pageNum": page_number,
             "pageSize": PAGE_SIZE,
             "filters": asset_filter,
             "systemFilters": system_filter
            }
        }

    return assets_query

def fetch_assets_data(token, expires_at):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    all_assets = []
    page_number = 1
    assets_added = 0

    while True:
        # Prevent token expiration by refreshing it 5 minutes before it expires 
        now = datetime.now(timezone.utc)
        if  expires_at - now < timedelta(minutes=5):
            logging.info(f"Token is expiring soon (in less than 5 minutes). Triggering refresh")
            new_token, new_expires_at = fetch_sepio_token()
            if new_token:
                token = new_token
                expires_at = new_expires_at 
                headers["Authorization"] = f"Bearer {token}"
                logging.info("Token refreshed successfully")
            else:
                logging.info("Failed to fetch new token")

        try:
            for attempt in range(3):
                logging.info(f"SSL verification is set to: {ssl_verify}")

                try:
                    payload = build_assets_query(page_number)
                    logging.debug(f"Payload: {payload}")
                    response = requests.post(SEPIO_ASSETS_API_URL, headers=headers, json=payload, timeout=120, verify=ssl_verify)

                except requests.RequestException as error:
                    logging.error(f"Network error on attempt {attempt + 1}: {error}")
                    time.sleep(1)
                    continue

                logging.info(f"Response status: {response.status_code}, Page: {page_number}, Page Size: {PAGE_SIZE}")

                if response.status_code == 200:
                    break

                logging.info(f"Attempt {attempt + 1} failed. Retrying in 1s")
                logging.error(f"Response headers: {dict(response.headers)}")
                
                try:
                    logging.error(f"Response body: {response.json()}")
                except ValueError:
                    logging.error(f"Response text: {response.text}")

                time.sleep(1)
            else:
                logging.error("Failed to get 200 response after 3 attempts. Stopping")
                break

            response.raise_for_status()
            response_data = response.json()

            if "data" in response_data:

                conditional_table = response_data.get("data", {}).get("conditionalTable", {})
                assets_on_page = conditional_table.get("data", [])
                
                if not assets_on_page:
                    logging.info(f"No assets found on page {page_number}. Ending pagination")
                    break

                for item in assets_on_page:
                    real_mac = (item.get("mac") or "").lower() 
                    asset_id = item.get("id")
                    key = item.get("key")
                    is_risk_accepted = item.get("isRiskAccepted")
                    status_description = item.get("statusDescription")
                    last_seen = item.get("lastSeen")
                    first_seen = item.get("firstSeen")
                    risk_level = item.get("riskLevel")
                    model = item.get("model")
                    icon_description = item.get("iconDescription")
                    is_online = item.get("isOnline")

                    if DORMANT_DEVICE_CREATION == "false" and real_mac.lower() == "dormant device":
                        logging.debug(f"Skipping asset: {key} dormant device creation is false")
                        continue
                    
                    # Skip if the device does not have a MAC and is_online is false 
                    if not real_mac and not is_online:
                        # logging.debug(f"Skipping asset: {key}, it is offline and has no MAC address. {is_online}")
                        continue

                    if real_mac.lower() == "dormant device" or not real_mac:
                        random_mac = generate_random_mac(asset_id).lower()
                            # logging.debug(f"Generated real_mac for {key}: {random_mac}")
                    else:
                        random_mac = ""

                    description = ""
                    sub_indication_string = ""
                    risk_indication_string = ""
                    display_string = ""

                    if "indicatorViewDetails" in item and isinstance(item["indicatorViewDetails"], list):
                            if len(item["indicatorViewDetails"]) == 0 and real_mac and real_mac.lower() != "dormant device":
                                # logging.debug(f"Skipping asset: {key} because indicatorViewDetails is empty and it has a real_mac.")
                                continue
                            elif len(item["indicatorViewDetails"]) > 0:
                                risk_indication_strings = [
                                    detail.get("riskIndicationString")
                                    for detail in item.get("indicatorViewDetails", [])
                                    if detail.get("riskIndicationString")
                                ]

                                risk_indication_string = ", ".join(risk_indication_strings)

                                descriptions = [
                                    detail.get("description")
                                    for detail in item.get("indicatorViewDetails", [])
                                    if detail.get("description")
                                ]
                                
                                description = ", ".join(descriptions)

                                sub_indication_strings = [
                                    detail.get("subType")
                                    for detail in item.get("indicatorViewDetails", [])
                                    if detail.get("subType")
                                ]

                                sub_indication_string = ", ".join(sub_indication_strings)

                                contains_potential_unmanaged_switch = any(
                                    detail.get("subType") == "Potential Unmanaged Switch"
                                    for detail in item["indicatorViewDetails"]
                                )
                                
                                # Handle Potential Unmanaged Switches separately as a random MAC is required and the device must not be dormant 
                                if random_mac and real_mac.lower() != "dormant device":
                                    if POTENTIAL_UNMANAGED_SWITCH == "false":
                                        logging.info(f"Potential Unmanaged Switch is false")
                                        continue
                                    elif POTENTIAL_UNMANAGED_SWITCH == "true" and not contains_potential_unmanaged_switch:
                                        logging.info(f"Skipping asset: {key} No Potential Unmanaged Switch found")
                                        continue

                                contains_subtype_filter = any(
                                    detail.get("subType") in subtype_filter
                                    for detail in item["indicatorViewDetails"]
                                )
 
                                # Skip the asset if it has a MAC address but no relevant indications
                                if real_mac and real_mac.lower() != "dormant device" and (not subtype_filter or not contains_subtype_filter):
                                    # logging.debug(f"Skipping asset: {key} as it has a MAC address but no threat or DNA anomaly indication.")
                                    continue

                    else:
                        logging.info(f"No indicatorViewDetails or unexpected format for asset {key}")

                    display_strings = [
                        detail.get("displayString")
                        for detail in item.get("locations", [])
                        if detail.get("displayString")
                    ]

                    display_string = ", ".join(display_strings)

                    asset = {
                        "random_mac": random_mac,
                        "real_mac": real_mac,
                        "key": key,
                        "is_risk_accepted": is_risk_accepted,
                        "status_description": status_description,
                        "last_seen": last_seen,
                        "first_seen": first_seen,
                        "model": model,
                        "risk_level": risk_level,
                        "description": description,
                        "sub_indication_string": sub_indication_string,
                        "risk_indication_string": risk_indication_string,
                        "icon_description": icon_description,
                        "display_string": display_string                     
                    }

                    logging.debug(f"MAC Addresses - Real: {asset['real_mac']} | Random: {asset['random_mac']}")
                    assets_added += 1
                    
                    all_assets.append(asset)

                # Wait between API calls to reduce the load on the server 
                if WAIT_TIME > 0 and WAIT_TIME <= 120000:
                    # Convert milliseconds to seconds
                    seconds = WAIT_TIME / 1000
                    logging.info(f"Waiting {seconds} seconds ({WAIT_TIME} milliseconds) before next page request")
                    time.sleep(seconds)

                page_number += 1

            else:
                logging.error("No data found in the response")
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
        except Exception as error:
            logging.error(f"An unexpected error occurred: {error}")
            break

    logging.info(f"Total assets processed: {assets_added}")

    return all_assets

token, expires_at = fetch_sepio_token()

if token:
    assets = fetch_assets_data(token, expires_at)
    logging.info(f"Number of assets: {len(assets)}")
else:
    logging.error("Failed to retrieve authentication token")
     
response = {"endpoints": []}
try:
    for asset in assets:
        random_mac = asset.get("random_mac")
        real_mac = asset.get("real_mac")
        key = asset.get("key")
        is_risk_accepted = asset.get("is_risk_accepted")
        risk_level = asset.get("risk_level")
        model = asset.get("model")
        description = asset.get("description")
        sub_indication_string = asset.get("sub_indication_string")
        risk_indication_string = asset.get("risk_indication_string")
        icon_description = asset.get("icon_description")
        display_string = asset.get("display_string")
        status_description = asset.get("status_description")
        raw_last_seen = asset.get("last_seen")
        raw_first_seen = asset.get("first_seen") 

        # Prepare the UTC time and convert it into the format that Forescout accepts (UNIX timestamp) 
        current_time_gmt = datetime.now(timezone.utc)
        timestamp = str(int(current_time_gmt.timestamp()))

        last_seen = None
        if raw_last_seen:
            dt_last_seen = datetime.fromisoformat(raw_last_seen.replace("Z", "+00:00"))
            # Use current time if "last_seen" is in the future (matching the "Now" label in Sepio)
            if dt_last_seen >= current_time_gmt:
                last_seen = timestamp
            else:
                last_seen = str(int(dt_last_seen.timestamp()))

        first_seen = None
        if raw_first_seen:
            dt_first_seen = datetime.fromisoformat(raw_first_seen.replace("Z", "+00:00"))
            int_first_seen = int(dt_first_seen.timestamp())
            
            # Don't push first_seen time for "Never" value from Sepio 
            if int_first_seen > 0:
                first_seen = str(int_first_seen)
            else:
                logging.info(f"Asset {key} has never been seen") 

        if real_mac and real_mac.lower() != "dormant device":
            # Use the real_mac if it exists and is not "Dormant Device"
            mac = {"mac": real_mac}
            mac_field = {}  # Do not set "connect_sepio_macrandom" if real MAC is present
        else:
            # Use random_mac if real_mac is missing or is "Dormant Device"
            mac = {"mac": random_mac}
            mac_field = {"connect_sepio_macrandom": random_mac}
                                            
        endpoint = {
            **mac,
            "properties": {
            "connect_sepio_department": "Sepio",
            **mac_field,
            "connect_sepio_asset_id": key,
            "connect_sepio_model": model,
            **({"connect_sepio_riskscore": risk_level} if risk_level is not None else {}),
            "connect_sepio_risk_acceptance": is_risk_accepted,
            "connect_sepio_description": description, 
            "connect_sepio_subindicationstring": sub_indication_string, 
            "connect_sepio_riskindicationstring": risk_indication_string, 
            "connect_sepio_classification": icon_description, 
            "connect_sepio_locations": display_string,
            "connect_sepio_status": status_description,
            **({"connect_sepio_last_seen": last_seen} if last_seen else {}),
            **({"connect_sepio_first_seen": first_seen} if first_seen else {}),  
            "connect_sepio_timestamp": timestamp 
            }
        }
                                       
        response["endpoints"].append(endpoint)
        logging.debug(f"Exporting assets: {endpoint}")
        
except Exception as error:
    response["error"] = "Could not retrieve endpoints"
    logging.error(f"Error occurred while processing assets: {str(error)}")

logging.info("Assets processing completed")