import logging
import urllib
import json
import ssl
from urllib import request, parse
from urllib.request import HTTPError, URLError
from datetime import datetime
import math

ip = params["connect_tychonelastic_ip"]
port = params["connect_tychonelastic_port"]
apiKey = params["connect_tychonelastic_api_key"]
index = params["connect_tychonelastic_stig_index"]

#dependencies
mac = params["mac"]
host_name = params["nbthost"]

upper_mac = mac.upper()
colon_mac = ":".join(upper_mac[i:i+2] for i in range(0,12,2))

score_query = {
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
                },
                {
                    "bool": {
                        "should":{
                            "match_phrase":{
                                "benchmark.score.system": "tychon.io:ccri-weighted"
                            }
                        }
                    }
                }
            ]
        }
    },
    "_source": [
        "benchmark.score.severity.overall",
        "benchmark.score.value",
        "benchmark.score.maximum",
        "benchmark.title",
        "benchmark.score.severity.high",
        "benchmark.score.severity.medium",
        "benchmark.score.severity.low",
        "benchmark.score.percentage",
        'event.created'
      ],
    "size": 1000
}

score_data = json.dumps(score_query).encode("utf-8")

request = urllib.request.Request(url='https://'+ip+':'+port+'/'+index+'/_search')
request.add_header("accept", "application/json")
request.add_header("Authorization", "ApiKey " + apiKey)
request.add_header("Content-Type", "application/json")
request.method = "GET"

response = {}
properties = {}

ret = []

try:
    request.data = score_data
    with urllib.request.urlopen(request, context=ssl_context) as resp:
        resp_bytes = resp.read()
        resp_ascii = resp_bytes.decode(encoding="UTF-8")
        obj = json.loads(resp_ascii)
        if 'hits' in obj:
            if 'hits' in obj['hits']:
                if len(obj['hits']['hits']) > 0:
                    for vdata in obj['hits']['hits']:
                        if "_source" in vdata:
                            data = vdata["_source"]

                            context_data =  composite_entry = {
                                "stigbenchmarktitle": data["benchmark.title"],
                                "stigbenchmarkscorevalue": int(math.ceil(float(data["benchmark.score.value"]))),
                                "stigbenchmarkscoremax": int(math.ceil(float(data["benchmark.score.maximum"]))),
                                "stigbenchmarkscorepercent": int(math.ceil(float(data["benchmark.score.percentage"]))),
                                "stigbenchmarkscorehigh": int(math.ceil(float(data["benchmark.score.severity.high"]))),
                                "stigbenchmarkscoremedium": int(math.ceil(float(data["benchmark.score.severity.medium"]))),
                                "stigbenchmarkscorelow": int(math.ceil(float(data["benchmark.score.severity.low"]))),
                                "stigscandate": int(datetime.strptime(data["event.created"], "%Y-%m-%dT%H:%M:%SZ").strftime('%s'))
                            }
                            ret.append(context_data)
    properties['connect_tychonelastic_stig_scores'] = ret
    response["properties"] = properties
    logging.debug("Returning response object to infrastructure. response=[{}]".format(response))

except HTTPError as e:
    response["error"] = "HTTPError: {}".format(e.code)
except URLError as e:
    response["error"] = "URLError: {}".format(e.reason)
except Exception as e:
    response["error"] = "Exception: {}".format(str(e))