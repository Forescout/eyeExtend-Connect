import logging
import urllib
import json
import ssl
import certifi
from urllib.request import HTTPError, URLError
from datetime import datetime

ip = params["connect_tychonelastic_ip"]
port = params["connect_tychonelastic_port"]
apiKey = params["connect_tychonelastic_api_key"]
index = "tychon_assets*"

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
    },"sort" : [{ "event.created" : "desc" }],
    "_source":[
        "host.os.name",
        "host.hardware.bios.name",
        "host.os.version",
        "host.os.family",
        "host.os.build",
        "host.hardware.bios.version",
        "host.epo.name",
        "host.epo.guid",
        "host.hardware.cpu.numberofcores",
        "host.hardware.serial_number",
        "host.hardware.model",
        "host.hardware.cpu.caption",
        "host.agentguid",
        "host.biossn",
        "host.building",
        "host.department",
        "host.hardware.cpu.numberofcpus",
        "host.hardware.manufacturer",
        "host.hardware.time.boot_utc",
        "host.hardware.usb",
        "host.ou", #AD Host
        "host.os.releaseid",
        "host.path",
        "tags",
        "host.logged_on_user",
        "event.hygiene.shb_version",
        "application.tychon.endpoint.product.version",
        "host.id",
        "realm.id",
        "event.created"
      ], "size": 1
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
rtn = []

properties["connect_tychonelastic_managed"] = False
properties["connect_tychonelastic_hostid"] = ""
properties["connect_tychonelastic_realmid"] = ""
properties["connect_tychonelastic_lastcheckin"] = ""

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
                       composite_entry["osname"] = data["host.os.name"]
                       composite_entry["osversion"] = data["host.os.version"]
                       composite_entry["osbuild"] = data["host.os.build"]
                       composite_entry["osfamily"] = data["host.os.family"]
                       composite_entry["osrelease"] = data["host.os.releaseid"]
                       composite_entry["serialnumber"] = data["host.hardware.serial_number"]
                       composite_entry["systemmanufacturer"] = data["host.hardware.manufacturer"]
                       composite_entry["boottime"] = data["host.hardware.time.boot_utc"]
                       composite_entry["systemmodel"] = data["host.hardware.model"]
                       composite_entry["hostou"] = data["host.ou"]
                       composite_entry["biosversion"] = data["host.hardware.bios.version"]
                       composite_entry["biosname"] = data["host.hardware.bios.name"]
                       composite_entry["cpucores"] = data["host.hardware.cpu.numberofcores"]
                       composite_entry["cpucount"] = data["host.hardware.cpu.numberofcpus"]
                       composite_entry["epoguid"] = data["host.epo.guid"]
                       composite_entry["eponame"] = data["host.epo.name"]
                       composite_entry["epopath"] = data["host.path"]
                       composite_entry["epotags"] = data["tags"]
                       composite_entry["shbversion"] = data["event.hygiene.shb_version"]
                       composite_entry["epoagentid"] = data["host.agentguid"]
                       composite_entry["tychonversion"] = data["application.tychon.endpoint.product.version"]
                       composite_entry["tychonid"] = data["host.id"]
                       composite_entry["biosssn"] = data["host.biossn"]
                       composite_entry["hostdepartment"] = data["host.department"]
                       composite_entry["hostbuilding"] = data["host.department"]


                       rtn.append(composite_entry)
                       properties["connect_tychonelastic_hostid"] = data["host.id"]
                       properties["connect_tychonelastic_managed"] = True
                       properties["connect_tychonelastic_lastcheckin"] = int(datetime.strptime(data["event.created"], "%Y-%m-%dT%H:%M:%SZ").strftime('%s'))
                       properties["connect_tychonelastic_realmid"] = data["realm.id"]

    properties['connect_tychonelastic_host_info'] = rtn
    response["properties"] = properties
    logging.debug("Returning response object to infrastructure. response=[{}]".format(response))
except HTTPError as e:
    response["error"] = "HTTPError: {}".format(e.code)
except URLError as e:
	response["error"] = "URLError: {}".format(e.reason)
except Exception as e:
	response["error"] = "Exception: {}".format(str(e))

