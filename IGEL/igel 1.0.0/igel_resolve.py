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

import requests
import logging
import json

logging.info('===>Starting IGEL Resolve Script')

# Initialize response
response = {}

# Make the API Call
try:
    api_hostname = params.get('connect_igel_hostname', '')
    api_port = params.get('connect_igel_port', 8443)
    cookie = params.get('connect_authorization_token', '')
    proxy_ip = params.get('connect_proxy_ip', '')
    proxy_port = params.get('connect_proxy_port', '')
    proxy_username = params.get('connect_proxy_username', '')
    proxy_password = params.get('connect_proxy_password', '')
    resolve_mac = params.get('mac', '').lower()

    if not api_hostname:
        logging.warning('Hostname/IP not specified!')

    if not cookie:
        logging.warning('Authorization cookie not specified')

    payload = {}
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'charset': 'utf-8',
        'User-Agent': 'FSCT/2.16.2022',
        'Cookie': cookie
    }

    logging.debug('Retrieving all thin clients from IGEL UMS...')
    url = f'https://{api_hostname}:{api_port}/umsapi/v3/thinclients'
    resp = requests.request('GET', url, headers=headers, data=payload, verify=False, allow_redirects=True)

    if resp is None:
        response['error'] = 'No response from IGEL UMS.'
    elif resp.status_code == 200:
        properties = {}
        response_json = json.loads(resp.content)
        # logging.debug(response_json)
        thin_client_found = False
        logging.debug(f'Checking for thin clients with a MAC of {resolve_mac}..')
        for thin_client in response_json:
            thin_client_mac = thin_client.get('mac', '').lower()
            # logging.debug(f'Comparing thin client MAC ({thin_client_mac}) to {resolve_mac}...')
            if thin_client_mac == resolve_mac:
                thin_client_found = True
                logging.debug(f'Found match for {resolve_mac}: {thin_client}')
                properties = {'mac': resolve_mac,
                              'ip': thin_client.get('lastIP', ''),
                              'connect_igel_unit_id': thin_client.get('unitID', ''),
                              'connect_igel_mac': thin_client.get('mac', ''),
                              'connect_igel_firmware_id': thin_client.get('firmware_id', ''),
                              'connect_igel_last_ip': thin_client.get('lastIP', ''),
                              'connect_igel_device_attributes': thin_client.get('deviceAttributes', []),
                              'connect_igel_id': thin_client.get('id', ''),
                              'connect_igel_name': thin_client.get('name', ''),
                              'connect_igel_parent_id': thin_client.get('parentID', ''),
                              'connect_igel_moved_to_bin': thin_client.get('movedToBin', False),
                              'connect_igel_object_type': thin_client.get('objectType', ''),
                              'connect_igel_links': thin_client.get('links', [])
                              }
                response['properties'] = properties
                break
            else:
                continue

        if thin_client_found:
            logging.debug(f'properties: {response["properties"]}')
        else:
            logging.debug(f'{resolve_mac} not found in IGEL UMS')
            response['error'] = f'{resolve_mac} not found in IGEL UMS'
    else:
        response['error'] = f'Error Code {resp.status_code} received from IGEL UMS.'
except requests.exceptions.RequestException as e:
    response['error'] = f'Could not connect to IGEL UMS. Exception occurred. {e}'
except Exception as e:
    response['error'] = f'Unknown error: {e}'

logging.debug(f'Resolve Script Returned Response: {response}')

logging.info('===>Ending IGEL Resolve Script')
