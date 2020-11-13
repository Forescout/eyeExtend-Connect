'''
Disconnect F5 VPN Session
'''
import urllib.request
import urllib.parse
import urllib
import logging

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
# CONFIGURATION from UI Panels
P_F5_HOST = params.get('connect_f5vpn_host')
P_TOKEN = params.get('connect_authorization_token')

# Eendpont Properties
EP_SESSION_ID = params.get('connect_f5vpn_session_id')

if P_TOKEN == '':
    logging.info('ERROR: No Valid Token Stored.')
else:
    logging.info('Request to terminate F5 VPN Session ID : %s', EP_SESSION_ID)

    response = {}
    F5_DISCONNECT_URL = f'{P_F5_HOST}/mgmt/tm/apm/session/'
    # Build request
    request = urllib.request.Request(F5_DISCONNECT_URL + EP_SESSION_ID)
    request.add_header("X-F5-Auth-Token", P_TOKEN)
    request.get_method = lambda: 'DELETE'

    session_response = urllib.request.urlopen(request, context=ssl_context)
    logging.info('session_response code : %s', session_response.getcode())

    if session_response.getcode() == 200:
        # Get response body and convert to Dict

        # Like the action response, the response object must have a "succeeded" field to denote success. It can also optionally have
        # a "result_msg" field to display a custom test result message.
        response["succeeded"] = True
        response["result_msg"] = \
            f"Successfully terminated F5 VPN Session ID {EP_SESSION_ID}"
    else:
        response["succeeded"] = False
        response["result_msg"] = f"ERROR: Could not terminate F5 VPN Session ID {EP_SESSION_ID}"
