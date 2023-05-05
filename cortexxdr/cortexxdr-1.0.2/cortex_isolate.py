'''
Copyright © 2021 Westcon Solutions Pte Ltd.

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
'''

''' Isolate Cortex XDR Endpoints '''
import uuid
import json
import requests, urllib.error
from datetime import datetime, timezone
import secrets
import string
import hashlib


base_url = params['connect_cortexxdr_api_url']
auth_id = params['connect_cortexxdr_api_id']
auth_key = params['connect_cortexxdr_api_key']
response = {}

# Generate a 64 bytes random string
nonce = "".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(64)])
# Get the current timestamp as milliseconds.
timestamp = int(datetime.now(timezone.utc).timestamp()) * 1000
# Generate the API auth key:
api_auth_key = "%s%s%s" % (auth_key, nonce, timestamp)
# Convert to bytes object
api_auth_key = api_auth_key.encode("utf-8")
# Calculate sha256 to use for Authorisation:
api_key_hash = hashlib.sha256(api_auth_key).hexdigest()

header = {
           'x-xdr-timestamp': str(timestamp),
           'x-xdr-nonce': nonce,
           'x-xdr-auth-id': auth_id,
           'Authorization': api_key_hash,
           'Content-Type': 'application/json'
    }


if 'connect_cortexxdr_read_endpointid' in params:
    endpoint_id = params ['connect_cortexxdr_read_endpointid']

    data = {
        "request_data":{
             "endpoint_id":endpoint_id
        }
    }
   
    data = json.dumps(data)

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
            logging.debug("Proxy enabled / no user")
        else:
            proxy_url = f"https://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
            proxies = {"https" : proxy_url}
            logging.debug("Proxy enabled / user")
    else:
        logging.debug("Proxy disabled")
        proxies = None

    try:
        resp = requests.post(url=base_url+'/public_api/v1/endpoints/isolate', data=bytes(data.encode("utf-8")), headers=header, verify=ssl_verify, proxies=proxies)
        request_response = json.loads(resp.content)
        return_values = request_response['reply']
        if return_values['endpoints_count'] == 1:
            response["succeeded"] = True
        else:
            response["succeeded"] = False
            response["troubleshooting"] = "Failed, endpoint was not able to be restricted"
    # for some reason, a valid output will cause a HTTP error so the exception is caught and processed
    except urllib.error.HTTPError as e:
        request_response = json.loads(e.read())
        return_values = request_response['reply']
        if return_values['err_code'] == 500 and return_values['err_msg'] == "An error occurred while processing XDR public API - No endpoint was found for creating the requested action":
           response["succeeded"] = False 
           response["troubleshooting"] = "Failed action. Device Cannot be blocked"
        else:
           response["succeeded"] = False 
           response["troubleshooting"] = "Failed action. Unknown"
    except requests.exceptions.HTTPError as errh:
        response["succeeded"] = False
        response["troubleshooting"] = "Failed action, HTTP error:{}".format(errh)
    except requests.exceptions.ConnectionError as errc:
        response["succeeded"] = False
        response["troubleshooting"] = "Failed action, Connecting error:{}".format(errc)
    except requests.exceptions.Timeout as errt:
        response["succeeded"] = False
        response["troubleshooting"] = "Failed action, imeout error:{}".format(errt)
    except requests.exceptions.RequestException as err:
        response["succeeded"] = False
        response["troubleshooting"] = "Failed action, error:{}".format(err)

else:
    response["succeeded"] = False
    response["troubleshooting"] = "Failed action. Endpoint ID not Valid"
