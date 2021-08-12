"""
Copyright © 2021 Forescout Technologies, Inc.

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

from connectproxyserver import ConnectProxyServer, ProxyProtocol
from urllib import request
from urllib.request import HTTPError, URLError
import logging
import json
import re

# Mapping between Symantec API response fields to CounterACT properties
symantec_to_ct_props_map = {
    "uniqueId": "connect_symantec_computer_id",
    "computerName": "connect_symantec_computer_name",
    "macAddresses": "connect_symantec_mac_address",
    "ipAddresses": "connect_symantec_ip_address",
    "operatingSystem": "connect_symantec_os"
}

server_url = params.get("connect_symantec_server_url")
port = params.get("connect_symantec_server_port")
page_size = params.get("connect_symantec_poll_pagesize")
page_range = params.get("connect_symantec_poll_pagerange")

protocol = "https://"
poll_base_url = f"{protocol}{server_url}:{port}/sepm/api/v1/computers"

response = {}
bearer_token = params.get("connect_authorization_token")

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": "Bearer " + str(bearer_token)
}

if bearer_token:
    try:
        # For pagination, we use parameters pageIndex and pageSize in the url
        # For example: https://8.8.8.8:8446/sepm/api/v1/computers?pageIndex=2&pageSize=3
        # pageIndex is the page to poll
        # pageSize is the max. number of endpoints to poll within a page
        pagination_completed = False
        #default page_index is 1 which means we will starting polling from page 1
        page_index = 1
        page_end_index = 1
        # If the user does not specify a page range to poll, we will poll all pages
        # Else, extract the page_index and page_end_index (last page to poll) from the input page range
        # Page range must start and end with numbers and dash character (one or more) in between.
        # Using whitespaces at the beginning, the end, before and after dash(es) of page range are acceptable
        # Start number (page_index) must be smaller than end number (page_end_index)
        # Example of valid page range: "4-10", "4--10", "  04--010 ", "4  - 10 "
        if page_range:
            range_pattern = re.compile("^(\d+)(\s*)(-+)(\s*)(\d+)$")
            ranges = range_pattern.findall(page_range.strip())
            if ranges:
                page_index = int(ranges[0][0])
                page_end_index = int(ranges[0][-1])
                if not (1 <= page_index <= page_end_index):
                    page_range = None
                    logging.debug("Page range is invalid and won't not be used")
            else:
                page_range = None
                logging.debug("Page range is invalid and won't not be used")
        endpoints=[]
        while not pagination_completed:
            # Create proxy server
            proxy_server = ConnectProxyServer(params)
            # Pass to use what HTTPS or HTTP or both in the protocol, pass down the ssl_context
            opener = proxy_server.get_urllib_request_https_opener(ProxyProtocol.all, ssl_context)
            poll_url = f"{poll_base_url}?pageIndex={page_index}&pageSize={page_size}"
            #Eg: https://8.8.8.8:8446/sepm/api/v1/computers?pageIndex=1&pageSize=2
            logging.debug("Get polling URL: {}".format(poll_url))
            poll_request = request.Request(poll_url, headers=headers)
            poll_response = opener.open(poll_request)
            if poll_response.getcode() == 200:
                poll_response_dict = json.loads(poll_response.read())
                for endpoint_data in poll_response_dict["content"]:
                    endpoint = {}
                    mac_with_dash = endpoint_data["macAddresses"][0]
                    mac = "".join(mac_with_dash.split("-"))
                    endpoint["mac"] = mac
                    properties = {}
                    for key, value in endpoint_data.items():
                        if key == "macAddresses":
                            properties[symantec_to_ct_props_map[key]] = mac
                        elif key == "ipAddresses":
                            properties[symantec_to_ct_props_map[key]] = endpoint_data[key][0]
                        elif key in symantec_to_ct_props_map:
                            properties[symantec_to_ct_props_map[key]] = value
                    endpoint["properties"] = properties
                    endpoints.append(endpoint)
                is_last_page = poll_response_dict["lastPage"]
                #check if this is the last page of the response or the last page the user want to poll (when poll page range is set)
                if is_last_page or (page_range and page_index >= page_end_index):
                    pagination_completed = True
                else:
                    #polling the next page if last page is not reached
                    page_index += 1
        logging.debug(f"Got {len(endpoints)} endpoints: {endpoints}")
        response["endpoints"] = endpoints
    except HTTPError as e:
        http_error_msg = f"HTTP Error : Could not connect to Symantec server. Error code: {e.code}"
        response["error"] = http_error_msg
        logging.debug(http_error_msg)
    except URLError as e:
        url_error_msg = f"URL Error : Could not connect to Symantec server. Reason: {e.reason}"
        response["error"] = url_error_msg
        logging.debug(url_error_msg)
    except Exception as e:
        exp_error_msg = f"Could not connect to Symantec server. Exception: {e}"
        response["error"] = exp_error_msg
        logging.debug(exp_error_msg)
else:
    error_msg = "Bearer token is not available or empty"
    response["error"] = error_msg
    logging.debug(error_msg)