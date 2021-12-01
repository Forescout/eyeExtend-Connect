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
import requests
import json
import logging

logging.debug('===>Starting Cisco FMC ADD_IP Script')

#Definining Variables
response = {}

server = params['connect_ciscofmc_url']
username = params['connect_ciscofmc_username']
password = params['connect_ciscofmc_password']
Access_token = params["connect_authorization_token"]
domain = params['connect_ciscofmc_domain']
dynamicobject = params['connect_ciscofmc_dynamicobject']
ip = params['ip']
ctx = ssl_verify




try:
    if Access_token != '':
        logging.debug(f'Add IP script: Authorisation Token: {Access_token}')
    else:
        fmc = ciscofmc.CiscoFMC(server, username, password, ctx)
        fmc.get_auth_token()
        Access_token = fmc.access_token
        logging.debug(f'Add IP script: Authorisation Token: {Access_token}')

    url = f'https://{server}/api/fmc_config/v1/domain/{domain}/object/dynamicobjects/{dynamicobject}/mappings?action=add'
    headers = {'X-Auth-Access-Token': Access_token, 'Content-Type': 'application/json'}
    payload = json.dumps({"mappings": [ip]})

    resp = requests.put(url, headers=headers,data=payload, verify=ctx)
    if resp.status_code == 201:
        response["succeeded"] = True
        logging.debug(f'CiscoFMC add IP was success. Response: {resp.json()}')

    elif resp.status_code == 500:
        response["succeeded"] = False
        response["troubleshooting"] = f"Failed action. Invalid Domain Name"
        logging.debug(f"===>Cisco FMC Add IP Failed- Invalid Domain name- {resp.json()}")

    elif resp.status_code == 404:
        response["succeeded"] = False
        response["troubleshooting"] = f"Failed action. Invalid Dynamic Object Name"
        logging.debug(f"===>Cisco FMC Add IP Failed- Invalid Dynamic Object Name- {resp.json()}")
    else:
        response["succeeded"] = False
        response["troubleshooting"] = f"Failed action.Debug for more details"
        logging.debug(f"===>Cisco FMC Add IP Failed- Response Code - {resp.status_code}")
        logging.debug(f"===>Cisco FMC Add IP Failed- Response - {resp.json()}")


except requests.exceptions.HTTPError as e:
    logging.debug(f'Cannot connect the FMC HTTPError: {e}')
except requests.exceptions.ConnectionError as e:
    logging.debug(f'Cannot connect the FMC ConnectionError : {e}')
except requests.exceptions.Timeout as e:
    logging.debug(f'Cannot connect the FMC Timeout Error : {e}')
except Exception as e:
    logging.debug(f"===>Cisco FMC Class Failed - Error - Verify the FMC IP/FQDN \n{e}")

logging.debug('===>End of  Cisco FMC ADD_IP Script')