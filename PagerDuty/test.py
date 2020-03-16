pd_api_key= params["connect_pagerduty_api_key"]
pd_user = params["connect_pagerduty_admin_user"]
pd_url = params["connect_pagerduty_url"]
pd_service_id = params["connect_pagerduty_service_id"]



response = {}


headers = {"Content-Type": "application/json",
		   "Accept": "application/vnd.pagerduty+json;version=2",
		   "Authorization": "Token token=" + pd_api_key ,
		   "From": pd_user}





## Verify all APIs required for the App return valid values back and are authenticated
URL = "https://api.pagerduty.com/incidents?time_zone=UTC"
request = urllib.request.Request(URL,  headers=headers)
resp = urllib.request.urlopen(request)
json_resp = json.loads(resp.read())
logging.debug(str(json_resp))

URL_SERVICE = "https://api.pagerduty.com/services/" + pd_service_id
service_request = urllib.request.Request(URL_SERVICE,  headers=headers)
service_resp = urllib.request.urlopen(service_request)
service_json_resp = json.loads(service_resp.read())
service_instance = service_json_resp['service'] 
logging.debug(str(service_json_resp))



if (resp.getcode() == 200) and (service_resp.getcode() == 200):
	response["succeeded"] = True
	response["result_msg"] = "Successfuly Connected and authenticated with PagerDuty Instance " + pd_url + " as user " + pd_user + " for service id " + pd_service_id + " name " + service_instance['name']
else:
	response["succeeded"] = False
	response["result_msg"] = "Failed to connect and/or authenticate with PagerDuty"

   



