import logging
import urllib
import json
import ssl
import certifi
from urllib.request import HTTPError, URLError

ip = params["connect_tychonelastic_ip"]
port = params["connect_tychonelastic_port"]
apiKey = params["connect_tychonelastic_api_key"]

index = params["connect_tychonelastic_ess_services_index"]

#dependencies
mac = params["mac"]
sending_ip = params["access_ip"]
domain = params["nbtdomain"]
host_name = params["nbthost"]

upper_mac = mac.upper()
colon_mac = ":".join(upper_mac[i:i+2] for i in range(0,12,2))

query = {
    "query": {
        "bool": {
            "filter":[
                {
                    "bool": {
                        "should":{
                            "match_phrase":{
                                "host.mac.keyword": colon_mac
                            }
                        }
                    }
                },
                {
                    "bool": {
                        "should":{
                            "match_phrase":{
                                "host.hostname.keyword": host_name
                            }
                        }
                    }
                }
            ]
        }
    },
    "_source":[
        "service.name",
        "service.version",
        "service.state",
        "service.status"
      ]
}



data = json.dumps(query).encode("utf-8")

request = urllib.request.Request(url='https://'+ip+':'+port+'/'+index+'/_search')
request.add_header("accept", "application/json")
request.add_header("Authorization", "ApiKey " + apiKey)
request.add_header("Content-Type", "application/json")
request.method = "GET"
request.data = data

response = {}
properties = {}

vulnerability_count = 0
rtn = []

try:
    with urllib.request.urlopen(request, context=ssl_context) as resp:
        resp_bytes = resp.read()
        resp_ascii = resp_bytes.decode(encoding="UTF-8")
        obj = json.loads(resp_ascii)
        if 'hits' in obj:
            if 'hits' in obj['hits']:
                for o in obj['hits']['hits']:
                    if '_source' in o:
                       data = o['_source']
                       composite_entry = {}
                       composite_entry["servicename"] = data["service.name"]
                       composite_entry["serviceversion"] = data["service.version"]
                       composite_entry["servicestatus"] = data["service.status"]
                       composite_entry["servicestate"] = data["service.state"]
                       rtn.append(composite_entry)

    properties['connect_tychonelastic_ess_services'] = rtn
    response["properties"] = properties
    logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
except HTTPError as e:
    response["error"] = "HTTPError: {}".format(e.code)
except URLError as e:
	response["error"] = "URLError: {}".format(e.reason)
except Exception as e:
	response["error"] = "Exception: {}".format(str(e))
