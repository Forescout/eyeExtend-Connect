import logging
import urllib
import json
import ssl
from urllib import request, parse
from urllib.request import HTTPError, URLError

ip = params.get("connect_tychonelastic_ip")
port = params.get("connect_tychonelastic_port")
apiKey = params.get("connect_tychonelastic_api_key")
indexes = [
    params.get("connect_tychonelastic_cve_iava_index"),
    params.get("connect_tychonelastic_ess_services_index"),
    params.get("connect_tychonelastic_cve_scan_index"),
    params.get("connect_tychonelastic_stig_index"),
    "tychon_assets"
]
headers = {
    "accept": "application/json",
    "Authorization": "ApiKey " + apiKey,
    "content-type": "application/json"
}

def callElastic(_index):
    _test_ping = request.Request("https://" + ip + ":" + port + "/" + _index + "/_stats", headers=headers, method="GET")
    _test_res = request.urlopen(_test_ping, context=ssl_context)
    _response = json.loads(_test_res.read())
    return _response

response = {}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
current_index = ""

try:
    for inx in indexes:
        current_index = inx
        response = callElastic(inx)
        if response is None:
            response["succeeded"] = False
            response["error"] = "No Response from Index Pattern " + inx
            response["troubleshooting"] = "Check the index pattern and try again"
            break

    response["succeeded"] = True
    response['result_msg'] = f'Connect App : Successfully connected. \n{str(indexes)}'

except HTTPError as e:
    response["succeeded"] = False
    response["error"] = "HTTP Error : Could not connect to TYCHON. Response code: {}".format(e.code)
    response["error"] = response["error"] + " " + current_index
    if e.code == 400:
        response["error"] = response["error"] + " " + "BAD REQUEST"
        response["troubleshooting"] = "Check the index pattern and try again"
    elif e.code == 401:
        response["error"] = response["error"] + " " + "NOT FOUND"
        response["troubleshooting"] = "Check the index pattern and try again"
    elif e.code == 403:
        response["error"] = response["error"] + " " + "FORBIDDEN"
        response["troubleshooting"] = "Ensure the API Key is an Elastic Base64 Encoded String and API key as " \
                                      "permission to indexes then try again "
    elif e.code == 404:
        response["error"] = response["error"] + " " + "MISSING"
        response["troubleshooting"] = "Check the index pattern and try again"
    elif e.code == 500:
        response["error"] = response["error"] + " " + "INTERNAL SERVER ERROR"
        response["troubleshooting"] = "Check the index pattern and try again"
    else:
        response["error"] = response["error"] + " " + " Unknown SERVER ERROR"
        response["troubleshooting"] = "Check the index pattern and try again"
except Exception as e:
    response["succeeded"] = False
    response["error"] = "HTTP Error : Could not connect to TYCHON. Response code: {}".format(e)

if "succeeded" not in response:
    response["succeeded"] = False
    response["error"] = 'Unknown issue'