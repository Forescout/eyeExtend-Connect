"""
Copyright © 2021 Forescout Technologies, Inc.

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

import logging
import requests
import json

# Values from system.conf
server = params.get("connect_ivantiepm_server")
port = params.get("connect_ivantiepm_port")
clientid = params.get("connect_ivantiepm_client_id")
clientsecret = params.get("connect_ivantiepm_client_secret")
username = params.get("connect_ivantiepm_username")
password = params.get("connect_ivantiepm_password")
scope = params.get("connect_ivantiepm_scope")

# General Values
response = {}

# Requests Proxy
is_proxy_enabled = params.get("connect_proxy_enable")
if is_proxy_enabled == "true":
    proxy_ip = params.get("connect_proxy_ip")
    proxy_port = params.get("connect_proxy_port")
    proxy_user = params.get("connect_proxy_username")
    proxy_pass = params.get("connect_proxy_password")
    if not proxy_user:
        proxy_url = f"https://{proxy_ip}:{proxy_port}"
        proxies = {"https" : proxy_url}
        logging.debug ("Proxy enabled / no user")
    else:
        proxy_url = f"https://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
        proxies = {"https" : proxy_url}
        logging.debug ("Proxy enabled / user")
else:
    logging.debug ("Proxy disabled")
    proxies = None

# URL to obtain Token
url = "https://{}:{}/my.identityserver/identity/connect/token".format(server,port)

# Data for Token request
payload = {
        "client_id" : clientid,
        "client_secret" : clientsecret,
        "grant_type" : "password",
        "scope" : scope,
        "username" : username,
        "password" : password
}
headers = {} # Left blank headers in case required in future

logging.debug("Attempting to obtain authorization token")

resp = requests.request("POST", url, headers=headers, data=payload, verify=ssl_verify, proxies=proxies)
resp_code = resp.status_code
json_resp = json.loads(resp.content)

if resp_code == 200:
    response["token"] = json_resp["access_token"]
    logging.debug("Received token valid for {} seconds".format(json_resp["expires_in"]))
else:
    response["token"] = ""
    logging.debug("No token received for authorization")