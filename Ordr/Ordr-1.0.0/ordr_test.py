
# Resolve script for CounterACT
import urllib.request,urllib.error
import base64
import logging
import json
import requests

REQUEST_GET_TIMEOUT = 10


logging.debug('===>Starting Ordr Resolve Script')
# Defining Variables
resp = None

# Obtaining Global Variables
base_url = params.get("connect_ordr_url")
username = params.get("connect_ordr_username")
password = params.get("connect_ordr_password")
ctx = ssl_context


# Defining Headers and Adding Authentication header-----
headers = {
    'Content-Type': "application/xml",
    'charset': 'utf-8',
    'User-Agent': "FSCT/1.16.2020",
    }
credentials = ('%s:%s' % (username, password))
encoded_credentials = base64.b64encode(credentials.encode('ascii'))
headers['Authorization'] = 'Basic %s' % encoded_credentials.decode("ascii")

#-------------------------End of Headers

response = {}
properties = {}

try:
    url = base_url+"/Rest/Devices"
    resp = requests.get(url, headers=headers, auth=(username, password), verify=False, timeout=REQUEST_GET_TIMEOUT)
    if resp.status_code == 200 :
        response["succeeded"] = True
        response["result_msg"] = "Successfully connected to Ordr Server - "+str(resp.content)
    else:
        response["succeeded"] = False
        response["result_msg"] = "Could not connect to Ordr server"
except Exception as e:
    response["succeeded"] = False
    error = str(e)
    response["result_msg"] = "Could not connect to Ordr server - "+error
    logging.debug("Cannot connect. Error : " + error)

logging.debug('===>End of Ordr Test Script')
