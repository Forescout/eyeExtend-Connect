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

from urllib import request
from urllib.request import HTTPError, URLError
import logging
import json

#
# FUNCTIONS
#
def get_nac_data():
    ''' Get NAC data by MAC address
    '''
    # Modify global variable
    global succeed_flag

    # Init vars
    nac_result_message = []
    nac_response_dict = {}

    if NAC_TOKEN:
        bearer_header = {"Authorization": "Bearer " + NAC_TOKEN}

        nac_url = f"{P_SERVICE_URI}/devices/?querycriteria=macaddress&api-version=1.1&value={P_TEST_MAC_ADDRESS}"
        logging.info("TEST RESOLVE QUERY : [%s]", nac_url)

        try:
            logging.debug("Starting NAC TEST...")
            # Create proxy server
            proxy_server = intune_proxy_server.ConnectProxyServer()
            proxy_server.set_init(params)
            opener = proxy_server.get_urllib_request_https_opener(intune_proxy_server.ProxyProtocol.all, ssl_context)
            nac_request = request.Request(nac_url, headers=bearer_header)
            nac_response = request.urlopen(nac_request)

            logging.debug("nac_response code  : [%s]", nac_response.getcode())

            nac_response_dict = json.loads(nac_response.read())
            logging.debug("nac_response_dict : [%s]", nac_response_dict)

            # Check azureDeviceID key exists in response
            if "azureDeviceId" in nac_response_dict:

                # Check if the device is managed
                if nac_response_dict["isManaged"]:
                    nac_result_message.append(f"We have NAC Token : [{NAC_TOKEN[0:50]}]\n")
                    nac_result_message.append("Successfully connected NAC service.")
                    nac_result_message.append(f"** Query : {nac_url}\n")
                    nac_result_message.append(f"** JSON **\n{json.dumps(nac_response_dict)}\n")

                else:
                    nac_result_message.append(f"We have NAC Token : [{NAC_TOKEN[0:50]}]\n")
                    nac_result_message.append("Successfully connected NAC service.")
                    nac_result_message.append("###########################\n## MAC address NOT FOUND ##\n###########################")
                    nac_result_message.append(f"** Query : {nac_url}\n")
                    nac_result_message.append(f"** JSON **\n{nac_response_dict}\n")

                    succeed_flag = True

            else:
                    nac_result_message.append(f"We have NAC Token : [{NAC_TOKEN[0:50]}]\n")
                    nac_result_message.append("Successfully connected NAC service.")
                    nac_result_message.append("###########################\n## azureDeviceId NOT FOUND ##\n###########################")
                    nac_result_message.append(f"** JSON **\n{nac_response_dict}\n")

        except HTTPError as e:
            succeed_flag = False
            nac_result_message.append(f"## HTTP Error : NAC RESPONSE ERROR : {e.code}\n")

        except URLError as e:
            succeed_flag = False
            nac_result_message.append(f"## URL Error : NAC RESPONSE ERROR : {e.reason}\n")

        except Exception as e:
            succeed_flag = False
            nac_result_message.append(f"## Exception : NAC RESPONSE ERROR : {str(e)}\n")

        return (nac_result_message, nac_response_dict.get("azureDeviceId"), nac_response_dict.get("isManaged") )

    else:
        succeed_flag = False
        nac_result_message.append(f"## NAC Token is not valid: [{NAC_TOKEN[0:50]}]\n")
        return (nac_result_message, None, None)

def get_graph_data(passed_filter, passed_filter_value):
    ''' Get GRAPH data for device_id
    '''
    # Modify global variable
    global succeed_flag

    # Init variables
    graph_result_message = []

    # Used to build query url
    SPACE = "%20"
    QUOTE = "%27"

    if GRAPH_TOKEN:
        # Build GRAPH API Query
        user_header = {"Authorization": "Bearer " + GRAPH_TOKEN}

        url_filter = "?$filter=" + passed_filter + SPACE + "eq" + SPACE + QUOTE + passed_filter_value + QUOTE

        graph_url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices" + url_filter

        try:
            logging.info("Test Query : %s", graph_url)
            # Create proxy server
            proxy_server = intune_proxy_server.ConnectProxyServer()
            proxy_server.set_init(params)
            opener = proxy_server.get_urllib_request_https_opener(intune_proxy_server.ProxyProtocol.all, ssl_context)

            graph_request = request.Request(graph_url, headers=user_header)
            graph_response = request.urlopen(graph_request)

            graph_response_dict = json.loads(graph_response.read())

            count = graph_response_dict["@odata.count"]
            logging.debug('Count : %s', count)

            #graph_response_json = json.dumps(graph_response_dict)
            #logging.debug("graph_response_json : %s", graph_response_json)

            # Check we found the device
            if count != 0:
                graph_result_message.append(f"We have GRAPH Token : [{GRAPH_TOKEN[0:50]}]\n")
                graph_result_message.append("Successfully connected GRAPH service.")
                graph_result_message.append(f"** Query : {graph_url}\n")
                graph_result_message.append(f"** JSON **\n{json.dumps(graph_response_dict)}\n")
            else:
                graph_result_message.append(f"We have GRAPH Token : [{GRAPH_TOKEN[0:50]}]\n")
                graph_result_message.append("Successfully connected GRAPH service.")
                graph_result_message.append("######################\n## Device NOT FOUND ##\n######################")
                graph_result_message.append(f"** Query : {graph_url}\n")

            succeed_flag = True

        except HTTPError as e:
            succeed_flag = False
            graph_result_message.append(f"## HTTP Error : GRAPH RESPONSE ERROR CODE : {e.code}\n")

        except URLError as e:
            succeed_flag = False
            graph_result_message.append(f"## URL Error : GRAPH RESPONSE ERROR REASON : {e.reason}\n")

        except Exception as e:
            succeed_flag = False
            graph_result_message.append(f"## Exception : GRAPH RESPONSE ERROR GENERAL : {str(e)}\n")

    else:
        succeed_flag = False
        graph_result_message.append("## GRAPH Token is not valid\n")

    return graph_result_message

#
# FUNCTIONS END
#

# Init
# Used to build console message output (append to list and then join to console_test message string)
result_test_message = []
graph_result_test_message = []
nac_result_test_message = []
console_test_message = ""
#
succeed_flag = False
response = {}

# Get TEST Parameters
P_TEST_IMEI = params.get('connect_intune_test_imei')
P_TEST_SERIAL_NUMBER = params.get('connect_intune_test_serial_number')
P_TEST_DEVICE_NAME = params.get('connect_intune_test_device_name')
P_TEST_MAC_ADDRESS = params.get('connect_intune_test_mac')
P_SERVICE_URI = params.get('connect_intune_service_endpoint_uri')

# Convert tokens from STR to DICT
P_STR_TOKENS = params.get("connect_authorization_token")

# Check Service Endpoint URI has https://
if "https://" in P_SERVICE_URI:
    console_test_message =  console_test_message + "## Service Endpoint URI contains https:// ** Looks Good **\n\n"
else:
    console_test_message =  console_test_message + "## Service Endpoint URI does NOT contain https://\n### CHECK Intune Connection TAB\n\n"


# Make sure we have tokens
if P_STR_TOKENS:
    # Extract str tokens to dict
    DICT_TOKENS = json.loads(P_STR_TOKENS)

    # Get GRAPH and NAC tokens
    GRAPH_TOKEN = DICT_TOKENS.get("graph_token")
    NAC_TOKEN = DICT_TOKENS.get("nac_token")

    # Check we have a MAC Address for NAC Query
    if P_TEST_MAC_ADDRESS:
        logging.debug("TEST NAC Query")
        # NAC Query and GRAPH query using device ID obtained from NAC Query
        # Flow used to resolve properties

        # NAC Query
        nac_result_test_message, azure_device_id, azure_is_managed = get_nac_data()

        # GRAPH query
        if azure_is_managed:
            graph_result_test_message = get_graph_data("azureADDeviceId", azure_device_id)
        else:
            graph_result_test_message.append("## NO Azure Device ID Found, skipping GRAPH Query.")

        result_test_message = nac_result_test_message + graph_result_test_message

    else:
        logging.debug("TEST GRAPH Query")
        # Skip NAC query as MAC Address not populated

        # Check we have GRAPH properties populated
        if P_TEST_IMEI == P_TEST_SERIAL_NUMBER == P_TEST_DEVICE_NAME == '':
            graph_result_test_message.append("###########################################")
            graph_result_test_message.append("## Check you have populated the TEST tab ##")
            graph_result_test_message.append("###########################################")

            result_test_message = graph_result_test_message
        else:
            # GRAPH API Query ONLY
            graph_filter = ""
            graph_filter_value = ""

            if P_TEST_IMEI:
                graph_filter = "imei"
                graph_filter_value = P_TEST_IMEI
            elif P_TEST_SERIAL_NUMBER:
                graph_filter = "serialNumber"
                graph_filter_value = P_TEST_SERIAL_NUMBER
            elif P_TEST_DEVICE_NAME:
                graph_filter = "deviceName"
                graph_filter_value = P_TEST_DEVICE_NAME

            # GRAPH query
            result_test_message = get_graph_data(graph_filter, graph_filter_value)
else:
    # Token ISSUE
    console_test_message = "No Authentication Bearer Tokens. SKIPPING checks. Check Credentials"

# Build console output
if succeed_flag:
    logging.info("Test Query Succeeded : %s", succeed_flag)
    console_test_message = console_test_message + "\n".join(result_test_message)
    response["succeeded"] = True
    response["result_msg"] = console_test_message
else:
    logging.info("Test Query Failed : %s", succeed_flag)
    console_test_message = console_test_message + "\n".join(result_test_message)
    response["succeeded"] = False
    response["result_msg"] = console_test_message
