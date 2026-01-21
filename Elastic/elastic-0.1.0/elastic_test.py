import json
import logging
import requests

# Initialize logging
logging.debug('===>Starting Elastic Test Script')

# Get parameters
base_url = params.get("connect_elastic_url")
username = params.get("connect_elastic_username")
password = params.get("connect_elastic_password")
request_timeout = int(params.get("connect_elastic_request_timeout"))
logging.info('Testing connection to Elastic at: %s', base_url)
response = {
    "succeeded": False,
    "result_msg": ""
} 

url = base_url + "/_cat/health?format=json"

try: 
    request = requests.get(
        url,
        auth=(username, password),
        verify=ssl_verify,
        timeout=request_timeout
    )
    if(request.status_code == 200):
        response["succeeded"] = True
        response["result_msg"] = "Successfully connected"
        logging.info('Connection successful')
    else:
        response["succeeded"] = False
        response["result_msg"] = "API Status code error: " + json.dumps(request.json())
        logging.error('Connection failed: status %s', request.status_code)
except Exception as e:
    response["succeeded"] = False
    response["result_msg"] = "Exception: " + str(e)
    logging.error('Exception: %s', str(e))
