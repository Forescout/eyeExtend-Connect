import logging
import urllib
import json
import ssl
from urllib import request, parse
from urllib.request import HTTPError, URLError

ip = params["connect_tychonelastic_ip"]
port = params["connect_tychonelastic_port"]
apiKey = params["connect_tychonelastic_api_key"]
index = params["connect_tychonelastic_stig_index"]

#dependencies
mac = params["mac"]
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
    "aggs":{
      "result":{
          "terms": {"field": "rule.result.keyword"},
          "aggs":{
            "severity": {
             "terms": {
               "field": "rule.severity.keyword"
             }
           }
          }
      }
    },
    "size": 0
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

total_fail = 0
total_pass = 0
stig_type_fail_count = {
    "medium": 0,
    "high": 0,
    "low": 0
}
stig_type_pass_count = {
    "medium": 0,
    "high": 0,
    "low": 0
}

try:
    with urllib.request.urlopen(request, context=ssl_context) as resp:
        resp_bytes = resp.read()
        resp_ascii = resp_bytes.decode(encoding="UTF-8")
        obj = json.loads(resp_ascii)
        logging.debug("Benchmark Counts. elasticdata=[{}]".format(obj))
        if 'aggregations' in obj:
            if 'result' in obj["aggregations"]:
                if 'buckets' in obj['aggregations']['result']:
                    for resulty in obj['aggregations']['result']['buckets']:
                        result = resulty["key"]
                        if result == "pass":
                            total_pass = resulty["doc_count"]
                        else:
                            total_fail = resulty["doc_count"]
                        if 'severity' in resulty:
                            if 'buckets' in resulty['severity']:
                                for hitr in resulty['severity']['buckets']:
                                    if 'key' in hitr:
                                        sev = hitr["key"]
                                        if 'fail' == result and sev in stig_type_fail_count:
                                            stig_type_fail_count[sev] = hitr["doc_count"]
                                        elif 'pass' == result and sev in stig_type_pass_count:
                                            stig_type_pass_count[sev] = hitr["doc_count"]

    composite_item = {
        "totalstigpass": int(total_pass),
        "totalstigfail": int(total_fail),
        "stigfailhigh": int(stig_type_fail_count["high"]),
        "stigfailmedium": int(stig_type_fail_count["medium"]),
        "stigfaillow": int(stig_type_fail_count["low"]),
        "stigpasshigh": int(stig_type_pass_count["high"]),
        "stigpassmedium": int(stig_type_pass_count["medium"]),
        "stigpasslow": int(stig_type_pass_count["low"])
    }

    ret = []
    ret.append(composite_item)

    properties['connect_tychonelastic_stig_counts'] = ret
    response["properties"] = properties
    logging.debug("Returning response object to infrastructure. response=[{}]".format(response))

except HTTPError as e:
    response["error"] = "HTTPError: {}".format(e.code)
except URLError as e:
	response["error"] = "URLError: {}".format(e.reason)
except Exception as e:
	response["error"] = "Exception: {}".format(str(e))
