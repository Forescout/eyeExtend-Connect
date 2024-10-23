"""
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
"""

from urllib import request, parse
from urllib.request import HTTPError, URLError
import json
import logging

# PANEL Related VARS
P_TENANT_ID = params.get("connect_intune_tenant_id")
P_APPID = params.get("connect_intune_application_id")
P_APPLICATION_SECRET = params.get("connect_intune_application_secret")

# Delegated Account
P_USERNAME = params.get("connect_intune_username")
P_USERNAME_PASSWORD = params.get("connect_intune_username_password")

# COMMON API VARS
MS_LOGIN_URL = "https://login.microsoftonline.com/"
OAUTH2_ENDPOINT = "/oauth2/token"
OAUTH2_DELEGATED_ENDPOINT = "/oauth2/v2.0/token"
TOKEN_URL = MS_LOGIN_URL + P_TENANT_ID + OAUTH2_ENDPOINT

# NAC API TOKEN
NAC_RESOURCE = "https://api.manage.microsoft.com/"

# GRAPH API TOKEN
GRAPH_RESOURCE = "https://graph.microsoft.com"

# Build NAC payload
NAC_PAYLOAD = {"client_id": P_APPID,
               "resource": NAC_RESOURCE,
               "client_secret": P_APPLICATION_SECRET,
               "grant_type": "client_credentials"}

# Build GRAPH payload
GRAPH_PAYLOAD = {"client_id": P_APPID,
                 "resource": GRAPH_RESOURCE,
                 "client_secret": P_APPLICATION_SECRET,
                 "grant_type": "client_credentials"}

# DELEGATED GRAPH
GRAPH_DELEGATED_PAYLOAD = {"client_id": P_APPID,
                           "username": P_USERNAME,
                           "password": P_USERNAME_PASSWORD,
                           "client_secret": P_APPLICATION_SECRET,
                           "resource": "https://graph.microsoft.com",
                           "grant_type": "password"}

# NAC endcoded payload
nac_data = parse.urlencode(NAC_PAYLOAD).encode()

# GRAPH endcoded payload
graph_data = parse.urlencode(GRAPH_PAYLOAD).encode()

# Delegated GRAPH endcoded payload
graph_delegated_data = parse.urlencode(GRAPH_DELEGATED_PAYLOAD).encode()

logging.info('Requesting Bearer Tokens')

# Init
response = {}
tokens = {}
tokens["nac_token"] = ""
tokens["graph_token"] = ""
tokens["graph_delegated_token"] = ""
response_error_message = []

# GET TOKENS
# NAC
try:
    # Create proxy server
    proxy_server = intune_proxy_server.ConnectProxyServer()
    proxy_server.set_init(params)
    opener = proxy_server.get_urllib_request_https_opener(intune_proxy_server.ProxyProtocol.all, ssl_context)

    logging.info('Requesting NAC Bearer Token')
    nac_req = request.Request(TOKEN_URL, data=nac_data, method="POST")
    nac_resp = request.urlopen(nac_req)

    nac_json_resp = json.loads(nac_resp.read())

    tokens["nac_token"] = nac_json_resp['access_token']

    logging.info('Retrieved NAC Bearer Token')
    logging.debug("NAC Bearer Token (First 50): %s", tokens["nac_token"][0:50])

except HTTPError as e:
    logging.debug('HTTP Error : Could not connect to Intune : %s', format(e.code))
    response_error_message.append(f"ERROR : NAC / GRAPH : HTTP Error : {e.code}\n")

except URLError as e:
    logging.debug('URL Error : Could not connect to Intune : %s', format(e.reason))
    response_error_message.append(f"ERROR : NAC / GRAPH : URL Error : {e.reason}\n")

except Exception as e:
    logging.debug('Exception : Could not connect to Intune : %s', format(str(e)))
    response_error_message.append(f"ERROR : NAC / GRAPH : Exception Error : {str(e)}\n")

# GRAPH
try:
    # Create proxy server
    proxy_server = intune_proxy_server.ConnectProxyServer()
    proxy_server.set_init(params)
    opener = proxy_server.get_urllib_request_https_opener(intune_proxy_server.ProxyProtocol.all, ssl_context)

    logging.info('Requesting GRAPH Bearer Token')
    graph_req = request.Request(TOKEN_URL, data=graph_data, method="POST")
    graph_resp = request.urlopen(graph_req)
    graph_json_resp = json.loads(graph_resp.read())

    tokens["graph_token"] = graph_json_resp['access_token']

    logging.info('Retrieved GRAPH Bearer Token')
    logging.debug("GRAPH Bearer Token (First 50): %s", tokens["graph_token"][0:50])

except HTTPError as e:
    logging.debug('HTTP Error not connect to Intune : %s', format(e.code))
    response_error_message.append(f"ERROR : NAC / GRAPH : HTTP Error : {e.code}\n")

except URLError as e:
    logging.debug('URL Error Error not connect to Intune : %s', format(e.reason))
    response_error_message.append(f"ERROR : NAC / GRAPH : URL Error : {e.reason}\n")

except Exception as e:
    logging.debug('Exception Error not connect to Intune : %s', format(str(e)))
    response_error_message.append(f"ERROR : NAC / GRAPH : Exception Error : {str(e)}\n")

# DELEGATED
if P_USERNAME:

    # Delegated Token URL
    TOKEN_DELEGATED_URL = MS_LOGIN_URL + P_TENANT_ID + OAUTH2_ENDPOINT

    try:
        # Create proxy server
        proxy_server = intune_proxy_server.ConnectProxyServer()
        proxy_server.set_init(params)
        opener = proxy_server.get_urllib_request_https_opener(intune_proxy_server.ProxyProtocol.all, ssl_context)
        # DELEGATED GRAPH TOKEN
        logging.info('Requesting DELEGATED GRAPH Bearer Token')

        graph_delegated_req = request.Request(TOKEN_DELEGATED_URL, data=graph_delegated_data, method="POST")
        graph_delegated_resp = request.urlopen(graph_delegated_req)
        graph_delegated_json_resp = json.loads(graph_delegated_resp.read())

        tokens["graph_delegated_token"] = graph_delegated_json_resp['access_token']

        logging.info('Retrieved DELEGATED GRAPH Bearer Token')
        logging.debug("DELEGATED GRAPH Bearer Token (First 50): %s", tokens["graph_delegated_token"][0:50])

    except HTTPError as e:
        logging.debug('ERROR : DELEGATED : HTTP Error not connect to Intune : %s', format(e.code))
        response_error_message.append(f"ERROR : DELEGATED : HTTP Error : {e.code}\n")

    except URLError as e:
        logging.debug('ERROR : DELEGATED : URL Error not connect to Intune : %s', format(e.reason))
        response_error_message.append(f"ERROR : DELEGATED : URL Error : {e.reason}\n")

    except Exception as e:
        logging.debug('ERROR : DELEGATED : Exception Error not connect to Intune : %s', format(str(e)))
        response_error_message.append(f"ERROR : DELEGATED : Exception Error : {str(e)}\n")

else:
    logging.info("GRAPH DELEGATED TOKEN not required")
    response_error_message.append("GRAPH DELEGATED Bearer Token not required\n")

# Build Tokens Store
# Response token is a string using json.dumps
# Other modules will need to convert back to dict.

# Build response return
if tokens["nac_token"] and tokens["graph_token"] and tokens["graph_delegated_token"]:
    # Retrieved all 3 tokens
    logging.info('Retrieved NAC and GRAPH and DELEGATED Bearer Tokens')
    response["succeeded"] = True
    response["token"] = json.dumps(tokens)

elif tokens["nac_token"] and tokens["graph_token"] and P_USERNAME == "":
    # Only require NAC and GRAPH tokens
    logging.info('Retrieved NAC and GRAPH  Bearer Tokens (DELEGATED token not required)')
    response["succeeded"] = True
    response["token"] = json.dumps(tokens)

elif tokens["nac_token"] and tokens["graph_token"]:
    # Only require NAC and GRAPH tokens
    logging.info('Retrieved NAC and GRAPH  Bearer Tokens (DELEGATED Token Suspect)')
    response["succeeded"] = True
    response["token"] = json.dumps(tokens)

else:
    # Something went wrong
    logging.info("ERROR : Exception cound not obtain 1 or more tokens. Set debug to level 5")
    response["succeeded"] = False
    response["error"] = response_error_message
    response["token"] = json.dumps(tokens)
