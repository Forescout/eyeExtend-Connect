"""
Copyright © 2023 Forescout Technologies, Inc.

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

api_details ={}

api_details["subscriber_api_key"] = params.get("connect_vederelabsioc_subscriber_api_key")
api_details["lookback"] = params.get("connect_vederelabsioc_lookback_days")
api_details["ssl_verify"] = ssl_verify

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

api_details["proxies"] = proxies

logging.debug("***Vedere Labs - Test*** Starting vederelabs Test Script")
logging.debug("***Vedere Labs - Test*** Params for Test Script: {}".format(api_details))

_headers = {'Content-Type': 'application/json; charset=utf-8;', 'api-key' : api_details["subscriber_api_key"]}
_time_range = "start=now-{}d".format(api_details["lookback"])

url = "https://api.feeds.vederelabs.com/feedservice/api/indicators/?type=ipv4-addr&{}".format(_time_range)

response = {}

try: 

    resp = requests.get(url, headers=_headers, timeout=360, verify=api_details["ssl_verify"], proxies=api_details["proxies"])
    
    if resp.status_code == 200: 
        response['succeeded'] = True
        response['result_msg'] = "Successfully connected to Vedere Labs."
    elif "No valid indicators" in resp.text:
        response['succeeded'] = True
        response['result_msg'] = "Successfully connected to Vedere Labs. No valid indicators found for configured conditions."
    else:
        resp.raise_for_status()

except Exception as e: 
    response['succeeded'] = False
    response['result_msg'] = "Could not connect to Vedere Labs Service. Exception occured: {}".format(e)

logging.debug("***Vedere Labs - Test*** {}".format(response["result_msg"]))