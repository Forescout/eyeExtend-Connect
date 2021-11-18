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
def get_wireless_by_mac(passed_bearer_token):
    '''
    Get a list of Wireless Clients
    return wireless dict
    '''
    aruba_wireless = {}
    # Convert Forescout MAC to Aruba MAC (add colons)
    aruba_macaddr = ':'.join(P_MAC[i:i + 2] for i in range(0, 12, 2))

    # Build  URL
    wireless_url_request = f'https://{P_STEP1_AUTH_URL}/monitoring/v1/clients/wireless?access_token={passed_bearer_token}&macaddr={aruba_macaddr}'
    logging.debug('wireless_url_request : %s', wireless_url_request)

    aps_request = urllib.request.Request(wireless_url_request)

    try:
        wireless_response = OPENER.open(aps_request)

        if wireless_response.getcode() == 200:
            # Interested in response body auth_code
            # Convert JSON to dict
            aruba_wireless = json.loads(wireless_response.read())

    except urllib.error.HTTPError as error:
        logging.debug('Error : step3_get_auth_code() did not get auth_code : %s', error.read())

    return aruba_wireless


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
ARUBA_CLIENT_WIRELESS_TO_FS_MAP = {
    #'macaddr': 'mac',
    #'ip_address': 'ip',
    'associated_device': 'connect_arubacentral_ap_serial',
    'site': 'connect_arubacentral_site',
    'group_name': 'connect_arubacentral_group_name',
    'associated_device_mac': 'connect_arubacentral_client_wireless_associated_device_mac',
    'band': 'connect_arubacentral_client_wireless_band',
    'channel': 'connect_arubacentral_client_wireless_channel',
    'connection': 'connect_arubacentral_client_wireless_connection',
    'encryption_method': 'connect_arubacentral_client_wireless_encryption_method',
    'group_id': 'connect_arubacentral_client_wireless_group_id',
    'health': 'connect_arubacentral_client_wireless_health',
    'ht_type': 'connect_arubacentral_client_wireless_ht_type',
    'manufacturer': 'connect_arubacentral_client_wireless_manufacturer',
    'maxspeed': 'connect_arubacentral_client_wireless_maxspeed',
    'name': 'connect_arubacentral_client_wireless_name',
    'network': 'connect_arubacentral_client_wireless_network',
    'os_type': 'connect_arubacentral_client_wireless_os_type',
    'phy_type': 'connect_arubacentral_client_wireless_phy_type',
    'radio_mac': 'connect_arubacentral_client_wireless_radio_mac',
    'radio_number': 'connect_arubacentral_client_wireless_radio_number',
    'snr': 'connect_arubacentral_client_wireless_snr',
    'speed': 'connect_arubacentral_client_wireless_speed',
    'swarm_id': 'connect_arubacentral_client_wireless_swarm_id',
    'username': 'connect_arubacentral_client_wireless_username',
    'vlan': 'connect_arubacentral_client_wireless_vlan'
    }

# Forescout response
response = {}

if STEP4_BEARER_TOKEN:
    # Make sure we have a mac address for endpoint
    if P_MAC is not None and P_MAC != '':
        #######
        # Get Wireless Client
        #######
        WIRELESS_CLIENTS = get_wireless_by_mac(STEP4_BEARER_TOKEN)
        logging.debug('MAC: %s :Wireless Client Count : %s', P_MAC, len(WIRELESS_CLIENTS['clients']))

        # Something went wrong if count is not 1
        if WIRELESS_CLIENTS['count'] == 1:
            ########################################
            # Forescout Properties for endpoint(s)
            ########################################
            fs_endpoint_properties = {}

            for key, value in ARUBA_CLIENT_WIRELESS_TO_FS_MAP.items():

                # Build Properties verify key exists
                if key in WIRELESS_CLIENTS['clients'][0].keys():

                    # Need to remove colon from mac address(s)
                    if key in ('associated_device_mac', 'radio_mac'):
                        fs_endpoint_properties[value] = WIRELESS_CLIENTS['clients'][0][key].replace(':', '')
                    else:
                        fs_endpoint_properties[value] = WIRELESS_CLIENTS['clients'][0][key]

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
