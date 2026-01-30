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
import requests
import json
import re
import datetime

logging.debug("SentinelOne Quarantine Script Starting - jnetz")
# Get app user defined parameters from server
token = params.get("connect_sentinelone_api_token")
server = params.get("connect_sentinelone_server")

headers = {
    "Content-type": "application/json",
    "Authorization": f"ApiToken {token}"
}
try:
    logging.debug("The params mac value is: " + str(params['mac']))
except Exception as e:
    logging.debug("Error: " + str(e))

response = {}

# Should def this in the future, main code
try:
    if "mac" in params:
        mac = ":".join(params["mac"][i:i + 2] for i in range(0, 12, 2))
        logging.debug(f"Sending SentinelOne quarantine request for {mac}")
        resp = requests.get(f"{server}/web/api/v2.1/agents?networkInterfacePhysical__contains={mac}&countOnly=false&limit=1", headers=headers)
        
        if resp.status_code == 200:
            req = resp.json()
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
                logging.debug(f"Preparing Quarantine with data {json.dumps(data)}")
                
                quarantine_resp = requests.post(f"{server}/web/api/v2.1/agents/actions/disconnect",
                                                       json=data,
                                                       headers=headers)

                logging.debug(f"Quarantine Response Code is {quarantine_resp.status_code}")
                
                if quarantine_resp.status_code == 200:
                    response['succeeded'] = True
                    response['data'] = quarantine_resp.json()['data']

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

logging.debug("---End of SentinelOne Quarantine Script---")