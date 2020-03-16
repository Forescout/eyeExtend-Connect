pd_api_key= params["connect_pagerduty_api_key"]
pd_user = params["connect_pagerduty_admin_user"]
pd_url = params["connect_pagerduty_url"]
pd_service_id = params["connect_pagerduty_service_id"]
pd_incident_urgency = params["connect_pagerduty_incident_urgency"]
pd_incident_title = params["connect_pagerduty_incident_title"]
pd_incident_body = params["connect_pagerduty_incident_details"]

response = {}

URL = "https://api.pagerduty.com/incidents?time_zone=UTC"


headers = {"Content-Type": "application/json",
		   "Accept": "application/vnd.pagerduty+json;version=2",
		   "Authorization": "Token token=" + pd_api_key,
		   "From": pd_user}


body = {
 "incident": {
    "type": "incident",
    "title": pd_incident_title,
    "service": {
      "id": pd_service_id,
      "type": "service_reference"
    },
    "urgency": "high",
    "body": {
      "type": "incident_body",
      "details": pd_incident_body
    }
 
  }
 }

 
request = urllib.request.Request(URL,  headers=headers, data=bytes(json.dumps(body),encoding="utf-8"))
resp = urllib.request.urlopen(request)
json_resp = json.loads(resp.read())
logging.debug(str(json_resp))

if resp.getcode() == 201:
	response["succeeded"] = True
	incident = json_resp['incident']
	response["response_message"] = "Successfuly Created incident with ID " + incident['id']
else:
	response["succeeded"] = False
	response["troubleshooting"] = "Failed to create Incident" + pd_incident_title

   





