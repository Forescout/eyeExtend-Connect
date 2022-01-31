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
def get_ap_by_mac(passed_bearer_token):
    '''
    Get a list of APs
    return aps dict
    '''

    aruba_aps = {}
    # Convert Forescout MAC to Aruba MAC (add colons)
    aruba_macaddr = ':'.join(P_MAC[i:i + 2] for i in range(0, 12, 2))

    # Build  URL with MAC
    aps_url_request = f'https://{P_STEP1_AUTH_URL}/monitoring/v1/aps?access_token={passed_bearer_token}&macaddr={aruba_macaddr}'
    logging.debug('aps_url_request : %s', aps_url_request)

    aps_request = urllib.request.Request(aps_url_request)

    try:
        aps_response = OPENER.open(aps_request)

        if aps_response.getcode() == 200:
            # Interested in response body auth_code
            # Convert JSON to dict
            aruba_aps = json.loads(aps_response.read())

    except urllib.error.HTTPError as error:
        logging.debug('Error : step3_get_auth_code() did not get auth_code : %s', error.read())
        #logging.debug('Params :  : %s', params)

    return aruba_aps

#######
# END OF FUNCTIONS
#######

# SSL Context
#P_SSL_CONTEXT = ssl_context

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
ARUBA_AP_TO_FS_MAP = {
    #'macaddr': 'mac',
    #'ip_address': 'ip',
    'serial': 'connect_arubacentral_ap_serial',
    'site': 'connect_arubacentral_site',
    'group_name': 'connect_arubacentral_group_name',
    'ap_deployment_mode': 'connect_arubacentral_ap_deployment_mode',
    'ap_group': 'connect_arubacentral_ap_group',
    'cluster_id': 'connect_arubacentral_ap_cluster_id',
    'firmware_version': 'connect_arubacentral_ap_firmware_version',
    'labels': 'connect_arubacentral_ap_labels',
    'last_modified': 'connect_arubacentral_ap_last_modified',
    'mesh_role': 'connect_arubacentral_ap_mesh_role',
    'model': 'connect_arubacentral_ap_model',
    'name': 'connect_arubacentral_ap_name',
    'public_ip_address': 'connect_arubacentral_ap_public_ip_address',
    'radios': 'connect_arubacentral_ap_radios',
    'status': 'connect_arubacentral_ap_status',
    'subnet_mask': 'connect_arubacentral_ap_subnet_mask',
    'swarm_id': 'connect_arubacentral_ap_swarm_id',
    'swarm_master': 'connect_arubacentral_ap_swarm_master'
    }

# Forescout response
response = {}

if STEP4_BEARER_TOKEN:
    # Make sure we have a mac address for endpoint
    if P_MAC is not None and P_MAC != '':
        #######
        # Get AP
        #######
        ACCESS_POINTS = get_ap_by_mac(STEP4_BEARER_TOKEN)
        logging.info('MAC: %s :Access Point Count : %s', P_MAC, len(ACCESS_POINTS['aps']))

        # Something went wrong if count is not 1
        if ACCESS_POINTS['count'] == 1:
            ########################################
            # Forescout Properties for endpoint(s)
            ########################################
            fs_endpoint_properties = {}
            for key, value in ARUBA_AP_TO_FS_MAP.items():

                # Build Properties verify key exists
                if key in ACCESS_POINTS['aps'][0].keys():

                    # replace colon in radio mac address
                    if key == 'radios':
                        # iterate radios removing colon from mac address
                        for radio in ACCESS_POINTS['aps'][0]['radios']:
                            radio['macaddr'] = radio['macaddr'].replace(':', '')

                    # Add properties
                    fs_endpoint_properties[value] = ACCESS_POINTS['aps'][0][key]

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
