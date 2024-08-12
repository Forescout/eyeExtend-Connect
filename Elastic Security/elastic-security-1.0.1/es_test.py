import requests

# Get parameters
url = f'{params["connect_elasticsecurity_kibana_url"]}/api/endpoint/metadata?sortField=last_checkin&pageSize=1'
username = params["connect_elasticsecurity_kibana_username"]
password = params["connect_elasticsecurity_kibana_password"]

response = {
    "succeeded": False,
    "result_msg": ""
} 

try: 
    request = requests.get(
        url,
        verify=ssl_verify,
        headers={'kbn-xsrf': 'true'},
        auth=(username, password)
    )
    if(request.status_code == 200):
        response["succeeded"] = True
        response["result_msg"] = "Successfully connected: " + json.dumps(request.json())
    else:
        response["succeeded"] = False
        response["result_msg"] = "API Status code error: " + json.dumps(request.json())
except Exception as e:
    response["succeeded"] = False
    response["result_msg"] = "Exception: " + str(e)

# logging.debug(response)