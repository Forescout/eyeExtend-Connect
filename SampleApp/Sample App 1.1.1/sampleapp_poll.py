import urllib.request
from connectproxyserver import ConnectProxyServer, ProxyProtocol

# Mapping between SampleApp API response fields to CounterACT properties
sampleapp_to_ct_props_map = {
    "state": "connect_sampleapp_state",
    "mac_addresses": "connect_sampleapp_mac_addresses",
    "id": "connect_sampleapp_id"
}

# CONFIGURATION
url = params.get("connect_sampleapp_url")  # Server URL

response = {}
endpoints = []
logging.debug("SampleApp polling.")
# Check if we have valid auth token or not before processing.
if params.get("connect_authorization_token"):
    # ***** PART 2 - QUERY FOR DEVICES  ***** #
    jwt_token = params.get("connect_authorization_token")
    get_mac_url = url + "/devices/v2/"
    device_headers = {"Content-Type": "application/json; charset=utf-8",
                      "Authorization": "Bearer " + str(jwt_token)}

    try:
        # Create proxy server
        proxy_server = ConnectProxyServer(params)
        # Pass to use what HTTPS or HTTP or both in the protocol, pass down the ssl_context
        opener = proxy_server.get_urllib_request_https_opener(ProxyProtocol.all,
                                                              ssl_context)
        poll_request = urllib.request.Request(get_mac_url,
                                              headers=device_headers)
        # Use opener.open to get the request ( you can use urlopen as well, look at resolve script
        poll_response = opener.open(poll_request)
        poll_response_json = json.loads(poll_response.read().decode("utf-8"))
        logging.debug(
            "Response json: {}".format(json.dumps(poll_response_json)))

        # For polling, the response dictionary must contain a list called "endpoints", which will contain new
        # endpoint information. Each endpoint must have a field named either "mac" or "ip". The endpoint
        # object/dictionary may also have a "properties" field, which contains property information in the format
        # {"property_name": "property_value"}.
        # The full response object, for example would be:
        # {"endpoints": [
        #     {
        #         "mac": "001122334455",
        #         "properties": {
        #         	"property1": "property_value",
        #         	"property2": "property_value2"}
        #     }
        # ] }
        for endpoint_data in poll_response_json.get("page_items"):
            endpoint = {}
            mac_with_dash = endpoint_data.get("mac_addresses")[0]
            mac = "".join(mac_with_dash.split("-"))
            endpoint["mac"] = mac
            properties = {}
            for key, value in endpoint_data.items():
                if key in sampleapp_to_ct_props_map and key is not "mac_addresses":
                    properties[sampleapp_to_ct_props_map[key]] = value
            endpoint["properties"] = properties
            endpoints.append(endpoint)
        response["endpoints"] = endpoints
    except Exception as e:
        response["error"] = "Could not retrieve endpoints."
        logging.debug("Get error: {}".format(str(e)))
else:
    response["error"] = "Unauthorized"
