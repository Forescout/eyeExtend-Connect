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
def get_aps(passed_bearer_token, passed_page_limit, passed_offset):
    '''
    Get a list of APs
    return aps dict
    '''
    aruba_aps = {}

    # Build  URL
    aps_url_request = f'https://{P_STEP1_AUTH_URL}/monitoring/v1/aps?access_token={passed_bearer_token}&limit={passed_page_limit}&offset={passed_offset}'
    logging.debug('aps_url_request : %s', aps_url_request)

    aps_request = urllib.request.Request(aps_url_request)

    try:
        aps_response = OPENER.open(aps_request)

        if aps_response.getcode() == 200:
            # Interested in response body auth_code
            # Convert JSON to dict
            aruba_aps = json.loads(aps_response.read())

    except urllib.error.HTTPError as error:
        logging.debug('Error : get_aps() Failed to get AP devices : %s', error.read())

    return aruba_aps

def get_wireless_clients(passed_bearer_token, passed_page_limit, passed_offset):
    '''
    Get a list of Wireless Clients
    return wireless dict
    '''
    aruba_wireless = {}

    # Build  URL
    wireless_url_request = f'https://{P_STEP1_AUTH_URL}/monitoring/v1/clients/wireless?access_token={passed_bearer_token}&limit={passed_page_limit}&offset={passed_offset}'
    logging.debug('aps_url_request : %s', wireless_url_request)

    aps_request = urllib.request.Request(wireless_url_request)

    try:
        wireless_response = OPENER.open(aps_request)

        if wireless_response.getcode() == 200:
            # Interested in response body auth_code
            # Convert JSON to dict
            aruba_wireless = json.loads(wireless_response.read())

    except urllib.error.HTTPError as error:
        logging.debug('Error : get_wireless_clients() Failed to get wireless devices : %s', error.read())

    return aruba_wireless


def get_wired_clients(passed_bearer_token, passed_page_limit, passed_offset):
    '''
    Get a list of Wireless Clients
    return wired dict
    '''
    aruba_wired = {}

    # Build  URL
    wired_url_request = f'https://{P_STEP1_AUTH_URL}/monitoring/v1/clients/wired?access_token={passed_bearer_token}&limit={passed_page_limit}&offset={passed_offset}'
    logging.debug('aps_url_request : %s', wired_url_request)

    wired_request = urllib.request.Request(wired_url_request)

    try:
        wired_response = OPENER.open(wired_request)

        if wired_response.getcode() == 200:
            # Interested in response body auth_code
            # Convert JSON to dict
            aruba_wired = json.loads(wired_response.read())

    except urllib.error.HTTPError as error:
        logging.debug('Error : get_wired_clients() Failed to get wired devices : %s', error.read())

    return aruba_wired


#######
# END OF FUNCTIONS
#######

# Panel AUTH Details
STEP4_BEARER_TOKEN = params.get('connect_authorization_token')
logging.debug('STEP4_BEARER_TOKEN : %s', STEP4_BEARER_TOKEN)

P_STEP1_AUTH_URL = params.get('connect_arubacentral_api_domain_gateway')

P_GET_APS = params.get('connect_arubacentral_discover_access_points')
P_GET_WIRELESS = params.get('connect_arubacentral_discover_wireless_clients')
P_GET_WIRED = params.get('connect_arubacentral_discover_wired_clients')
# All panels values are stored as strings, convert to INTEGER
P_PAGE_LIMIT = int(params.get('connect_arubacentral_page_limit'))

logging.debug('P_GET_APS : %s', P_GET_APS)
logging.debug('P_GET_WIRELESS : %s', P_GET_WIRELESS)
logging.debug('P_GET_WIRED : %s', P_GET_WIRED)
logging.debug('P_PAGE_LIMIT : %s', P_PAGE_LIMIT)

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
    'macaddr': 'mac',
    'ip_address': 'ip',
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

ARUBA_CLIENT_WIRELESS_TO_FS_MAP = {
    'macaddr': 'mac',
    'ip_address': 'ip',
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

ARUBA_CLIENT_WIRED_TO_FS_MAP = {
    'macaddr': 'mac',
    'ip_address': 'ip',
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

    response = {}
    fs_endpoints = []

    #######
    # Get AP's
    #######
    if P_GET_APS == 'true':

        # Used for REQUEST Pagination
        COUNT = 0
        OFFSET = 0

        # Start of REQUEST Pagination
        while True:
            ACCESS_POINTS = get_aps(STEP4_BEARER_TOKEN, P_PAGE_LIMIT, OFFSET)
            LENGTH_APS = len(ACCESS_POINTS.get('aps'))
            logging.debug('No. APs : %s', LENGTH_APS)

            for ap in ACCESS_POINTS['aps']:
                ########################################
                # Forescout Properties for endpoint(s)
                ########################################
                fs_endpoint = {}
                fs_endpoint_properties = {}

                for key, value in ARUBA_AP_TO_FS_MAP.items():
                    # Build Properties verify key exists
                    if key in ap.keys():
                        # Get IP and MAC
                        if key in ('ip_address', 'macaddr'):
                            if key == 'macaddr':
                                # remove colon from mac address
                                fs_endpoint["mac"] = ap['macaddr'].replace(':', '')
                            else:
                                fs_endpoint["ip"] = ap['ip_address']
                            continue

                        # Remove colon from radio MAC address
                        if key == 'radios':
                            # iterate radios removing colon from mac address
                            for radio in ap['radios']:
                                radio['macaddr'] = radio['macaddr'].replace(':', '')

                        # Add properties
                        fs_endpoint_properties[value] = ap[key]

                    fs_endpoint['properties'] = fs_endpoint_properties

                # Append
                fs_endpoints.append(fs_endpoint)

            # REQUEST Pagination checks
            if LENGTH_APS < P_PAGE_LIMIT:
                LOG_MESSAGE = f'PAGINATION BREAK APS Length : {LENGTH_APS} : P_PAGE_SIZE : {P_PAGE_LIMIT} : offset : {OFFSET}'
                logging.debug(LOG_MESSAGE)
                break

            # Increment REQUEST Pagination
            COUNT += 1
            OFFSET = P_PAGE_LIMIT * COUNT

    #######
    # Get Wireless Clients
    #######
    if P_GET_WIRELESS == 'true':

        # Used for REQUEST Pagination
        COUNT = 0
        OFFSET = 0

        # Start of REQUEST Pagination
        while True:

            WIRELESS_CLIENTS = get_wireless_clients(STEP4_BEARER_TOKEN, P_PAGE_LIMIT, OFFSET)
            LENGTH_CLIENTS = len(WIRELESS_CLIENTS.get('clients'))
            logging.debug('No. Wireless Clients : %s', LENGTH_CLIENTS)

            for client in WIRELESS_CLIENTS['clients']:
                ########################################
                # Forescout Properties for endpoint(s)
                ########################################
                fs_endpoint = {}
                fs_endpoint_properties = {}

                for key, value in ARUBA_CLIENT_WIRELESS_TO_FS_MAP.items():
                    # Build Properties verify key exists
                    if key in client.keys():
                        # Get IP and MAC
                        if key in ('ip_address', 'macaddr'):
                            if key == 'macaddr':
                                # remove colon from mac address
                                fs_endpoint["mac"] = client['macaddr'].replace(':', '')
                            else:
                                fs_endpoint["ip"] = client['ip_address']
                            continue

                        # Need to remove colon from mac address(s)
                        if key in ('associated_device_mac', 'radio_mac'):
                            fs_endpoint_properties[value] = client[key].replace(':', '')
                        else:
                            fs_endpoint_properties[value] = client[key]

                    fs_endpoint['properties'] = fs_endpoint_properties

                # Append
                fs_endpoints.append(fs_endpoint)

            # REQUEST Pagination checks
            if LENGTH_CLIENTS < P_PAGE_LIMIT:
                LOG_MESSAGE = f'PAGINATION BREAK Wireless Length : {LENGTH_CLIENTS} : P_PAGE_SIZE : {P_PAGE_LIMIT} : OFFSET : {OFFSET}'
                logging.debug(LOG_MESSAGE)
                break

            # Increment REQUEST Pagination
            COUNT += 1
            OFFSET = P_PAGE_LIMIT * COUNT

    #######
    # Get Wired Clients
    #######
    if P_GET_WIRED == 'true':

        # Used for REQUEST Pagination
        COUNT = 0
        OFFSET = 0

        while True:

            WIRED_CLIENTS = get_wired_clients(STEP4_BEARER_TOKEN, P_PAGE_LIMIT, OFFSET)
            LENGTH_CLIENTS = len(WIRED_CLIENTS.get('clients'))
            logging.debug('No. Wired Clients : %s', LENGTH_CLIENTS)

            for client in WIRED_CLIENTS['clients']:
                ########################################
                # Forescout Properties for endpoint(s)
                ########################################
                fs_endpoint = {}
                fs_endpoint_properties = {}

                for key, value in ARUBA_CLIENT_WIRED_TO_FS_MAP.items():
                    # Build Properties verify key exists
                    if key in client.keys():
                        # Get IP and MAC
                        if key in ('ip_address', 'macaddr'):
                            if key == 'macaddr':
                                # remove colon from mac address
                                fs_endpoint["mac"] = client['macaddr'].replace(':', '')
                            else:
                                fs_endpoint["ip"] = client['ip_address']
                            continue

                        # Need to remove colon from mac address(s)
                        if key in ('interface_mac', 'associated_device_mac'):
                            fs_endpoint_properties[value] = client[key].replace(':', '')
                        else:
                            fs_endpoint_properties[value] = client[key]

                    fs_endpoint['properties'] = fs_endpoint_properties

                # Append
                fs_endpoints.append(fs_endpoint)

            # REQUEST Pagination checks
            if LENGTH_CLIENTS < P_PAGE_LIMIT:
                LOG_MESSAGE = f'PAGINATION BREAK Wired Length : {LENGTH_CLIENTS} : P_PAGE_SIZE : {P_PAGE_LIMIT} : OFFSET : {OFFSET}'
                logging.debug(LOG_MESSAGE)
                break

            # Increment REQUEST Pagination
            COUNT += 1
            OFFSET = P_PAGE_LIMIT * COUNT

    # Connect Response
    logging.debug('endpoints =  %s', fs_endpoints)
    # Update Forescout with endponts
    response["endpoints"] = fs_endpoints

else:
    logging.info("No Valid Bearer Token")
    response['error'] = 'No Valid Bearer Token'
    response["succeeded"] = False
