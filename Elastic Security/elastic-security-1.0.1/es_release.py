import requests
from datetime import datetime
import json

logging.debug("===> Elastic Security: Host Release Isolation Requested")

# Get parameters
username = params["connect_elasticsecurity_kibana_username"]
password = params["connect_elasticsecurity_kibana_password"]
cookie = json.loads(params["cookie"])
# Get agent, comment, case_id from cookie
agent_id = params["connect_elasticsecurity_agent_id"]
comment = params["connect_elasticsecurity_comment"]
if(comment == "NONE"):
    comment = ""
autoCloseCase = params["connect_elasticsecurity_isolate_case_autoClose"]
case_id = cookie["case_id"]

# Setup response object to Forescout
response = {
    "succeeded": False,
    "troubleshooting": "",
}

################################################################
## If closing case, check that case is not deleted first
################################################################
case_version = ""
if(autoCloseCase and case_id):
    case_url = f'{params["connect_elasticsecurity_kibana_url"]}/api/cases/{case_id}'
    try: 
        # Make request
        request = requests.get(
            case_url,
            verify=ssl_verify,
            headers={'kbn-xsrf': 'true'},
            auth=(username, password)
        )
        
        if(request.status_code == 200):
            case_version = request.json()["version"]
        else: 
            logging.warning("API status code error on getting case -- Will result in case close failure")
            logging.warning(request.json())
    except Exception as e:
        logging.warning("Exception on getting case version -- Will result in case close failure")
        logging.warning(e)

#############################################
## Create & Send request to release endpoint
#############################################
# Build request body
url = f'{params["connect_elasticsecurity_kibana_url"]}/api/endpoint/action/unisolate'
body = {
    "endpoint_ids": [agent_id],
    "comment": ""
}
# Add Case ID if present
if(case_version and case_id):
    body["case_ids"] = [case_id]
# Comment, prepend "performed by Forescout" for tracking
if(len(comment) > 0):
    body["comment"] = "Undo Isolation performed by Forescout: " + comment
else:
    body["comment"]  = "Undo Isolation performed by Forescout"

try: 
    # Make request
    request = requests.post(
        url,
        verify=ssl_verify,
        headers={'kbn-xsrf': 'true'},
        data=json.dumps(body),
        auth=(username, password)
    )
    
    if(request.status_code == 200):
        # Prase response
        response_json = request.json()

        # Check if no errors
        if('errors' not in response_json['data']):
            response["succeeded"] = True
            # Update host with new isolated config
            response["properties"] = {
                "connect_elasticsecurity_meta_endpoint": {
                    "configuration_isolation": False,
                    "state_isolation": False
                }
            }
        elif response_json['data']['errors']:
            response['succeeded'] = False
            response['troubleshooting'] = f'Elastic Security gave API error: {json.dumps(response_json["data"]["errors"])}'
    # 
    else:
        response['succeeded'] = False
        response['troubleshooting'] = f'Elastic Security gave status code error: {request.json()}'

except Exception as e:
    response['succeeded'] = False
    response["troubleshooting"] = f'Request Exception: {e}'


################################################################
## Get version of case after the release of the host
################################################################
if(autoCloseCase and case_version):
    case_url = f'{params["connect_elasticsecurity_kibana_url"]}/api/cases/{case_id}'
    try: 
        # Make request
        request = requests.get(
            case_url,
            verify=ssl_verify,
            headers={'kbn-xsrf': 'true'},
            auth=(username, password)
        )
        
        if(request.status_code == 200):
            case_version = request.json()["version"]
        else: 
            logging.warning("API status code error on getting case version -- Will result in case close failure")
            logging.warning(request.json())
    except Exception as e:
        logging.warning("Exception on getting case version -- Will result in case close failure")
        logging.warning(e)

#############################################
## Create & Send request to close case
#############################################
if(autoCloseCase and case_version):
    case_url = f'{params["connect_elasticsecurity_kibana_url"]}/api/cases'
    # Build request body
    case_body = {
        "cases": [
            {
                "id": case_id,
                "version": case_version,
                "status": "closed"
            }
        ],
    }

    try: 
        # Make request
        request = requests.patch(
            case_url,
            verify=ssl_verify,
            data=json.dumps(case_body),
            headers={'kbn-xsrf': 'true'},
            auth=(username, password)
        )
        
        if(request.status_code == 200):
            logging.info("Case closed")
        else: 
            logging.warning("Case closed failed, API status code error")
            logging.warning(request.json())
    except Exception as e:
        logging.warning("Case close failed, exception")
        logging.warning(e)

logging.debug("===> Elastic Security: Finished Host Release Isolation Request")
# print(json.dumps(response))