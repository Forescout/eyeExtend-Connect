"""
Nuvolo Post Asset Action Script for Forescout Connect App

This script posts discovered endpoint data to the Nuvolo device discovery staging table.
It uses the field mappings defined in the FIELD_MAPPINGS dictionary to map Forescout properties to Nuvolo columns.

Author: Forescout
Version: 1.0.0
"""

import ssl
import json
import logging
from datetime import datetime

# Library functions are dynamically loaded - no direct import

# Fields that contain Unix timestamps and need conversion to datetime format
TIMESTAMP_FIELDS = ["otsm_details_first_seen", "otsm_details_last_seen"]

# Fields that should be sent as numeric values (not strings)
NUMERIC_FIELDS = ["cysiv_risk_score"]

def convert_unix_timestamp_to_datetime(timestamp):
    """
    Convert Unix timestamp to ServiceNow glide_date_time format (YYYY-MM-DD HH:MM:SS)
    Args:
        timestamp: Unix timestamp (seconds since epoch) as string or int
    Returns:
        Formatted datetime string or None if conversion fails
    """
    try:
        timestamp_int = int(timestamp)
        dt = datetime.utcfromtimestamp(timestamp_int)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError, OSError) as e:
        logging.warning(f"Failed to convert timestamp {timestamp}: {str(e)}")
        return None

# Field mappings from Forescout properties to Nuvolo table columns
FIELD_MAPPINGS = {
    "otsm_details_first_seen": "u_first_discovered",
    "otsm_details_last_seen": "u_most_recent_discovery",
    "cysiv_risk_severity": "u_security_impact_overall",
    "rem_fda_class": "u_security_impact_patient",
    "rem_phi": "u_security_impact_data",
    "rem_function": "u_security_impact_business",
    "cysiv_risk_score": "u_security_risk_score",
    "wifi_ssid": "u_discovered_network_names",
    "otsm_details_host_name": "u_discovered_hostname",
    "os_details_classification": "u_discovered_os",  # Parses JSON: parent+flavor -> u_discovered_os, version -> u_discovered_os_version, build -> u_discovered_os_revision
    "comp_application": "u_discovered_software_version",
    "otsm_details_firmware_version": "u_discovered_firmware_version",
    "otsm_details_host_mac_addresses": "u_discovered_mac",
    "ip": "u_discovered_ip",
    # "u_discovered_device" is constructed from "manufacturer_classification" and "connect_nuvolo_host_role"
    "otsm_details_serial_number": "u_discovered_sn",
    "sw_ipport": "u_switch_ip_and_port_number"
}

# Initialize response dictionary
response = {}

try:
    # Get connection parameters
    instance_url = params.get("connect_nuvolo_instance_url", "")
    access_token = params.get("connect_authorization_token", "")
    
    # Validate instance URL
    if not instance_url:
        response = {
            "succeeded": False,
            "troubleshooting": "Nuvolo Instance URL is not configured"
        }
        logging.error("Instance URL is missing")
    elif not access_token:
        response = {
            "succeeded": False,
            "troubleshooting": "OAuth2 authorization token is not available. Please check authorization configuration."
        }
        logging.error("Authorization token is missing")
    else:
        # Configure SSL context
        ssl_context = ssl.create_default_context()

        # Certificate validation setting
        cert_validation = params.get("connect_certification_validation")
        if cert_validation and str(cert_validation).lower() == 'false':
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        else:
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # Proxy configuration
        proxy_enable = params.get("connect_proxy_enable")
        proxy_ip = params.get("connect_proxy_ip", "")
        proxy_port = params.get("connect_proxy_port", "")
        proxy_username = params.get("connect_proxy_username", "")
        proxy_password = params.get("connect_proxy_password", "")
        
        # Configure proxy and SSL
        opener = nuvolo_lib.handle_proxy_configuration(
            proxy_enable, proxy_ip, proxy_port, proxy_username, proxy_password, ssl_context
        )
        
        # Remove https:// prefix if present in instance_url
        if instance_url.startswith('https://'):
            instance_url = instance_url.replace('https://', '')
        if instance_url.startswith('http://'):
            instance_url = instance_url.replace('http://', '')
        
        # Remove trailing slash if present
        if instance_url.endswith('/'):
            instance_url = instance_url[:-1]
        
        # Build payload by mapping Forescout properties to Nuvolo columns
        payload = {}
        
        # Parse os_details_classification JSON for OS, OS version and OS revision
        os_details_classification = params.get("os_details_classification")
        if os_details_classification:
            try:
                # Parse JSON format: {"flavor":"Enterprise","parent":"Windows 11 64-bit","build":"7623.26200","arch":"64-bit","sp":null,"version":"25H2"}
                # Extract parent and flavor (combined for OS), version (OS version) and build (OS revision)
                os_data = None
                
                # Check if it's already a dict
                if isinstance(os_details_classification, dict):
                    os_data = os_details_classification
                else:
                    # If it's a string, parse as JSON
                    os_data = json.loads(str(os_details_classification))
                
                # Extract fields from parsed JSON
                os_parent = os_data.get('parent')
                os_flavor = os_data.get('flavor')
                os_version = os_data.get('version')
                os_revision = os_data.get('build')
                
                # Combine parent and flavor for os_name (e.g., "Windows 11 64-bit - Enterprise")
                if os_parent and os_flavor:
                    os_name = f"{os_parent} - {os_flavor}"
                    payload["u_discovered_os"] = os_name
                    logging.debug(f"Parsed OS from os_details_classification: {os_name}")
                elif os_parent:
                    # If no flavor, just use parent
                    payload["u_discovered_os"] = os_parent
                    logging.debug(f"Parsed OS from os_details_classification: {os_parent}")
                
                if os_version:
                    payload["u_discovered_os_version"] = os_version
                    logging.debug(f"Parsed OS version from os_details_classification: {os_version}")
                if os_revision:
                    payload["u_discovered_os_revision"] = os_revision
                    logging.debug(f"Parsed OS revision from os_details_classification: {os_revision}")
            except Exception as parse_error:
                logging.warning(f"Failed to parse os_details_classification: {str(parse_error)}")
        
        # Handle u_last_discovery_location: use sw_ipport first, fallback to wifi_ap_location
        location_value = params.get("sw_ipport")
        if not location_value:
            location_value = params.get("wifi_ap_location")
        if location_value:
            payload["u_last_discovery_location"] = str(location_value)
           
        # Iterate through field mappings and extract values from params
        for forescout_prop, nuvolo_column in FIELD_MAPPINGS.items():
            value = params.get(forescout_prop)
            logging.debug(f"Property name: {forescout_prop}, Value: {value}")
            if value is not None and value != "":
                # Skip os_details_classification - already parsed above
                if forescout_prop == "os_details_classification":
                    # Already handled in the parsing section above
                    pass
                # Convert Unix timestamps to datetime format for glide_date_time fields
                elif forescout_prop in TIMESTAMP_FIELDS:
                    converted_value = convert_unix_timestamp_to_datetime(value)
                    if converted_value:
                        payload[nuvolo_column] = converted_value
                        logging.debug(f"Converted timestamp {value} to {converted_value}")
                # Keep numeric fields as numbers for proper ServiceNow field type handling
                elif forescout_prop in NUMERIC_FIELDS:
                    try:
                        # Try to convert to float for numeric fields
                        payload[nuvolo_column] = float(value)
                        logging.debug(f"Converted numeric field {forescout_prop}: {value} -> {float(value)}")
                    except (ValueError, TypeError):
                        # If conversion fails, send as string
                        payload[nuvolo_column] = str(value)
                        logging.warning(f"Could not convert {forescout_prop} value '{value}' to float, sending as string")
                # Handle MAC address - strip brackets and quotes from ["08:92:04:c0:8b:ee"] format
                elif forescout_prop == "otsm_details_host_mac_addresses":
                    mac_value = value
                    # If it's a list, get the first element
                    if isinstance(mac_value, list) and len(mac_value) > 0:
                        mac_value = mac_value[0]
                    # Convert to string and strip any quotes or brackets
                    mac_str = str(mac_value).strip('[]"\'')
                    if mac_str:
                        payload[nuvolo_column] = mac_str
                        logging.debug(f"Cleaned MAC address from '{value}' to '{mac_str}'")
                else:
                    payload[nuvolo_column] = str(value)

        # Additional field: u_discovered_device (from manufacturer and role)
        manufacturer = params.get("manufacturer_classification", "")
        role = params.get("otsm_details_role", "")
        logging.debug(f"Manufacturer from manufacturer_classification: '{manufacturer}'")
        logging.debug(f"Role from otsm_details_role: '{role}'")
        if manufacturer or role:
            discovered_device = f"{manufacturer} - {role}".strip(' -')
            payload["u_discovered_device"] = discovered_device
            logging.debug(f"Constructed u_discovered_device: '{discovered_device}'")
        
        # Construct u_discovery_source_url from Forescout Cloud URL and asset ID
        forescout_cloud_url = params.get("connect_nuvolo_forescout_cloud_url", "")
        asset_id = params.get("cde_eyefocus_asset_id", "")
        
        if forescout_cloud_url or asset_id:
            # Remove trailing slash from cloud URL if present
            cloud_url = forescout_cloud_url.rstrip('/')
            # Construct the full asset URL
            discovery_source_url = f"{cloud_url}/#/assets/{asset_id}"
            payload["u_discovery_source_url"] = discovery_source_url
            logging.debug(f"Constructed discovery source URL: {discovery_source_url}")
        
        # Log the payload for debugging
        logging.debug(f"Posting asset data to Nuvolo: {payload}")
        
        # Construct API endpoint URL
        api_url = f"https://{instance_url}/api/now/table/x_nuvo_eam_forescout_clinical_device_staging"
        
        # Make POST request
        response_data, status_code = nuvolo_lib.make_api_request(
            api_url, access_token, opener, method='POST', data=payload
        )
        
        # Log the full response for debugging
        logging.debug(f"ServiceNow response status: {status_code}")
        logging.debug(f"ServiceNow response data: {response_data}")
        
        # Check response
        if status_code == 201 and response_data:
            # Success - record created
            sys_id = response_data.get('result', {}).get('sys_id', 'unknown')
            result = response_data.get('result', {})
            
            # Log what was actually saved to help debug missing fields
            logging.debug(f"Asset record created successfully with sys_id: {sys_id}")
            logging.debug(f"Saved record - OS: {result.get('u_discovered_os')}, Version: {result.get('u_discovered_os_version')}, Revision: {result.get('u_discovered_os_revision')}")
            response = {"succeeded": True}
        elif status_code == 200 and response_data:
            # Also accept 200 as success
            logging.debug("Asset record processed successfully")
            response = {"succeeded": True}
        else:
            # Failure
            error_msg = f"Failed to post asset data: HTTP {status_code}"
            if response_data:
                error_detail = response_data.get('error', {}).get('message', 'Unknown error')
                error_msg = f"{error_msg} - {error_detail}"
            logging.error(error_msg)
            response = {
                "succeeded": False,
                "troubleshooting": error_msg
            }

except Exception as e:
    response = {
        "succeeded": False,
        "troubleshooting": f"Action failed with error: {str(e)}"
    }
    logging.error(f"Post asset action error: {str(e)}")
