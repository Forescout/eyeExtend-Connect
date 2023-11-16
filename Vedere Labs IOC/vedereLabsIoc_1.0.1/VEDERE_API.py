"""
Copyright © 2023 Forescout Technologies, Inc.

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

VL_FEEDS_BASEURL = "https://api.feeds.vederelabs.com"

def clean_empty_dict(d):
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_empty_dict(v) for v in d) if v]
    return {k: v for k, v in ((k, clean_empty_dict(v)) for k, v in d.items()) if v or v is False}


def VL_RETRIEVE_INDICATORS(api_details):

    logging.debug("***Vedere Labs*** Starting to retrieve indiators")

    types = 0

    _current_status_code = None
    _verify = api_details["ssl_verify"]
    _api_key = api_details["subscriber_api_key"]
    _lookback = api_details["lookback"]
    _ipv4_lookup = api_details["enable_ipv4_ioc"]
    _dns_lookup = api_details["enable_dns_ioc"]
    _hash_lookup = api_details["enable_hash_ioc"]
    _proxy = api_details["proxies"]

    logging.debug("***Vedere Labs*** Retrieved {}".format(api_details))

    if _ipv4_lookup == "true":
        types += 1
    
    if _dns_lookup == "true":
        types += 2

    if _hash_lookup == "true":
        types += 4

    logging.debug("***Vedere Labs*** Determined which IOC types needed: {}".format(types))

    _headers = {'User-Agent': 'VedereLabs-Connect-App-1.0.1', 'Content-Type': 'application/json; charset=utf-8;', 'api-key' : _api_key }

    _time_range = "start=now-{}d".format(_lookback)
    
    logging.debug("***Vedere Labs*** headers: {} , and time range: {}".format(_headers, _time_range))

    ## For lookups that only require 1 API call
    if types in (1, 4, 7):
        if types == 7:
            _indicators_controller = '{}/feedservice/api/indicators/?{}'.format(VL_FEEDS_BASEURL,_time_range)
        elif types == 1:
            _indicators_controller = '{}/feedservice/api/indicators/?type=ipv4-addr&{}'.format(VL_FEEDS_BASEURL,_time_range)
        elif types == 4:
            _indicators_controller = '{}/feedservice/api/indicators/?type=file&{}'.format(VL_FEEDS_BASEURL,_time_range)

        logging.debug("***Vedere Labs*** Using Request URL: {}".format(_indicators_controller))

        try:
            response = requests.get(_indicators_controller, headers=_headers, timeout=360, verify=_verify, proxies=_proxy)
            _current_status_code = response.status_code
            
            if _current_status_code == 200:
                payload = response.content
                json_response = json.loads(payload.decode("utf-8"))
            elif "No valid indicators" in response.text:
                json_response = "No valid indicators"
                logging.debug("***Vedere Labs*** {}".format(json_response))
            else:
                response.raise_for_status()

        except Exception as e:
            logging.error("***Vedere Labs*** Get HTTP Client failed: {}.".format(str(e)))
        return _current_status_code, json_response
    ## For lookups that require multiple API calls
    elif types in (2, 3, 5, 6):
        if types == 2:
            _indicators_controller_1 = '{}/feedservice/api/indicators/?type=domain-name&{}'.format(VL_FEEDS_BASEURL,_time_range)
            _indicators_controller_2 = '{}/feedservice/api/indicators/?type=url&{}'.format(VL_FEEDS_BASEURL,_time_range)
        elif types == 3:
            _indicators_controller_1 = '{}/feedservice/api/indicators/?type=domain-name&{}'.format(VL_FEEDS_BASEURL,_time_range)
            _indicators_controller_2 = '{}/feedservice/api/indicators/?type=url&{}'.format(VL_FEEDS_BASEURL,_time_range)    
            _indicators_controller_3 = '{}/feedservice/api/indicators/?type=ipv4-addr&{}'.format(VL_FEEDS_BASEURL,_time_range)    
        elif types == 5:
            _indicators_controller_1 = '{}/feedservice/api/indicators/?type=ipv4-addr&{}'.format(VL_FEEDS_BASEURL,_time_range)
            _indicators_controller_2 = '{}/feedservice/api/indicators/?type=file&{}'.format(VL_FEEDS_BASEURL,_time_range)
        else:
            _indicators_controller_1 = '{}/feedservice/api/indicators/?type=domain-name&{}'.format(VL_FEEDS_BASEURL,_time_range)
            _indicators_controller_2 = '{}/feedservice/api/indicators/?type=url&{}'.format(VL_FEEDS_BASEURL,_time_range)    
            _indicators_controller_3 = '{}/feedservice/api/indicators/?type=file&{}'.format(VL_FEEDS_BASEURL,_time_range) 
        
        ## For lookups that require 2 API calls
        if types in (2, 5):
            
            logging.debug("***Vedere Labs*** 1st API Call Using Request URL: {}".format(_indicators_controller_1))
            logging.debug("***Vedere Labs*** 2nd API Call Using Request URL: {}".format(_indicators_controller_2))

            try:
                response_1 = requests.get(_indicators_controller_1, headers=_headers, timeout=360, verify=_verify, proxies=_proxy)
                response_2 = requests.get(_indicators_controller_2, headers=_headers, timeout=360, verify=_verify, proxies=_proxy)
                _current_status_code_1 = response_1.status_code
                _current_status_code_2 = response_2.status_code
                            
                if _current_status_code_1 == 200:
                    payload_1 = response_1.content
                    json_response_1 = json.loads(payload_1.decode("utf-8"))
                elif "No valid indicators" in response_1.text:
                    json_response_1 = "No valid indicators"
                    logging.debug("***Vedere Labs*** {}".format(json_response_1))
                else:
                    response_1.raise_for_status()

                if _current_status_code_2 == 200:
                    payload_2 = response_2.content
                    json_response_2 = json.loads(payload_2.decode("utf-8"))
                elif "No valid indicators" in response_2.text:
                    json_response_2 = "No valid indicators"
                    logging.debug("***Vedere Labs*** {}".format(json_response_2))
                else:
                    response_2.raise_for_status()

                ## Decision logic if responses must be merged, based on which API calls returned valid indicators
                if _current_status_code_1 == _current_status_code_2 == 200:
                    logging.debug("***Vedere Labs*** Both API calls returned 200, merging responses")
                    _current_status_code = _current_status_code_1

                    object_1 = json_response_1.get("objects", [])
                    object_2 = json_response_2.get("objects", [])
                
                    merged_objects = object_1 + object_2
                
                    merged_response = {
                        "objects" : merged_objects
                    }
                elif _current_status_code_1 == 200:
                    logging.debug("***Vedere Labs*** Only 1st API call returned 200")
                    _current_status_code = _current_status_code_1
                    merged_response = json_response_1
                elif _current_status_code_2 == 200:
                    logging.debug("***Vedere Labs*** Only 2nd API call returned 200")
                    _current_status_code = _current_status_code_2
                    merged_response = json_response_2
                else:
                    logging.debug("***Vedere Labs*** Both API calls did not return 200")
                    _current_status_code = _current_status_code_1
                    merged_response = json_response_1

            except Exception as e:
                logging.error("***Vedere Labs*** Get HTTP Client failed: {}.".format(str(e)))
            return _current_status_code, merged_response
        
        ## For lookups that require 3 API calls
        else:

            logging.debug("***Vedere Labs*** 1st API Call Using Request URL: {}".format(_indicators_controller_1))
            logging.debug("***Vedere Labs*** 2nd API Call Using Request URL: {}".format(_indicators_controller_2))
            logging.debug("***Vedere Labs*** 3rd API Call Using Request URL: {}".format(_indicators_controller_3))

            try:
                response_1 = requests.get(_indicators_controller_1, headers=_headers, timeout=360, verify=_verify, proxies=_proxy)
                response_2 = requests.get(_indicators_controller_2, headers=_headers, timeout=360, verify=_verify, proxies=_proxy)
                response_3 = requests.get(_indicators_controller_3, headers=_headers, timeout=360, verify=_verify, proxies=_proxy)
                _current_status_code_1 = response_1.status_code
                _current_status_code_2 = response_2.status_code
                _current_status_code_3 = response_3.status_code
                            
                if _current_status_code_1 == 200:
                    payload_1 = response_1.content
                    json_response_1 = json.loads(payload_1.decode("utf-8"))
                elif "No valid indicators" in response_1.text:
                    json_response_1 = "No valid indicators"
                    logging.debug("***Vedere Labs*** {}".format(json_response_1))
                else:
                    response_1.raise_for_status()

                if _current_status_code_2 == 200:
                    payload_2 = response_2.content
                    json_response_2 = json.loads(payload_2.decode("utf-8"))
                elif "No valid indicators" in response_2.text:
                    json_response_2 = "No valid indicators"
                    logging.debug("***Vedere Labs*** {}".format(json_response_2))
                else:
                    response_2.raise_for_status()

                if _current_status_code_3 == 200:
                    payload_3 = response_3.content
                    json_response_3 = json.loads(payload_3.decode("utf-8"))
                elif "No valid indicators" in response_3.text:
                    json_response_3 = "No valid indicators"
                    logging.debug("***Vedere Labs*** {}".format(json_response_3))
                else:
                    response_3.raise_for_status()
                
                ## Decision logic if responses must be merged, based on which API calls returned valid indicators
                if _current_status_code_1 == _current_status_code_2 == _current_status_code_3 == 200:
                    logging.debug("***Vedere Labs*** All API calls returned 200, merging responses")
                    _current_status_code = _current_status_code_1

                    object_1 = json_response_1.get("objects", [])
                    object_2 = json_response_2.get("objects", [])
                    object_3 = json_response_3.get("objects", [])
                
                    merged_objects = object_1 + object_2 + object_3
                
                    merged_response = {
                        "objects" : merged_objects
                    } 
                elif _current_status_code_1 == _current_status_code_2 == 200:
                    logging.debug("***Vedere Labs*** 1st and 2nd API calls returned 200, merging responses")
                    _current_status_code = _current_status_code_1

                    object_1 = json_response_1.get("objects", [])
                    object_2 = json_response_2.get("objects", [])
                
                    merged_objects = object_1 + object_2
                
                    merged_response = {
                        "objects" : merged_objects
                    }
                elif _current_status_code_1 == _current_status_code_3 == 200:
                    logging.debug("***Vedere Labs*** 1st and 3rd API calls returned 200, merging responses")
                    _current_status_code = _current_status_code_1
                    
                    object_1 = json_response_1.get("objects", [])
                    object_3 = json_response_3.get("objects", [])
                
                    merged_objects = object_1 + object_3
                
                    merged_response = {
                        "objects" : merged_objects
                    }
                elif _current_status_code_2 == _current_status_code_3 == 200:
                    logging.debug("***Vedere Labs*** 2nd and 3rd API calls returned 200, merging responses")
                    _current_status_code = _current_status_code_2
                    
                    object_2 = json_response_2.get("objects", [])
                    object_3 = json_response_3.get("objects", [])
                
                    merged_objects = object_2 + object_3
                
                    merged_response = {
                        "objects" : merged_objects
                    }
                elif _current_status_code_1 == 200:
                    logging.debug("***Vedere Labs*** Only 1st API call returned 200")
                    _current_status_code = _current_status_code_1
                    merged_response = json_response_1
                elif _current_status_code_2 == 200:
                    logging.debug("***Vedere Labs*** Only 2nd API call returned 200")
                    _current_status_code = _current_status_code_2
                    merged_response = json_response_2
                elif _current_status_code_2 == 200:
                    logging.debug("***Vedere Labs*** Only 3rd API call returned 200")
                    _current_status_code = _current_status_code_3
                    merged_response = json_response_3
                else:
                    logging.debug("***Vedere Labs*** All API calls did not return 200")
                    _current_status_code = _current_status_code_1
                    merged_response = json_response_1

            except Exception as e:
                logging.error("***Vedere Labs*** Get HTTP Client failed: {}.".format(str(e)))
            return _current_status_code, merged_response