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
''' Forescout Discovery Poll
'''
import time
import logging
import json
import urllib.request

##############
# FUNCTIONS
##############
# Convert All Sessions Into PAGE SIZE CHUNKS


def sessions_chunks(sessions, size):
    '''
    Generator
    Convert ALL Sessions Into PAGE_SIZE_CHUNKS
    '''
    return (sessions[pos:pos + size] for pos in range(0, len(sessions), size))


# Build Session ID's as a string
def sessions_as_a_string(sessions_list):
    '''
    Obtains Sessions ID from URL Path
    and returns as a string
    Passed : ['https://localhost/mgmt/tm/apm/access-info/5519d028', 'https://localhost/mgmt/tm/apm/access-info/40780348']
    Returned : 5519d028 40780348
    '''
    sessions_ids_string = ""
    for id_of_session in sessions_list:
        sessions_ids_string = sessions_ids_string + \
            " " + id_of_session.split('/')[-1]

    # strip leading space before returning
    return sessions_ids_string.lstrip()


def get_f5_session_data():
    '''
    Get the F5 APM Sessions data for VPN
    '''
    returned_session_info = {}
    try:
        f5_sessions_url = f'{P_F5_HOST}/mgmt/tm/apm/access-info'
        logging.info('Get F5 Session Data : %s', f5_sessions_url)

        request = urllib.request.Request(f5_sessions_url)
        request.add_header("X-F5-Auth-Token", P_TOKEN)

        session_response = urllib.request.urlopen(request, context=ssl_context)

        # Return dict
        returned_session_info = json.loads(session_response.read())
        return returned_session_info
    except Exception as error:
        logging.log(f'Error in get_f5_session_data: {error}')
        return returned_session_info



def get_f5_bash_data(session_chunks):
    '''
    Get F5 Bash Session(s) Data
    '''
    returned_bash_info = {}
    try:
        f5_bash_url = f"{P_F5_HOST}/mgmt/tm/util/bash"
        logging.debug('Get F5 BASH Data : %s', f5_bash_url)

        # Build Payload
        post_payload = {
            'command': 'run',
            'utilCmdArgs': f'-c "tmsh -q list apm session {session_chunks}"'
            }

        # BODY Convert to JSON
        json_payload = json.dumps(post_payload).encode('utf-8')
        logging.debug('BASH Body Request : %s', json_payload)

        # Build Headers
        headers = {
            'X-F5-Auth-Token': P_TOKEN,
            'Content-type': 'application/json'
        }

        # Request BASH data
        request = urllib.request.Request(f5_bash_url, headers=headers, data=json_payload, method='POST')
        bash_response = urllib.request.urlopen(request, context=ssl_context)

        # Return dict
        returned_bash_info = json.loads(bash_response.read())
        return returned_bash_info
    except Exception as error:
        logging.log(f'Error in get_f5_bash_data: {error}')
        return returned_bash_info

###################
# END of Functions
###################

# Mapping between f5vpn response fields to CounterACT properties
# connect_f5vpn_session_id is obtained from initial query not BASH query
# This dict is used for scraping the BASH output
#
# NOTE : assigned.clientip has to be first entry in DICT


F5VPN_TO_CT_PROPS_MAP = {
    'assigned.clientip': 'connect_f5vpn_assigned_vpnip',
    'user.clientip': 'connect_f5vpn_session_user_clientip',
    'machine_info.last.net_adapter.list.[0].mac_address': 'connect_f5vpn_machine_info_mac_address',
    'ad.last.actualdomain': 'connect_f5vpn_ad_last_actualdomain',
    'check_software.last.av.item_1.name': 'connect_f5vpn_av_item_1_name',
    'check_software.last.av.item_1.signature': 'connect_f5vpn_av_item_1_signature',
    'check_software.last.av.item_1.vendor_name': 'connect_f5vpn_av_item_1_vendor_name',
    'check_software.last.av.item_1.version': 'connect_f5vpn_av_item_1_version',
    'check_software.last.fw.item_1.name': 'connect_f5vpn_fw_item_1_name',
    'check_software.last.fw.item_1.signature': 'connect_f5vpn_fw_item_1_signature',
    'check_software.last.fw.item_1.vendor_name': 'connect_f5vpn_fw_item_1_vendor_name',
    'check_software.last.fw.item_1.version': 'connect_f5vpn_fw_item_1_version',
    'client.hostname': 'connect_f5vpn_client_hostname',
    'client.platform': 'connect_f5vpn_client_platform',
    'logon.last.logonname': 'connect_f5vpn_logon_last_logonname',
    'logon.last.username': 'connect_f5vpn_logon_last_username',
    'policy.inspectionhost.status': 'connect_f5vpn_inspectionhost_status',
    'policy.inspectionhost.timestamp': 'connect_f5vpn_inspectionhost_timestamp',
    'server.network.name': 'connect_f5vpn_server_network_name',
    'server.network.port': 'connect_f5vpn_server_network_port',
    'server.network.protocol': 'connect_f5vpn_server_network_protocol',
    'user.ip_reputation': 'connect_f5vpn_user_ip_reputation',
    'user.starttime': 'connect_f5vpn_user_starttime'
}

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
# CONFIGURATION from UI Panels
P_F5_HOST = params.get('connect_f5vpn_host')
P_TOKEN = params.get('connect_authorization_token')
# Convert to Integers
P_PAGE_SIZE = int(params.get('connect_f5vpn_page_size'))
P_BACKOFF_TIMER = int(params.get('connect_f5vpn_backoff_timer'))

if P_TOKEN is None or P_TOKEN == "":
    response = {}
    endpoint_data = {}
    logging.debug(
        "Error : No Valid Token Stored. Check f5vpn_authorization.py outputs")
    #response["succeeded"] = False
    #response["troubleshooting"] = endpoint_data
    response["error"] = "No Valid Token Stored. Check f5vpn_authorization.py outputs"
else:

    F5_SESSION_DATA = {}
    F5_SESSION_DATA = get_f5_session_data()
    logging.debug('F5_SESSION_DATA : %s', F5_SESSION_DATA)

    ########################################
    # Forescout Properties for endpoint(s)
    ########################################
    response = {}
    fs_endpoints = []
    logging.info('Clearing response/fs_endpoints')

    if 'entries' in F5_SESSION_DATA:
        logging.info('Found F5 session data')

        # Start iterating PAGE_SIZE_CHUNKS
        for page_chunks in sessions_chunks(list(F5_SESSION_DATA['entries'].keys()), P_PAGE_SIZE):
            logging.info('Starting iterate BASH page chunks : %s', page_chunks)

            # Get Page Chunk Session IDs as a string
            session_ids_chunks = sessions_as_a_string(page_chunks)

            # HTTP Get f5 bash sessions chunks
            f5_session_cmd_result = get_f5_bash_data(session_ids_chunks)

            logging.info('Waiting P_BACKOFF_TIMER : %s', P_BACKOFF_TIMER)
            time.sleep(P_BACKOFF_TIMER)

            # ITERATE OVER BASH SESSIONS LOOKING FOR PROPERTIES
            for session in page_chunks:
                logging.info('Starting iterate BASH session : %s', session)
                session_id = session.split('/')[-1]

                ########################################
                # Forescout Properties for endpoint(s)
                ########################################
                fs_endpoint = {}
                fs_endpoint_properties = {}

                # Flag used to stop properties being added, if a sessions has NO IP
                # This can happen, if session is going through profile scanning
                # No tunnel IP is allocated yet
                flag_ip_found = False

                # Start searching Bash Properties
                for key, value in F5VPN_TO_CT_PROPS_MAP.items():
                    # Build Search String
                    f5_search_string = f"{session.split('/')[-1]}.session.{key}"

                    # Find START of search string
                    find_start = f5_session_cmd_result['commandResult'].find(f5_search_string)

                    # Check if the string was found, otherwise skip
                    if find_start != -1:
                        # Find END of search string
                        find_end = f5_session_cmd_result['commandResult'].find("\n", find_start)

                        # Get F5 property
                        f5_found_string = f5_session_cmd_result['commandResult'][find_start:find_end]

                        # Get IP Address
                        if key == "assigned.clientip" and not flag_ip_found:
                            logging.debug('Found IP : %s', f5_found_string.split(maxsplit=2)[2])
                            fs_endpoint["ip"] = f5_found_string.split(maxsplit=2)[2]
                            # Set flag we have found IP
                            flag_ip_found = True

                            # Also add Sessioned ID property
                            # Not included in the f5 to ct mapping dict
                            fs_endpoint_properties['connect_f5vpn_session_id'] = session_id

                        # BASH value
                        fs_endpoint_properties[value] = f5_found_string.split(maxsplit=2)[2]

                # Add properties to endpoint, if flag_ip_found is True
                if flag_ip_found:
                    fs_endpoint["properties"] = fs_endpoint_properties

                    # Append endpoint to endpoints
                    logging.debug('fs_endpoint : %s', fs_endpoint)
                    fs_endpoints.append(fs_endpoint)
                else:
                    logging.info('NO IP Found for session_id : %s', session_id)

        logging.debug('endpoints : %s', fs_endpoints)
        response = {}
        response["endpoints"] = fs_endpoints

    else:
        logging.info('No Active Sessions')
        #response["succeeded"] = True
        #response["result_msg"] = 'No Active Sessions'
        response["endpoints"] = fs_endpoints
