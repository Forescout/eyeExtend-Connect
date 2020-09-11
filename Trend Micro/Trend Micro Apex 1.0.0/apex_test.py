'''
Copyright © 2020 Forescout Technologies, Inc.

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
import base64
import jwt
import hashlib
import time
import json
import ssl
import urllib.request

logging.info('===>Starting apex Test Script')

# Setup the call info of the Trend Micro Apex server (server url, application id, api key)
# Server configuration fields will be available in the 'params' dictionary.
use_url_base = params['connect_apex_url']
use_application_id = params['connect_apex_appid']
use_api_key = params['connect_apex_apikey']

useRequestBody = ''
canonicalRequestHeaders = ''

# Default test path to check for API connectivity.
productServersAPIPath = '/WebApp/API/ServerResource/ProductServers'

def create_checksum(http_method, raw_url, headers, request_body):
    string_to_hash = http_method.upper() + '|' + raw_url.lower() + '|' + headers + '|' + request_body
    base64_string = base64.b64encode(hashlib.sha256(str.encode(string_to_hash)).digest()).decode('utf-8')
    return base64_string

def create_jwt_token(appication_id, api_key, http_method, raw_url, headers, request_body,
                     iat=time.time(), algorithm='HS256', version='V1'):
    checksum = create_checksum(http_method, raw_url, headers, request_body)
    payload = {'appid': appication_id,
               'iat': iat,
               'version': version,
               'checksum': checksum}
    token = jwt.encode(payload, api_key, algorithm=algorithm).decode('utf-8')
    return token

jwt_token = create_jwt_token(use_application_id, use_api_key, 'GET',
                              productServersAPIPath, canonicalRequestHeaders,
                               useRequestBody, iat=time.time())
headers = {'Authorization': 'Bearer ' + jwt_token}

# Return the 'response' dictionary, must have a 'succeded' field.
response = {}
message = []

logging.debug('Attempting to test Apex connection with the following parameters: url={} application ID={} API key=*****'.format(
use_url_base ,use_application_id))

# Attempt to connect to base url for simple network connectivity
message.append('Testing network connectivity to server...')
try:
    request = urllib.request.urlopen(use_url_base, timeout=5, context=ssl_context)
except urllib.error.URLError as e:
    response['succeeded'] = False
    response['result_msg'] = 'Unable to connect to server: ' + str((e.reason))
    logging.debug('Test connection failed to server: ' + str((e.reason)))
else: #Continue to attempt to retrieve data from API for Product Server)
    message.append('Attempting to query server API...')
    request2 = urllib.request.Request(use_url_base + productServersAPIPath, method='GET', headers=headers)
    try:
        resp = urllib.request.urlopen(request2, context=ssl_context)
    except urllib.error.HTTPError as e: #Handle any connection errors
        body = e.read().decode()
        try:
            e_json = json.loads(body)
        except ValueError as err: #Catch for response which is not in JSON format
            response['succeeded'] = False
            response['result_msg'] = 'Destination and port are available but no JSON response. ' + str((err.msg))
            logging.debug('Test connection failed to server API - no JSON Response: ' + str((err.msg)))
        else: #Read error codes in JSON format
            response['succeeded'] = False
            response['result_msg'] = 'Could not connect to Apex Central server. Error Code: ' + str(e_json['result_code']) + ' Reason: ' + e_json['result_description']
            logging.debug('Test connection failed to server API: ' + str(e_json['result_code']) + ' Reason: ' + e_json['result_description'])
    else: #No technical errors, check for API response
        request_response = json.loads(resp.read())
        if request_response['result_code'] == 1:
            response['succeeded'] = True
            response['result_msg'] = 'Successfully connected and retrieved API data.'
            logging.debug('Test connection succeeded to server.')
        else: #API connection is not successful
            response['succeeded'] = False
            response['result_msg'] = 'Could not connect to Apex Central Server. Reason:' + request_response['result_description']
            logging.debug('Could not connect to Apex Central Server. Reason:' + request_response['result_description'])

logging.info('===>Ending apex Test Script')
