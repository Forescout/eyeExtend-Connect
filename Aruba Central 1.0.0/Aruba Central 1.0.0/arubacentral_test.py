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
Test connection to Aruba Central
'''
import logging
import urllib
import urllib.request
import urllib.parse
import json
#from http.cookies import SimpleCookie

# Panel AUTH Details
STEP4_BEARER_TOKEN = params.get('connect_authorization_token')
P_STEP1_AUTH_URL = params.get('connect_arubacentral_api_domain_gateway')

#######
# Build HTTP Handerlers
#   Cookie Jar
#   HTTPS Context
#   Debug
#######
HANDLER = []
HANDLER.append(urllib.request.HTTPCookieProcessor())
HANDLER.append(urllib.request.HTTPSHandler(context=ssl_context))
# Debug level does not seem to work with logging module
#HANDLER.append(urllib.request.HTTPSHandler(debuglevel=10))
OPENER = urllib.request.build_opener(*HANDLER)

response = {}

if STEP4_BEARER_TOKEN:
    aruba_sites = {}

    # Build  URL
    sites_url_request = f'https://{P_STEP1_AUTH_URL}/central/v2/sites?access_token={STEP4_BEARER_TOKEN}'

    sites_request = urllib.request.Request(sites_url_request)

    try:
        sites_response = OPENER.open(sites_request)

        if sites_response.getcode() == 200:
            # Interested in response body auth_code
            # Convert JSON to dict
            aruba_sites = json.loads(sites_response.read())

            SITE_COUNT = aruba_sites['count']

            response['succeeded'] = True
            response['result_msg'] = f'Successfully connected. No of Sites {SITE_COUNT}'

    except urllib.error.HTTPError as error:
        logging.debug('Error : STEP4_BEARER_TOKEN = %s verify we have a token : %s', STEP4_BEARER_TOKEN, error.read())

        response['succeeded'] = False
        response['result_msg'] = 'Could not connect to Aruba Central server.'
else:
    logging.debug("No Valid Bearer Token")
    response['result_msg'] = 'No Valid Bearer Token'
    response["succeeded"] = False
