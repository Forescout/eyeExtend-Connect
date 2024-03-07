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

'''
Aruba Central Keep Bearer Token Updated
'''
	
import logging
import urllib
import urllib.request
import urllib.parse
import json
from http.cookies import SimpleCookie

# Panel AUTH Details
P_CLIENTID = params.get('connect_arubacentral_clientid')
P_CLIENT_SECRET = params.get('connect_arubacentral_client_secret')
P_STEP1_AUTH_URL = params.get('connect_arubacentral_api_domain_gateway')
P_STEP1_USERNAME = params.get('connect_arubacentral_step1_username')
P_STEP1_PASSWORD = params.get('connect_arubacentral_step1_password')
P_CUSTOMERID = params.get('connect_arubacentral_customerid')

#######
# Build HTTP Handlers
#   Cookie Jar
#   HTTPS Context
#   Debug
#######
HANDLER = []
HANDLER.append(urllib.request.HTTPCookieProcessor())
HANDLER.append(urllib.request.HTTPSHandler(context=ssl_context))
# Debug level does not seem to work with the logging module
# HANDLER.append(urllib.request.HTTPSHandler(debuglevel=10))
OPENER = urllib.request.build_opener(*HANDLER)

#######
# FUNCTIONS
#######


def step1_get_csrftoken():
    '''
    Get the csrftoken
    '''
    csrftoken = None
    # Build Body
    step1_request_body = {'username': P_STEP1_USERNAME,
                          'password': P_STEP1_PASSWORD
                          }
    # Convert to JSON and bytes
    json_body = json.dumps(step1_request_body)
    json_body_bytes = json_body.encode('utf8')

    # Build AUTH URL + ClientID parameter
    step1_url_request = f'https://{P_STEP1_AUTH_URL}/oauth2/authorize/central/api/login?client_id={P_CLIENTID}'

    step1_request = urllib.request.Request(step1_url_request, method="POST")
    step1_request.add_header('Content-Type', 'application/json')

    try:
        step1_response = OPENER.open(step1_request, data=json_body_bytes)

        if step1_response.getcode() == 200:
            # Interested in csrftoken
            set_cookie = step1_response.info()['Set-Cookie']
            cookie = SimpleCookie()
            cookie.load(set_cookie)
            csrftoken = cookie['csrftoken'].value

    except urllib.error.HTTPError as error:
        logging.debug('Error : step1_get_csrftoken() did not get csfrtoken : %s', error)

    logging.debug('step1_get_csrftoken()  : %s', csrftoken)
    return csrftoken


def step3_get_auth_code(passed_csrftoken, customer_id):
    '''
    Get auth_code using csrftoken from step1
    '''

    step3_auth_code = None
    # Build Body
    step3_request_body = {
        'client_id': P_CLIENTID,
        'customer_id': customer_id  # Include the customer ID here
    }

    # Convert to JSON and bytes
    json_body = json.dumps(step3_request_body)
    json_body_bytes = json_body.encode('utf8')

    # Build URL
    step3_url_request = f'https://{P_STEP1_AUTH_URL}/oauth2/authorize/central/api/'
    step3_url_request = f'{step3_url_request}?client_id={P_CLIENTID}&response_type=code&scope=all'

    headers = {
        'Content-Type': 'application/json',
        'X-csrf-token': passed_csrftoken
    }

    step3_request = urllib.request.Request(step3_url_request, headers=headers, method="POST")

    try:
        step3_response = OPENER.open(step3_request, data=json_body_bytes)

        if step3_response.getcode() == 200:
            # Interested in response body auth_code
            step3_response_body = json.loads(step3_response.read())
            step3_auth_code = step3_response_body['auth_code']

    except urllib.error.HTTPError as error:
        logging.debug('Error : step3_get_auth_code() did not get auth_code : %s', error.read())

    logging.debug('step3_get_auth_code()  : %s', step3_auth_code)
    return step3_auth_code


def step4_get_bearer_token(passed_csrftoken, passed_auth_code):
    '''
    Get bearer token
    '''
    step4_bearer_token = None
    # Build Body
    step4_request_body = {'client_id': P_CLIENTID}

    # Convert to JSON and bytes
    json_body = json.dumps(step4_request_body)
    json_body_bytes = json_body.encode('utf8')

    # Build URL
    step4_url_request = f'https://{P_STEP1_AUTH_URL}/oauth2/token/'
    step4_url_request = f'{step4_url_request}?client_id={P_CLIENTID}&client_secret={P_CLIENT_SECRET}'
    step4_url_request = f'{step4_url_request}&grant_type=authorization_code&code={passed_auth_code}'

    headers = {
        'Content-Type': 'application/json',
        'X-csrf-token': passed_csrftoken
    }

    step4_request = urllib.request.Request(step4_url_request, headers=headers, method="POST")

    try:
        step4_response = OPENER.open(step4_request, data=json_body_bytes)

        if step4_response.getcode() == 200:
            # Interested in response body auth_code
            step4_response_body = json.loads(step4_response.read())
            step4_bearer_token = step4_response_body['access_token']

    except urllib.error.HTTPError as error:
        logging.debug('Error : step4_get_bearer_token() did not get bearer token : %s', error.read())

    logging.debug('step4_get_bearer_token()  : %s', step4_bearer_token)
    return step4_bearer_token


#######
# END OF FUNCTIONS
#######
# Forescout response
response = {}

# Step-1
STEP1_CSRFTOKEN = step1_get_csrftoken()
logging.info('Step1 Get CSRFTOKEN')
logging.debug('STEP1_CSRFTOKEN : %s', STEP1_CSRFTOKEN)

# Step-2 NOT IMPLEMENTED (See note above)

# Step-3
if STEP1_CSRFTOKEN:
    logging.info('Step3 Get AUTH_CODE')
    STEP3_AUTH_CODE = step3_get_auth_code(STEP1_CSRFTOKEN, P_CUSTOMERID)
    logging.debug('STEP3_AUTH_CODE : %s', STEP3_AUTH_CODE)
else:
    logging.debug('Step-3 failed we do not have a CSRFTOKEN')

# Step-4
if STEP3_AUTH_CODE:
    logging.info('Step4 Get BEARER Token')
    STEP4_BEARER_TOKEN = step4_get_bearer_token(STEP1_CSRFTOKEN, STEP3_AUTH_CODE)
    logging.debug('STEP4_BEARER_TOKEN : %s', STEP4_BEARER_TOKEN)
    #
    if STEP4_BEARER_TOKEN:
        response['token'] = STEP4_BEARER_TOKEN
    else:
        response['error'] = 'Failed to get bearer token in step-4'
        response['token'] = ''
else:
    logging.info('Step-4 failed we do not have a AUTH CODE')
    #
    response['error'] = 'Failed to get bearer token'
    response['token'] = ''
