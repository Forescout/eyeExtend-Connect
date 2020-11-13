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
Test Connect To F5
'''
import urllib.request
import urllib.parse
import urllib
import json
import logging

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
# CONFIGURATION from UI Panels
P_F5_HOST = params.get('connect_f5vpn_host')
P_TOKEN = params.get('connect_authorization_token')

#############
# FUNCTIONS
#############
### FUNCTION END ###

if P_TOKEN is None or P_TOKEN == "":
    response = {}
    endpoint_data = {}
    logging.debug('Error : No Valid Token Stored. Check f5vpn_authorization.py outputs')
    response["succeeded"] = False
    response["result_msg"] = "No valid token stored."
else:
    try:
        response = {}
        F5_SESSIONS_URL = f'{P_F5_HOST}/mgmt/tm/apm/access-info'
        logging.info('Session URL : %s', F5_SESSIONS_URL)

        # Build request
        request = urllib.request.Request(F5_SESSIONS_URL)
        request.add_header("X-F5-Auth-Token", P_TOKEN)

        session_response = urllib.request.urlopen(request, context=ssl_context)
        logging.info('session_response code : %s', session_response.getcode())

        if session_response.getcode() == 200:
            # Get response body and convert to Dict
            SESSION_BODY = session_response.read()
            F5_SESSION_DATA = json.loads(SESSION_BODY)

            # Count No of Sessions
            NO_SESSIONS = 0
            if 'entries' in F5_SESSION_DATA:
                NO_SESSIONS = len(F5_SESSION_DATA['entries'])

            # Like the action response, the response object must have a "succeeded" field to denote success. It can also optionally have
            # a "result_msg" field to display a custom test result message.
            response["succeeded"] = True
            response["result_msg"] = f"Successfully connected. No. of VPN Sessions {NO_SESSIONS}"
        else:
            response["succeeded"] = False
            response["result_msg"] = f"Could not connect to f5vpn server {F5_SESSIONS_URL}"
    except Exception as error:
        errormsg = f"Error connecting to f5vpn server: request {F5_SESSIONS_URL}, error: {error}"
        logging.info(f'Error : {errormsg}')
        response["result_msg"] = errormsg
