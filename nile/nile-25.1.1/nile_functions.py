#!/usr/bin/env python3
"""
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
"""
import json
import logging
from datetime import datetime, timedelta, timezone
import requests


def get_proxy_settings(params):
    """
    Function to Parse Proxy Settings
    :param dict params: Dictionary of Proxy Parameters
    :return: dict. Return Proxy URL Parameters are dict
    """
    is_proxy_enabled = params.get("connect_proxy_enable")
    if is_proxy_enabled == "true":
        proxy_ip = params.get("connect_proxy_ip")
        proxy_port = params.get("connect_proxy_port")
        proxy_user = params.get("connect_proxy_username")
        proxy_pass = params.get("connect_proxy_password")
        if not proxy_user:
            proxy_url = f"https://{proxy_ip}:{proxy_port}"
            proxy_dict = {"https": proxy_url}
            logging.debug("Proxy is enabled / without user")
        else:
            proxy_url = f"https://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
            proxy_dict = {"https": proxy_url}
            logging.debug("Proxy is enabled / with user")
    else:
        logging.debug("Proxy disabled")
        proxy_dict = None
    return proxy_dict


def api_error_checks(resp_text):
    """
    Function to Check API Errors
    :param str resp_text: API Response
    :return: bool, str. False if API Errors, True otherwise
    """
    try:
        json.loads(resp_text)
        return True, resp_text
    except ValueError:
        if "login" in resp_text:
            logging.error('Authentication Credentials are wrong. API Token incorrect or expired')
            return False, 'Authentication Credentials are wrong. API Token incorrect or expired'
        if "freshchat" in resp_text:
            logging.error('API Error. Likely API not available')
            return False, 'API Error. Likely API not available'
    return False, resp_text


def update_segment(mac, segment_name, api_token, url, proxy_param):
    """
    Function to Update Segment through Nile API Calls
    :param str mac: Mac Address of the client to update Segment with
    :param str segment_name: Segment Name from Nile Portal
    :param str api_token: API Token in Generated file from Nile Portal
    :param str url: URL in Generated file from Nile Portal
    :param dict proxy_param: Dictionary of Proxy Parameters
    :return: bool, str. Return True if Success, Else False. String provides Reason
    """
    # Get Segment ID from Segment Name
    result, segment_id = get_segment_id(segment_name, api_token, url, proxy_param)
    if not result:
        return result, segment_id
    # Converting mac-address into expected format aa:bb:cc:dd:ee:ff (Nile) from aabbccddeeff (App)
    mac_addr = ':'.join(mac[i:i + 2] for i in range(0, 12, 2))
    mab_dict = {
        "macAddress": mac_addr,
        "segmentId": segment_id,
        "state": "AUTH_OK"
    }
    mab_json = {
        "macsList": [mab_dict]
    }
    # Post Mab Update for the device
    result, status = post_mab_update(mab_json, api_token, url, proxy_param)
    if not result:
        return result, status
    return True, "Success"


def get_segment_id(segment_name, api_token, url, proxy_param):
    """
    Function to get Segment ID for a given Segment.
    :param str segment_name: Segment Name from Nile Portal
    :param str api_token: API Token in Generated file from Nile Portal
    :param str url: URL in Generated file from Nile Portal
    :param dict proxy_param: Dictionary of Proxy Parameters
    :return: bool, str. Return True if Success, Else False. String provides Reason
    """
    head = {'Authorization': f'Bearer {api_token}'}
    final_url = f"{url}/api/v1/settings/segments?filter=instanceName=={segment_name}"
    try:
        logging.debug('Sending request for Get with url=%s', final_url)
        resp = requests.get(url=final_url, headers=head, proxies=proxy_param)
        resp.raise_for_status()
        logging.debug('Response Status Code: %s', resp.status_code)
        api_status, api_resp = api_error_checks(resp.text)
        if not api_status:
            logging.error(api_resp)
            return False, api_resp
        logging.debug(json.dumps(resp.json(), indent=2))
        result = resp.json()['data']['content']
        if len(result) == 0:
            logging.error("Could not get Segment ID. Likely Segment Name doesnt exist")
            return False, "Segment Name does not exist. Please check configuration"
        if len(result[0]['id']) != 36:
            logging.error("Could not get Segment ID. Exit()")
            return False, "Segment Name does not exist. Please check configuration"
        return True, result[0]['id']
    except requests.exceptions.HTTPError as err:
        return False, err
    except NameError as err:
        return False, err


def get_multiple_site_id(multiple_site_name, api_token, url, proxy_param):
    """
    Function to get Site ID from Site Name.
    :param str multiple_site_name: Multiple Site Name from Nile Portal
    :param str api_token: API Token in Generated file from Nile Portal
    :param str url: URL in Generated file from Nile Portal
    :param dict proxy_param: Dictionary of Proxy Parameters
    :return: bool, str. Return True if Success, Else False. String provides Reason
    """
    if "All" == multiple_site_name:
        return True, None
    multiple_site_id = ""
    sites = multiple_site_name.split(',')
    for site in sites:
        site_name = site.strip()
        result, site_id = get_site_id(site_name, api_token, url, proxy_param)
        if result:
            if multiple_site_id != "":
                multiple_site_id = multiple_site_id + ','
            multiple_site_id = multiple_site_id + site_id
        else:
            return result, site_id
    return True, multiple_site_id

def get_site_id(site_name, api_token, url, proxy_param):
    """
    Function to get Site ID from Site Name.
    :param str site_name: Site Name from Nile Portal
    :param str api_token: API Token in Generated file from Nile Portal
    :param str url: URL in Generated file from Nile Portal
    :param dict proxy_param: Dictionary of Proxy Parameters
    :return: bool, str. Return True if Success, Else False. String provides Reason
    """
    head = {'Authorization': f'Bearer {api_token}'}
    if "All" == site_name:
        filter_url = ""
    else:
        filter_url = f"?filter=name=={site_name}"
    final_url = f"{url}/api/v1/sites{filter_url}"
    logging.debug('Sending request for Get with url=%s', final_url)
    try:
        resp = requests.get(url=final_url, headers=head, proxies=proxy_param)
        resp.raise_for_status()
        logging.debug('Response Status Code: %s', resp.status_code)
        api_status, api_resp = api_error_checks(resp.text)
        if not api_status:
            logging.error(api_resp)
            return False, api_resp
        logging.debug(json.dumps(resp.json(), indent=2))
        result = resp.json()['content']
        if len(result) == 0:
            logging.error("Could not get Site ID. Likely Site Name doesnt exist")
            return False, "Site Name does not exist. Please check configuration"
        if len(result[0]['id']) != 36:
            logging.error("Could not get Site ID. Exit()")
            return False, "Site Name does not exist. Please check configuration"
        return True, result[0]['id']
    except requests.exceptions.HTTPError as err:
        return False, err
    except NameError as err:
        return False, err


def post_mab_update(json_data, api_token, url, proxy_param):
    """
    Function that calls API to update Mab Segment
    :param dict json_data: String in JSON Data
    :param str api_token: API Token in Generated file from Nile Portal
    :param str url: URL in Generated file from Nile Portal
    :param dict proxy_param: Dictionary of Proxy Parameters
    :return: bool, str. Return True if Success, Else False. String provides Reason
    """
    final_url = url + "/api/v1" + "/client-configs"
    head = {'Authorization': f'Bearer {api_token}', "Content-Type": "application/json"}
    logging.debug('Sending request for Patch with url=%s. json=%s', final_url, json_data)
    try:
        resp = requests.patch(url=final_url, headers=head, json=json_data, proxies=proxy_param)
        resp.raise_for_status()
        logging.debug('Response Status Code: %s Text: "%s".', resp.status_code, resp.text)
    except requests.exceptions.HTTPError as err:
        return False, err
    return True, "Success"


def get_time_in_format(time_duration):
    """
    Function to get time in format for API
    :param int time_duration: Duration of Delta in time
    :return: str, str. Now and Previous Time in UTC
    """
    # Get current time
    now_time = datetime.now(timezone.utc)
    now_utc = now_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    now_utc = now_utc.replace(":", "%3A")
    # Construct the time
    one_hour_ago = now_time - timedelta(hours=time_duration)
    past_utc = one_hour_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
    past_utc = past_utc.replace(":", "%3A")
    return now_utc, past_utc


def poll_client_list(api_token, url, proxy_param, site_id=None, wired_only="true", page_size=1000):
    """
    Function that polls Nile API for Clients.
    :param str api_token: API Token in Generated file from Nile Portal
    :param str url: URL in Generated file from Nile Portal
    :param dict proxy_param: Dictionary of Proxy Parameters
    :param str site_id: Site ID from Nile Portal
    :param str wired_only: If True, will poll only wired clients. Else, will poll all clients
    :param int page_size: Number of Clients to poll in one go (Default 1000)
    :return: bool, str. Return True if Success, Else False. String provides Reason
    """
    time_duration = 2
    # Mapping between Nile API Response fields to CounterAct properties
    nile_to_ct_props_map = {
        'macAddress':           'mac', # Modify to make mac-address format aabbccddeeff
        'ipAddress':            'ip',  # Handle for 'NOT AVAILABLE'
        # connect_nile_mac, connect_nile_ip: Internal variables used
        'serialName':           'connect_nile_serialName',
        'siteName':             'connect_nile_siteName',
        'buildingName':         'connect_nile_buildingName',
        'floorName':            'connect_nile_floorName',
        'segment':              'connect_nile_segment',
        'clientStatus':         'connect_nile_clientStatus',
        'connectedSince':       'connect_nile_connectedSince',
        'port':                 'connect_nile_port',
        'connectionType':       'connect_nile_connectionType',
        'ssid':                 'connect_nile_ssid',
        'deviceType':           'connect_nile_deviceType',
        'deviceManufacturer':   'connect_nile_deviceManufacturer',
        'deviceOs':             'connect_nile_deviceOs'
    }
    endpoints = []

    if site_id is None:
        scope = ""
    else:
        scope = f"&siteId={site_id}"

    now_utc, past_utc = get_time_in_format(time_duration)
    time_url = f"&startTime={past_utc}&endTime={now_utc}{scope}"
    url2 = f"{url}/api/v1/public/client-list-paginated-details?"
    head = {'Authorization': f'Bearer {api_token}'}
    result = []
    actual_iter = 0

    while True:
        final_url = f"{url2}pageNumber={actual_iter}&pageSize={page_size}{time_url}"
        logging.debug('Sending request for Get with url=%s', final_url)
        try:
            resp = requests.get(url=final_url, headers=head, proxies=proxy_param)
            logging.debug('Response Status Code:%s', resp.status_code)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return False, err
        api_status, api_resp = api_error_checks(resp.text)
        if not api_status:
            logging.error(api_resp)
            return False, api_resp
        resp2 = resp.json()
        cl_count = resp2['numTotalClients']
        result = result + resp2['clientList']
        actual_iter += 1
        if (actual_iter * page_size) >= cl_count:
            break
    for entry in result:
        if wired_only == "true":
            if entry["connectionType"] == "wireless":
                continue
        endpoint = {}
        endpoint_properties = {}
        for key, value in entry.items():
            if key in nile_to_ct_props_map:
                if key == 'macAddress':
                    # convert mac address from aa:bb:cc:dd:ee:ff to aabbccddeeff
                    value = value.replace(":", "")
                    endpoint["mac"] = value
                    endpoint_properties["connect_nile_mac"] = value
                elif key == 'ipAddress':
                    if "." in value: # Only values with A.B.C.D
                        endpoint["ip"] = value
                    endpoint_properties["connect_nile_ip"] = value
                else:
                    endpoint_properties[nile_to_ct_props_map[key]] = value
        endpoint["properties"] = endpoint_properties
        endpoints.append(endpoint)
    logging.debug('Number of Total Clients:%s Actual Clients: %s Wired Only: %s EndPoints: %s',
                  cl_count, len(result), wired_only, len(endpoints))
    return True, endpoints
