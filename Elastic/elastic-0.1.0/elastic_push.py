# Push script for CounterACT
import json
import logging
import requests
from typing import List, Dict

# Initialize logging
logging.debug('===>Starting Elastic Push Script')

# Defining Variables
base_url = params.get("connect_elastic_url")
username = params.get("connect_elastic_username")
password = params.get("connect_elastic_password")
datastream = params.get("connect_elastic_datastream")
request_timeout = int(params.get("connect_elastic_request_timeout"))
properties = {}
batch_mode = False
item_response = {}

# Initialize response structure
response = {
    "succeeded": False,
    "result_msg": ""
}

def fetch_data() -> List[Dict]:
    '''
    Fetch and process data from forescout endpoints.
    
    Args:
        endpoints (list): List of endpoint host data from Forescout
        
    Returns:
        list: Processed forescout_data
    
    '''
    forescout_data = []
    try:
        for host in endpoints:
            logging.info("Host Info >>> %s", str(host))
            if not isinstance(host, dict):
                raise ValueError("Host data is not a dictionary")
            data = host
            item_response = {}
            cid = host.get("correlation_id")
            if cid is None:
                raise KeyError("Missing correlation_id in host data")
            item_response["succeeded"] = True
            response[cid] = item_response
            # append processed to forescout_data
            forescout_data.append(data)
    except Exception as e:
        err_msg = f"Error while fetching data : {str(e)}"
        logging.error(err_msg)
        item_response["succeeded"] = False
        item_response["result_msg"] = err_msg
        response["default_response"] = item_response
    return forescout_data

def create_payload(forescout_data: List[Dict]) -> str:
    '''
    Create and format data to be sent to Elastic in bulk format.
    
    Args:
        forescout_data (list): List of data to be sent to Elastic

    Returns:
        str: Formatted data to be sent to Elastic
    '''
    lines = []
    for data in forescout_data:
        lines.append(json.dumps({"create": {}}))
        lines.append(json.dumps({"message": data}))
    payload = "\n".join(lines) + "\n"
    return payload

def send_to_elastic(payload: str) -> None:
    '''
    Send payload data to specified datastream in Elastic using bulk API.
    
    Args:
        payload (str): Formatted NDJSON payload to be sent to Elastic
    
    Returns:
        None: Updates the global response dictionary with success/error status
    '''
    try:
        logging.info('===>Sending POST request with req-body : %s', str(payload))
        url = f"{base_url}/logs-{datastream}-default/_bulk"
        resp = requests.post(
            url,
            headers={"Content-Type": "application/x-ndjson"},
            data=payload,
            auth=(username, password),
            verify=ssl_verify,
            timeout=request_timeout
        )
        if resp.status_code in [200, 201]:
            response["succeeded"] = True
        else:
            error_msg = f"Connection Error to Elastic : {resp.status_code}"
            logging.error(error_msg)
            item_response["error"] = error_msg
            item_response["result_msg"] = error_msg
            response["default_response"] = item_response
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection Error to Elastic in exception : {str(e)}"
        response["result_msg"] = error_msg
        logging.error(f"Request failed: {e}")

if 'endpoints' in vars() or 'endpoints' in globals():
  # 'endpoints' contains a list of host data from Forescout
    logging.info("Endpoints>>> %s", str(endpoints))
    batch_mode = True
    forescout_data = fetch_data()
    payload = create_payload(forescout_data)
    send_to_elastic(payload)
