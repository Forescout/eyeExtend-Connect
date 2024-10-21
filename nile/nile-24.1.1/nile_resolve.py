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


logging.debug('===> Start of nile_resolve Scripts')
if params is None:
    params = {}
api_key = params.get("connect_nile_api_token")
base_url = params.get("connect_nile_url")
mac = params.get("mac")
site_name = params.get("connect_nile_site_name")
wired_only = params.get("connect_nile_wired")
# Check if the parameters are present. They are mandatory.
if (api_key is None) or (base_url is None) or (mac is None) or (site_name is None):
    ERROR_TEXT = ""
    if api_key is None:
        ERROR_TEXT = ERROR_TEXT + " API-Key is Empty."
    if base_url is None:
        ERROR_TEXT = ERROR_TEXT + " URL is Empty."
    if mac is None:
        ERROR_TEXT = ERROR_TEXT + " Mac-Address is Empty."
    if site_name is None:
        ERROR_TEXT = ERROR_TEXT + " Site Name is Empty."
    ERROR_OUT = "Missing or Wrong Parameters."+str(ERROR_TEXT)
    logging.error(ERROR_OUT)
    response = {"error": ERROR_OUT}
else:
    # Get Proxy Parameters
    PROXY = nile_functions.get_proxy_settings(params)
    res2, site_ids = nile_functions.get_multiple_site_id(site_name, api_key, base_url, PROXY)
    if not res2:
        response = {"error": site_ids}
    else:
        res, message = nile_functions.resolve_client(api_key, base_url, PROXY, mac, site_ids)
        if res:
            response = {"properties": message["properties"]}
        else:
            response = {"error": message}
logging.debug('===> End of nile_resolve Scripts')
