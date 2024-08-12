import requests
from datetime import datetime
import json

logging.debug("===> Elastic Security: Host Isolation Requested")

# Get general parameters
username = params["connect_elasticsecurity_kibana_username"]
password = params["connect_elasticsecurity_kibana_password"]
create_case = params["connect_elasticsecurity_isolate_create_case"] == "true"

#############################################
## Create & Send request to Create case
#############################################
case_url = f'{params["connect_elasticsecurity_kibana_url"]}/api/cases'
case_title = params["connect_elasticsecurity_isolate_case_title"]
if(case_title == "NONE"):
    case_title = "Created by Forescout: Host Isolated by Action"
else:
    case_title = "Created by Forescout: " + case_title
case_tags = params["connect_elasticsecurity_isolate_case_tags"]
if(case_tags == "NONE"):
    case_tags = []
else:
    case_tags = case_tags.split(',')
case_severity = params["connect_elasticsecurity_isolate_case_severity"]
case_description = params["connect_elasticsecurity_isolate_case_description"]
case_syncAlerts = params["connect_elasticsecurity_isolate_case_syncAlerts"] == "true"
case_autoClose = params["connect_elasticsecurity_isolate_case_autoClose"] == "true"

case_id = "" # created case id

if(create_case):
    # Build request body
    case_body = {
        "connector": {
            "fields": None,
            "id": "none",
            "name": "none",
            "type": ".none"
        },
        "description": case_description,
        "owner": "securitySolution",
        "settings": {
            "syncAlerts": case_syncAlerts
        },
        "severity": case_severity,
        "tags": case_tags,
        "title": case_title
    }

    try: 
        # Make request
        request = requests.post(
            case_url,
            verify=ssl_verify,
            data=json.dumps(case_body),
            headers={'kbn-xsrf': 'true'},
            auth=(username, password)
        )
        
        if(request.status_code == 200):
            case_id = request.json()['id']
        else: 
            logging.warning("Case creation failed, API status code error")
            logging.warning(request.json())
    except Exception as e:
        logging.warning("Case creation failed, exception")
        logging.warning(e)

#############################################
## Create & Send request to Isolate endpoint
#############################################
isolate_url = f'{params["connect_elasticsecurity_kibana_url"]}/api/endpoint/action/isolate'
agent_id = params["connect_elasticsecurity_agent_id"]
comment = params["connect_elasticsecurity_comment"]
if(comment == "NONE"):
    comment = ""

# Build request body
isolate_body = {
    "endpoint_ids": [agent_id],
    "comment": ""
}
# Add Case ID if present
if(case_id):
    isolate_body["case_ids"] = [case_id]
# Comment, prepend "performed via Forescout" for tracking
if(len(comment) > 0):
    isolate_body["comment"] = "Isolated by Forescout: " + comment
else:
    isolate_body["comment"] = "Isolated by Forescout"

# Setup response object to Forescout
response = {
    "succeeded": False,
    #"troubleshooting": "",
    #"cookie": "",
    #"properties": {
    #    "connect_elasticsecurity_meta_endpoint": {
    #        "configuration_isolation": False,
    #        "state_isolation": False
    #    }
    #}
}

try: 
    # Make request
    request = requests.post(
        isolate_url,
        verify=ssl_verify,
        headers={'kbn-xsrf': 'true'},
        data=json.dumps(isolate_body),
        auth=(username, password)
    )
    
    if(request.status_code == 200):
        # Prase response
        response_json = request.json()

        # Check if no errors
        if('errors' not in response_json['data']):
            response["succeeded"] = True
            # Store agent id in cookie for undo action
            cookie = {
                "case_id": case_id
            }   
            response["cookie"] = json.dumps(cookie)
            # Update host with new isolated config
            response['succeeded'] = True
            response["properties"] = {
                "connect_elasticsecurity_meta_endpoint": {
                    "configuration_isolation": True,
                    "state_isolation": True
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

logging.debug("===> Elastic Security: Finished Host Isolation Request")
# print(json.dumps(response))