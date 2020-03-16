import json
import ssl
import urllib.request

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#headers = {"Accept": "application/vnd.pagerduty+json;version=2", "Authorization": "Token token=8qrKsRpBD_VKBcgNcSML"}
response = {}

URL = "https://api.pagerduty.com/incidents?time_zone=UTC"

#request = urllib.request.Request(URL,  headers=headers)
#resp = urllib.request.urlopen(request, context=ctx)
#json_resp = json.loads(resp.read())

headers = {"Content-Type": "application/json",
		   "Accept": "application/vnd.pagerduty+json;version=2",
		   "Authorization": "Token token=8qrKsRpBD_VKBcgNcSML",
		   "From": "gitesh.shah@forescout.com"}


body = {
 "incident": {
    "type": "incident",
    "title": "The server is on fire.",
    "service": {
      "id": "PDMWK58",
      "type": "service_reference"
    },
    "urgency": "high",
    "body": {
      "type": "incident_body",
      "details": "A disk is getting full on this machine. You should investigate what is causing the disk to fill, and ensure that there is an automated process in place for ensuring data is rotated (eg. logs should have logrotate around them). If data is expected to stay on this disk forever, you should start planning to scale up to a larger disk."
    }
 
  }
 }


request = urllib.request.Request(URL,  headers=headers, data=bytes(json.dumps(body),encoding="utf-8"))
resp = urllib.request.urlopen(request, context=ctx)
json_resp = json.loads(resp.read()) 

print ("Response Code: ") 
print( resp.getcode())
print("\n")
print(json_resp)
