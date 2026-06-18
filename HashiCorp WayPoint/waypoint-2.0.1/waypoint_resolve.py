"""
WayPoint Resolve Script
Looks up a device in Ivanti ISM by MAC address or hostname using OData API
"""
import json
import logging
import urllib.request
import urllib.error

# Configuration
url_call = params["connect_waypoint_base_url"].rstrip('/')
bearer_token = params["connect_authorization_token"]

response = {}

try:
    # Get MAC address from Forescout
    if "mac" not in params:
        raise ValueError("MAC address not available for this device")

    mac_address = params["mac"]
    logging.debug("Looking up MAC: " + mac_address)

    # API call headers
    header_info = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': bearer_token
    }

    found = False
    hostname = ""

    # Step 1: Try exact MAC match (lowercase)
    target_url = url_call + "/odata/businessobject/CIs?$filter=MACAddress%20eq%20'" + mac_address.lower() + "'"
    logging.debug("Trying MAC eq URL: " + target_url)

    request_obj = urllib.request.Request(target_url, headers=header_info)
    raw_response = urllib.request.urlopen(request_obj, context=ssl_context)
    status_code = raw_response.getcode()
    raw_body = raw_response.read().decode('utf-8')

    if status_code != 204 and raw_body:
        response_data = json.loads(raw_body)
        records = response_data.get('value', [])

        if records:
            record = records[0]
            mac_value = record.get("MACAddress", "")
            if mac_value:
                response["properties"] = {"connect_waypoint_mac": mac_value}
                logging.debug("Device found by MAC eq: " + mac_value)
                found = True

    # Step 2: If MAC eq didn't match, try hostname lookup via CHTR_Hostname
    if not found:
        # Get hostname from Forescout (try dhcp_hostname_v2 first, then nbthost)
        hostname = ""
        if "dhcp_hostname_v2" in params and params["dhcp_hostname_v2"]:
            hostname = params["dhcp_hostname_v2"]
            logging.debug("Using dhcp_hostname_v2: " + hostname)
        elif "nbthost" in params and params["nbthost"]:
            hostname = params["nbthost"]
            logging.debug("Using nbthost: " + hostname)
        elif "hostname" in params and params["hostname"]:
            hostname = params["hostname"]
            logging.debug("Using hostname: " + hostname)

        if hostname:
            # Clean hostname - remove any trailing null chars or whitespace
            hostname = hostname.strip().split('\x00')[0].split('\\')[0]
            logging.debug("Cleaned hostname: " + hostname)
            
            target_url = url_call + "/odata/businessobject/CIs?$filter=CHTR_Hostname%20eq%20'" + hostname + "'"
            logging.debug("Trying hostname URL: " + target_url)

            request_obj = urllib.request.Request(target_url, headers=header_info)
            raw_response = urllib.request.urlopen(request_obj, context=ssl_context)
            status_code = raw_response.getcode()
            raw_body = raw_response.read().decode('utf-8')

            if status_code != 204 and raw_body:
                response_data = json.loads(raw_body)
                records = response_data.get('value', [])

                if records:
                    record = records[0]
                    mac_value = record.get("MACAddress", "")
                    if mac_value:
                        response["properties"] = {"connect_waypoint_mac": mac_value}
                        logging.debug("Device found by hostname: " + mac_value)
                        found = True

    if not found:
        response["properties"] = {}
        hostname_info = hostname if hostname else "no hostname available"
        logging.debug("Device not found in Ivanti. MAC: " + mac_address + " | Hostname: " + hostname_info)

except urllib.error.HTTPError as e:
    error_body = ""
    try:
        error_body = e.read().decode('utf-8')
    except Exception:
        pass
    response["succeeded"] = False
    response["error"] = "HTTP " + str(e.code) + ": " + str(e.reason) + " | " + error_body[:200]
    logging.error("Resolve failed: HTTP " + str(e.code) + " " + str(e.reason))

except Exception as e:
    response["succeeded"] = False
    response["error"] = "Resolve failed: " + str(e)
    logging.error("Resolve failed: " + str(e))
