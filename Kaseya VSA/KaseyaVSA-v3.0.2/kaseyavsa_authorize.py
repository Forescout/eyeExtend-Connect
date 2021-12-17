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

import json
from urllib import parse
from hashlib import sha256
from hashlib import sha1
import random
import base64
import logging
import requests

# Values from system.conf
username = params["connect_kaseyavsa_username"]
password = params["connect_kaseyavsa_password"]
client_id = params["connect_kaseyavsa_client_id"]
client_secret = params["connect_kaseyavsa_client_secret"]
auth_token = params["connect_kaseyavsa_auth_code"]
redirect_uri = params["connect_kaseyavsa_redirect_uri"]
server = params["connect_kaseyavsa_server_ipaddress"]
port = params["connect_kaseyavsa_server_port"]
conn_type = params["connect_kaseyavsa_conn_type"]

# General Values
response = {}
response["token"] = ""

refresh_token = KASEYAVSA_API_LIB.refresh_token
refresh = refresh_token

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

if conn_type == "conn_type_oauth":

    logging.debug("Attempting OAuth")

    if refresh == "new":

        logging.debug("New OAuth Token")

        # OAuth Access URL
        oauth_access_url = "https://{}:{}/api/v1.0/authorize".format(server,port)
        oauth_raw = {"grant_type": "authorization_code", "code": auth_token, "redirect_uri": redirect_uri, "client_id": client_id, "client_secret": client_secret}
        oauth_data = parse.urlencode(oauth_raw).encode()
        header = {"Authorization": "Bearer " + auth_token,"content-type":"application/ x-www-form-urlencoded"}
        oauth_req = requests.request("POST", oauth_access_url, data=oauth_data, headers=header, verify=ssl_verify, proxies=proxies)
        code = oauth_req.status_code
        json_resp = json.loads(oauth_req.content)

        if code == 200:
            token = json_resp["access_token"]
            refresh = json_resp["refresh_token"]
            response["token"] = token
            KASEYAVSA_API_LIB.KASEYAVSA_REFRESH(refresh)
            logging.debug("Received token valid for {} seconds from OAuth Initial Request".format(json_resp["expires_in"]))
        else:
            token = ""
            refresh = "new"
            response["token"] = token
            KASEYAVSA_API_LIB.KASEYAVSA_REFRESH(refresh)
            logging.debug("No token received on OAuth Initial Request")

    else:

        logging.debug("Refresh OAuth Token")

        # OAuth Refresh URL
        oauth_refresh_url = "https://{}:{}/api/v1.0/token".format(server,port)
        oauth_raw = {"grant_type": "refresh_token", "refresh_token": refresh_token, "redirect_uri": redirect_uri, "client_id": client_id, "client_secret": client_secret}

        # Refresh access token
        oauth_data = parse.urlencode(oauth_raw).encode()
        header = {"Authorization": "Bearer " + auth_token,"content-type":"application/ x-www-form-urlencoded"}
        oauth_req = requests.request("POST", oauth_refresh_url, data=oauth_data, headers=header, verify=ssl_verify, proxies=proxies)
        code = oauth_req.status_code
        json_resp = json.loads(oauth_req.content)
        logging.debug("response code: {}".format(code))

        if code == 200:
            token = json_resp["access_token"]
            refresh = json_resp["refresh_token"]
            response["token"] = token
            KASEYAVSA_API_LIB.KASEYAVSA_REFRESH(refresh)
            logging.debug("Received token valid for {} seconds from OAuth Refresh".format(json_resp["expires_in"]))
        else:
            token = ""
            refresh = "new"
            response["token"] = token
            KASEYAVSA_API_LIB.KASEYAVSA_REFRESH(refresh)
            logging.debug("No token received on OAuth Refresh")

else:

    logging.debug("Attempting Basic Auth")

    UserPassword = password+username
    random_number = random.randint(9999999,100000000)

    RawSHA256Hash = sha256(password.encode('utf-8')).hexdigest()
    CoveredSHA256HashTemp = sha256(UserPassword.encode('utf-8')).hexdigest()
    CoveredSHA256Hash = sha256((CoveredSHA256HashTemp+str(random_number)).encode('utf-8')).hexdigest()
    RawSHA1Hash = sha1(password.encode('utf-8')).hexdigest()
    CoveredSHA1HashTemp = sha1(UserPassword.encode('utf-8')).hexdigest()
    CoveredSHA1Hash = sha1((CoveredSHA1HashTemp+str(random_number)).encode('utf-8')).hexdigest()
    Auth_header = 'user='+username+',pass2='+CoveredSHA256Hash+',pass1='+CoveredSHA1Hash+',rpass2='+RawSHA256Hash+',rpass1='+RawSHA1Hash+',rand2='+str(random_number)

    basic_url = "https://{}:{}/api/v1.0/auth".format(server,port)
    
    base64string = base64.b64encode(bytes('%s' % (Auth_header),'ascii'))
    header = {"Authorization": "Basic " + base64string.decode('utf-8')}

    basic_req = requests.request("GET", basic_url, headers=header, verify=ssl_verify, proxies=proxies)
    code = basic_req.status_code
    logging.debug("response code: {}".format(code))
    json_resp = json.loads(basic_req.content)

    if code == 200:
        token = json_resp["Result"]["Token"]
        response["token"] = token
        logging.debug("Received token valid until {} from Basic Auth".format(json_resp["Result"]["SessionExpiration"]))
    else:
        token = ""
        response["token"] = token
        logging.debug("No token received from Basic Auth")