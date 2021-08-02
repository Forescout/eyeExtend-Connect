# v1.1.1 Fortigate VPN disable local user
# Keith Gilbert / Cedric Antoine

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
from urllib import request, error

# Values for system.conf passed to params
fortigate_ip1 = params.get("connect_fvpn_fip1")
fortigate_ip2 = params.get("connect_fvpn_fip2")
fortigate_ip3 = params.get("connect_fvpn_fip3")
fortigate_ip4 = params.get("connect_fvpn_fip4")
fortigate_token1 = params.get("connect_fvpn_token1")
fortigate_token2 = params.get("connect_fvpn_token2")
fortigate_token3 = params.get("connect_fvpn_token3")
fortigate_token4 = params.get("connect_fvpn_token4")

# values from property.conf
fortigate_ip = params["connect_fvpn_ip"]
fortigate_user = params["connect_fvpn_user"]
fortigate_vdom = params["connect_fvpn_vdom"]
fortigate_learnt = params["connect_fvpn_learnt"]

if fortigate_learnt == "FortiGate":
    if fortigate_ip1 == fortigate_ip:
        fortigate_token = fortigate_token1
    if fortigate_ip2 == fortigate_ip:
        fortigate_token = fortigate_token2
    if fortigate_ip3 == fortigate_ip:
        fortigate_token = fortigate_token3
    if fortigate_ip4 == fortigate_ip:
        fortigate_token = fortigate_token4

    # Fortigate user URL / BODY
    fortigate_user_url = f"https://{fortigate_ip}/api/v2/cmdb/user/local/{fortigate_user}?access_token={fortigate_token}&vdom={fortigate_vdom}"
    fortigate_user_body_disable = b"{\"status\":\"disable\"}"
    response = {}

    logging.info("Checking API token")

    if fortigate_token is None or fortigate_token is "" or fortigate_token is "none":

        logging.info("No valid API token")

        response["succeeded"] = False
        response["troubleshooting"] = {}
    else:
        req_disable = request.Request(fortigate_user_url, data=fortigate_user_body_disable, method="PUT")
        try:
            resp_disable = request.urlopen(req_disable, context=ssl_context)
            if resp_disable.getcode() == 200:
                put_response = json.loads(resp_disable.read())
                response["succeeded"] = True
        except error.HTTPError as error:
            logging.debug(f"HTTPError code : {error.read()}")
            response["succeeded"] = False
            response["error"] = f"Error could not Disable User. {error.reason}"
else:
    response["succeeded"] = False
    response["error"] = f"Error cannot disable user on FortiManager"