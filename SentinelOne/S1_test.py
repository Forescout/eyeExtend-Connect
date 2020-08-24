import logging
import urllib.request

logging.info("SentinelOne Test Script")

# General params
token = params.get("connect_sentinelone_api_token")
server = params.get("connect_sentinelone_server")
headers = {
    "User-Agent": "FSCT/1.16.2020",
    "Accept": "*/*",
    "Cache-Control": "no-cache",
    "charset": "utf-8",
    "Connection": "keep-alive",
}
# Set response
response = {}

# Call resource
request = urllib.request.Request(
    server + "/web/api/v2.1/accounts?limit=1&countOnly=true&ApiToken=" + token, headers=headers,
)
# Read resource response
resp = urllib.request.urlopen(request)

if resp.getcode() == 200:
    logging.debug("Test: Succeeded")
    response["succeeded"] = True
    response["result_msg"] = "Successfull connected to SentinelOne Server."
else:
    logging.debug("Test: Failed")
    response["succeeded"] = False
    response["result_msg"] = "Could not connect to SentinelOne Server"
