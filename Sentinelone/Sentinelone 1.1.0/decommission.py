'''
Created 2024 Jesse Netz (SentinelOne)
**********
MIT License


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

import logging
import urllib.request
import json
import re
import datetime

logging.debug("SentinelOne Decommission Script Starting - jnetz")
# Get app user defined parameters from server
token = params.get("connect_sentinelone_api_token")
server = params.get("connect_sentinelone_server")

try:
    logging.debug("The params mac value is: " + str(params['mac']))
except Exception as e:
    logging.debug("Error: " + str(e))

response = {}

# Should def this in the future, main code
try:
    if "mac" in params:
        mac = ":".join(params["mac"][i:i + 2] for i in range(0, 12, 2))
        logging.debug(f"Sending SentinelOne decommission request for {mac}")
        request = urllib.request.Request(
            server
            + "/web/api/v2.1/agents?networkInterfacePhysical__contains="
            + mac
            + "&countOnly=false&limit=1&ApiToken="
            + token,
            headers={
                "User-Agent": "FSCT/1.16.2020",
                "Accept": "*/*",
                "Cache-Control": "no-cache",
                "charset": "utf-8",
                "Connection": "keep-alive",
            },
        )
        resp = urllib.request.urlopen(request, timeout=5)
        if resp.status == 200:
            req = json.loads(resp.read())
            if not req["data"]:
                logging.debug(f"There is no data for {mac}")
                pass
            else:
                sentinelone_id = req['data'][0]['id']
                logging.debug(f"Sentinelone ID: {sentinelone_id}")

                data = {
                    "data": {},
                    "filter": {
                        "ids": [
                            sentinelone_id
                        ]
                    }
                }
                logging.debug(f"Preparing Decom with data {json.dumps(data)}")
                decom_request = urllib.request.Request(server + "/web/api/v2.1/agents/actions/decommission",
                                                       data=bytes(json.dumps(data), encoding="utf-8"),
                                                       headers={
                                                           "User-Agent": "FSCT/1.16.2020",
                                                           "Accept": "*/*",
                                                           "Cache-Control": "no-cache",
                                                           "charset": "utf-8",
                                                           "Connection": "keep-alive",
                                                           "Content-type": 'application/json',
                                                           "Authorization": "APIToken " + token
                                                       })

                decom_resp = urllib.request.urlopen(decom_request, timeout=5)
                logging.debug(f"Decom Response Code is {decom_resp.getcode()}")
                
                if decom_resp.getcode() == 200:
                    response['succeeded'] = True
                    response['data'] = json.loads(decom_resp.read())['data']

        else:
            response["error"] = "Server response not '200'"
            logging.debug("Server response not '200'")
    else:
        response["error"] = "Forescout error: No MAC address to query the endpoint"
        logging.debug("Forescout error: No MAC address to query the endpoint")

except Exception as e:
    response["error"] = "Unknown Connection Error to SentinelOne"
    error = str(e)
    logging.debug("Error is : " + error)

logging.debug("---End of SentinelOne Decommission Script---")