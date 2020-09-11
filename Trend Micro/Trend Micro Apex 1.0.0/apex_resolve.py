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

apex_to_ct_props_map = {
    "product": "connect_apex_products",
    "entity_id": "connect_apex_id",
    "managing_server_id": "connect_apex_serverid",
    "ad_domain": "connect_apex_domain",
    "isolation_status": "connect_apex_isolationstatus",
    "capabilities": "connect_apex_capabilities"
}

# Use this region to setup the call info of the apex server (server url, application id, api key)
use_url_base = params['connect_apex_url']
use_application_id = params['connect_apex_appid']
use_api_key = params['connect_apex_apikey']

#function to create checksum for JWT
def create_checksum(http_method, raw_url, headers, request_body):
    string_to_hash = http_method.upper() + '|' + raw_url.lower() + '|' + headers + '|' + request_body
    base64_string = base64.b64encode(hashlib.sha256(str.encode(string_to_hash)).digest()).decode('utf-8')
    return base64_string

#function to create java web token required for each query to API
def create_jwt_token(appication_id, api_key, http_method, raw_url, headers, request_body,
                     iat=time.time(), algorithm='HS256', version='V1'):
    checksum = create_checksum(http_method, raw_url, headers, request_body)
    payload = {'appid': appication_id,
               'iat': iat,
               'version': version,
               'checksum': checksum}
    token = jwt.encode(payload, api_key, algorithm=algorithm).decode('utf-8')
    return token

response = {}

if "ip" in params:
    useRequestBody = ''
    ip = params.get('ip')

    # currently Canonical-Request-Headers will always be empty
    canonicalRequestHeaders = ''
    #path to API for Apex Central server for retrieving agent product list
    productAgentAPIPath = '/WebApp/API/AgentResource/ProductAgents'
    useQueryString = '?ip_address=' + ip

    #create the jwt
    jwt_token = create_jwt_token(use_application_id, use_api_key, 'GET',
                              productAgentAPIPath + useQueryString,
                              canonicalRequestHeaders, useRequestBody, iat=time.time())

    #establish header and append token
    headers = {'Authorization': 'Bearer ' + jwt_token}
    logging.debug('apex: Attempting to resolve client properties using following parameters: url={} application ID={} Client IP={} API path={} '.format(
    use_url_base ,use_application_id,ip,productAgentAPIPath))
    ip_addr = ip
    properties = {}
    logging.debug("apex: Resolving properties for ip address: " + ip_addr)
    # Get device information
    try:
        request = urllib.request.Request(use_url_base + productAgentAPIPath + useQueryString, method='GET', headers=headers)
        resp = urllib.request.urlopen(request, timeout=5, context=ssl_context)
        request_response = json.loads(resp.read())
        if request_response['result_code'] == 1:
            if len(request_response["result_content"]) == 0: #empty record
                response['succeeded'] = False
                response['error'] = 'No record exists for client'
                logging.info('apex: No record exists for client: ' + ip_addr)
            else: # retrieval is successful
                return_values = request_response["result_content"][0]
                for key, value in return_values.items():
                    if key in apex_to_ct_props_map:
                        properties[apex_to_ct_props_map[key]] = value
                response["properties"] = properties
                response['succeeded'] = True
                logging.debug('apex: Properties restrieved for client, ' + ip_addr + ' : ' + str(request_response["result_content"]))
        else:
            response['succeeded'] = False
            response['error'] = "Error resolving client properties: unable to connect to server, please test settings"
            logging.info('apex: Error resolving client properties for ip address: ' + ip_addr + ', unable to connect to server: ' + str(request_response['result_description']))
    except urllib.error.URLError as e:
        response['succeeded'] = False
        response["error"] = "Error resolving client properties: unable to connect to server, please test settings"
        logging.info('apex: Error resolving client properties for ip address: ' + ip_addr + ', unable to connect to server: ' + str((e.reason)))
else:
    response["succeeded"] = False
    response["error"] = "No IP address found to query for client."
    logging.info('apex: No IP address found to query for client.')
