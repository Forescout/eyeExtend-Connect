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

WO_SERVER_USERNAME= params.get("connect_workspaceone_user")
WO_SERVER_PASSWORD = params.get("connect_workspaceone_password")
WO_AUTH_MODE = params.get("connect_workspaceone_auth_mode")
WO_TOKEN_URL = params.get("connect_workspaceone_token_url")

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

response = {}

if WO_AUTH_MODE == "oauth":

    logging.debug("Requesting OAuth token from {}".format(WO_TOKEN_URL))
    payload = {
        "grant_type": "client_credentials",
        "client_id": WO_SERVER_USERNAME,
        "client_secret": WO_SERVER_PASSWORD
    }
    try:
        resp = requests.post(WO_TOKEN_URL, data=payload, verify=ssl_verify, proxies=proxies)
        json_resp = resp.json()
        if resp.status_code == 200:
            token = json_resp.get("access_token")
            logging.debug("OAuth token received, valid for {} seconds".format(json_resp.get("expires_in")))
            response["token"] = token
        else:
            response["error"] = "OAuth token request failed: {} - {}. OAuth token request failed, check Client ID, Secret and Token URL".format(resp.status_code, resp.text)
            logging.debug("{}".format(response["error"]))
    except requests.exceptions.RequestException as e:
        response["error"] = "OAuth token request exception: {}. OAuth token request failed, check Client ID, Secret and Token URL".format(str(e))
        logging.debug("{}".format(response["error"]))