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


def update_segment(mac, segment_name, api_token, url, proxie_param):
    """
    Function to Update Segment through Nile API Calls
    :param str mac: Mac Address of the client to update segment
    :param str segment_name: Segment Name from Nile Portal
    :param str api_token: API Token in Generated file from Nile Portal
    :param str url: URL in Generated file from Nile Portal
    :param dict proxie_param: Dictionary of Proxy Parameters
    :return: bool, str. Return True if Success, Else False. String provides Reason
    """
    # Get Segment ID from Segment Name
    result, segment_id = get_segment_id(segment_name, api_token, url, proxie_param)
    if not result:
        return result, segment_id
    # Converting mac-address into expected format aa:bb:cc:dd:ee:ff for Nile.
    # Application sends as aabbccddeeff
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
    result, status = post_mab_update(mab_json, api_token, url, proxie_param)
    if not result:
        return result, status
    return True, "Success"


def get_segment_id(segment_name, api_token, url, proxie_param):
    """
    Function to get Segment ID from Segment Name
    :param str segment_name: Segment Name from Nile Portal
    :param str api_token: API Token in Generated file from Nile Portal
    :param str url: URL in Generated file from Nile Portal
    :param dict proxie_param: Dictionary of Proxy Parameters
    :return: bool, str. Return True if Success, Else False. String provides Reason
    """
    head = {'Authorization': f'Bearer {api_token}'}
    final_url = url + f"/api/v1/settings/segments?filter=instanceName=={segment_name}"
    logging.debug('Sending request for Get with url=%s', final_url)
    try:
        resp = requests.get(url=final_url, headers=head, proxies=proxie_param)
        resp.raise_for_status()
        if "login" in resp.text:
            logging.error('Authentication Credentials are wrong. API Token incorrect or expired')
            return False, 'Authentication Credentials are wrong. API Token incorrect or expired'
        logging.debug('Response Status Code: %s', resp.status_code)
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


def post_mab_update(json_data, api_token, url, proxie_param):
    """
    Function that calls API to update Mab Segment
    :param dict json_data: String in JSON Data
    :param str api_token: API Token in Generated file from Nile Portal
    :param str url: URL in Generated file from Nile Portal
    :param dict proxie_param: Dictionary of Proxy Parameters
    :return: bool, str. Return True if Success, Else False. String provides Reason
    """
    final_url = url + "/api/v1" + "/client-configs"
    head = {'Authorization': f'Bearer {api_token}', "Content-Type": "application/json"}
    logging.debug('Sending request for Patch with url=%s. json=%s', final_url, json_data)
    try:
        resp = requests.patch(url=final_url, headers=head, json=json_data, proxies=proxie_param)
        resp.raise_for_status()
        logging.debug('Response Status Code: %s Text: "%s".', resp.status_code, resp.text)
    except requests.exceptions.HTTPError as err:
        return False, err
    return True, "Success"
