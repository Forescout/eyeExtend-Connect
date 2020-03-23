'''
Copyright © 2020 Forescout Technologies, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

pd_api_key= params["connect_pagerduty_api_key"]
pd_user = params["connect_pagerduty_admin_user"]
pd_service_id = params["connect_pagerduty_service_id"]
pd_incident_urgency = params["connect_pagerduty_incident_urgency"]
pd_incident_title = params["connect_pagerduty_incident_title"]
pd_incident_body = params["connect_pagerduty_incident_details"]

if pd_incident_urgency == 'connect_pagerduty_incident_low':
	pd_urgency_string = "low"
else:
	pd_urgency_string = "high"


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
    "urgency": pd_urgency_string,
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
	response["troubleshooting"] = "Failed to create Incident " + pd_incident_title







