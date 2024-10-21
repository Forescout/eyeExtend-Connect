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
import logging


logging.debug('===> Start of nile_authorization Scripts')
if params is None:
    params = {}
api_key = params.get("connect_nile_api_token")
base_url = params.get("connect_nile_url")
mac = params.get("mac")
seg_name = params.get("connect_nile_auth_segment_name")
seg_name_custom = params.get("netseg_name")
# Check if the parameters are present. They are mandatory.
if (api_key is None) or (base_url is None) or (mac is None) or (seg_name is None):
    ERROR_TEXT = ""
    if api_key is None:
        ERROR_TEXT = ERROR_TEXT + " API-Key is Empty."
    if base_url is None:
        ERROR_TEXT = ERROR_TEXT + " URL is Empty."
    if mac is None:
        ERROR_TEXT = ERROR_TEXT + " Mac-Address is Empty."
    if seg_name is None:
        ERROR_TEXT = ERROR_TEXT + " Segment Name is Empty."
    ERROR_OUT = "Missing or Wrong Parameters."+str(ERROR_TEXT)
    logging.error(ERROR_OUT)
    response = {"succeeded": False, "troubleshooting": ERROR_OUT}
else:
    # Get Proxy Parameters
    PROXY = nile_functions.get_proxy_settings(params)
    if seg_name_custom == "<default>":
        res, message = nile_functions.update_segment(mac, seg_name, api_key, base_url, PROXY)
    else:
        res, message = nile_functions.update_segment(mac, seg_name_custom, api_key, base_url, PROXY)
    if res:
        response = {"succeeded": res}
    else:
        response = {"succeeded": res, "troubleshooting": message}
logging.debug('===> End of nile_authorization Scripts')
