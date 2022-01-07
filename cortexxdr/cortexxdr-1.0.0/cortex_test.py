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

''' Cortex XDR Endpoint Test Script '''
import urllib.request
import json
import logging
from datetime import datetime, timezone
import secrets
import string
import hashlib
import socket

logging.info('===>Starting Test of Cortex API Server')

# Server configuration fields will be available in the 'params' dictionary.
base_url = params['connect_cortexxdr_api_url']
auth_id = params['connect_cortexxdr_api_id']
auth_key = params['connect_cortexxdr_api_key']
test_ip = params['connect_cortexxdr_test_ip']



# Return the 'response' dictionary, must have a 'succeded' field.
response = {}

try:
    #test to see if the IP address is valid. Exit if not valid 
    socket.inet_aton(test_ip)

    # Generate a 64 bytes random string
    nonce = "".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(64)])
    # Get the current timestamp as milliseconds.
    timestamp = int(datetime.now(timezone.utc).timestamp()) * 1000
    # Generate the API auth key:
    api_auth_key = "%s%s%s" % (auth_key, nonce, timestamp)
    # Convert to bytes object
    api_auth_key = api_auth_key.encode("utf-8")
    # Calculate sha256 for use in Authorization:
    api_key_hash = hashlib.sha256(api_auth_key).hexdigest()

    header = {
               'x-xdr-timestamp': str(timestamp),
               'x-xdr-nonce': nonce,
               'x-xdr-auth-id': auth_id,
               'Authorization': api_key_hash,
               'Content-Type': 'application/json'
        }

    data = {
    "request_data":{
         "filters":     [
                            { 
                                "field":"ip_list",
                                "operator":"in",
                                "value":[
                                            test_ip
                                        ]
                            }
                        ]
                    }
    }

    #convert the data to post to json
    data = json.dumps(data)

    try:
        #create a Post request and connect
        req = urllib.request.Request(url = base_url+'/public_api/v1/endpoints/get_endpoint', data = bytes(data.encode("utf-8")), headers=header, method = "POST")
        resp = urllib.request.urlopen(req)

        #For output only
        response_data = json.loads(resp.read().decode("utf-8"))
        
        if resp.getcode() == 200:
            response['succeeded'] = True
            response['result_msg'] = 'Successfully connected to Cortex API Server.\n'
            bad_chars = ["[", "]","'"]
            trimmed_response = json.loads(json.dumps(response_data['reply']['endpoints'], indent = 4))
            stroutput = ""
            if trimmed_response:
                    return_values = trimmed_response[0]
                    for key, value in return_values.items():
                        #remove bad chars from specific subfields
                        if key == 'ip' or key == 'users' or key == 'group_name' or key == 'operational_status_description':
                            value = str(value)
                            for i in bad_chars:
                                value = value.replace(i, '')
                        #replace empty values as 'None'
                        if value == '':
                            value = 'None'
                        value = str(value)
                        stroutput = stroutput + key + ": " + value + "\n"
                        #map the values to the map key
                    response['result_msg'] = stroutput
            else:
                response['result_msg'] = "=======>>>>>Cortex: Error " + test_ip + " Not Found in Cortex Database."
                logging.info(response['result_msg'])
             
        else:
            response['succeeded'] = False
            response['result_msg'] = 'Could not connect to Cortex API Server'

        logging.error('===>Ending Cortex API Server')
        
    except:
        response["error"] = "=======>>>>>Cortex: Error Unable to establish Connection"
        logging.error(response["error"])
        
except socket.error:
    response["error"] = "=======>>>>>Cortex: Error invalid IP"
    logging.error(response["error"])
  