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
Poll Aruba Central for AP, Clients
'''
import logging
import urllib
import urllib.request
import urllib.parse
import json
#from http.cookies import SimpleCookie

#######
# FUNCTIONS
#######
def get_wired_by_mac(passed_bearer_token):
    '''
    Get a list of Wireless Clients
    return wired dict
    '''
    aruba_wired = {}
    # Convert Forescout MAC to Aruba MAC (add colons)
    aruba_macaddr = ':'.join(P_MAC[i:i + 2] for i in range(0, 12, 2))

    # Build  URL
    wired_url_request = f'https://{P_STEP1_AUTH_URL}/monitoring/v1/clients/wired?access_token={passed_bearer_token}&macaddr={aruba_macaddr}'
    logging.debug('wired_url_request : %s', wired_url_request)

    wired_request = urllib.request.Request(wired_url_request)

    try:
        wired_response = OPENER.open(wired_request)

        if wired_response.getcode() == 200:
            # Interested in response body auth_code
            # Convert JSON to dict
            aruba_wired = json.loads(wired_response.read())

    except urllib.error.HTTPError as error:
        logging.debug('Error : step3_get_auth_code() did not get auth_code : %s', error.read())

    return aruba_wired


#######
# END OF FUNCTIONS
#######

# Panel AUTH Details
STEP4_BEARER_TOKEN = params.get('connect_authorization_token')
logging.debug('STEP4_BEARER_TOKEN : %s', STEP4_BEARER_TOKEN)

P_STEP1_AUTH_URL = params.get('connect_arubacentral_api_domain_gateway')
P_MAC = params.get('mac')

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

#######
# MAPPINGS
#######
ARUBA_CLIENT_WIRED_TO_FS_MAP = {
    #'macaddr': 'mac',
    #'ip_address': 'ip',
    'associated_device': 'connect_arubacentral_ap_serial',
    'site': 'connect_arubacentral_site',
    'group_name': 'connect_arubacentral_group_name',
    'associated_device_mac': 'connect_arubacentral_client_wired_associated_device_mac',
    'group_id': 'connect_arubacentral_client_wired_group_id',
    'interface_mac': 'connect_arubacentral_client_wired_interface_mac',
    'interface_port': 'connect_arubacentral_client_wired_interface_port',
    'manufacturer': 'connect_arubacentral_client_wired_manufacturer',
    'name': 'connect_arubacentral_client_wired_name',
    'os_type': 'connect_arubacentral_client_wired_os_type',
    'swarm_id': 'connect_arubacentral_client_wired_swarm_id',
    'username': 'connect_arubacentral_client_wired_username',
    'vlan': 'connect_arubacentral_client_wired_vlan'
    }

# Forescout response
response = {}

if STEP4_BEARER_TOKEN:
    # Make sure we have a mac address for endpoint
    if P_MAC is not None and P_MAC != '':
        #######
        # Get Wired Client
        #######
        WIRED_CLIENTS = get_wired_by_mac(STEP4_BEARER_TOKEN)
        logging.info('MAC: %s :Wired Client Count : %s', P_MAC, len(WIRED_CLIENTS['clients']))

        if WIRED_CLIENTS['count'] == 1:
            ########################################
            # Forescout Properties for endpoint(s)
            ########################################
            fs_endpoint_properties = {}

            for key, value in ARUBA_CLIENT_WIRED_TO_FS_MAP.items():

                # Build Properties verify key exists
                if key in WIRED_CLIENTS['clients'][0].keys():

                    # Need to remove colon from mac address(s)
                    if key in ('interface_mac', 'associated_device_mac'):
                        fs_endpoint_properties[value] = WIRED_CLIENTS['clients'][0][key].replace(':', '')
                    else:
                        fs_endpoint_properties[value] = WIRED_CLIENTS['clients'][0][key]

            logging.debug('properties =  %s', fs_endpoint_properties)
            # Update Forescout properties for endpoint
            response['properties'] = fs_endpoint_properties
        else:
            response['error'] = f'Client Count not equal to 1 or MAC address not found: mac {P_MAC}'
    else:
        response["error"] = "No MAC address for this device"
else:
    logging.debug("No Valid Bearer Token : MAC %s", P_MAC)
    response['error'] = f'No Valid Bearer Token : MAC {P_MAC}'
    response["succeeded"] = False
