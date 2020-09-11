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

# Use this region to setup the call info of the TMCM server (server url, application id, api key)
use_url_base = params['connect_apex_url']
use_application_id = params['connect_apex_appid']
use_api_key = params['connect_apex_apikey']
useRequestBody = ''
id = params.get('connect_apex_id')
ip = params.get('ip')

# currently Canonical-Request-Headers will always be empty
canonicalRequestHeaders = ''
productAgentAPIPath = '/WebApp/API/AgentResource/ProductAgents'

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

logging.debug('apex: Attempting to restore isolated client using following parameters: url={} application ID={} Client ID={} API path={} '.format(
use_url_base ,use_application_id,id,productAgentAPIPath))
response = {}

if id is not None and id != "":
    useRequestBody = json.dumps({'entity_id': id, 'act': 'cmd_restore_isolated_agent', 'allow_multiple_match': False})

    jwt_token = create_jwt_token(use_application_id, use_api_key, 'POST',
                                  productAgentAPIPath,
                                  canonicalRequestHeaders, useRequestBody, iat=time.time())
    headers = {'Authorization': 'Bearer ' + jwt_token}
    useRequestBodyBytes = bytes(useRequestBody, encoding='utf8')
    request = urllib.request.Request(use_url_base + productAgentAPIPath, method='POST', data=useRequestBodyBytes, headers=headers)
    try:
        resp = urllib.request.urlopen(request, timeout=5, context=ssl_context)
        request_response = json.loads(resp.read())
        if request_response['result_code'] == 1:
            response["succeeded"]= True
            response['result_msg'] = request_response['result_description']
            logging.debug('apex: Restoration of isolated client succedded for, ' + ip)
        else:
            response["succeeded"]= False
            response["error"] = "Error restoring isolated client: unable to connect to server, please test settings"
            logging.info('apex: Error restoring isolated client for ip address: ' + ip + ', unable to connect to server: ' + str(request_response['result_description']))
    except urllib.error.URLError as e:
        response['succeeded'] = False
        response["error"] = "Error restoring isolated client: unable to connect to server, please test settings"
        logging.info('apex: Error restoring isolated client for ip address: ' + ip + ', unable to connect to server: ' + str((e.reason)))
else:
    response["succeeded"]= False
    response["error"] = "No Apex ID for client."
    logging.info('apex: No Apex ID found to execute for client: ' + ip)
