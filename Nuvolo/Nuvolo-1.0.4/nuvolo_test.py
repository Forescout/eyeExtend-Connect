"""
Nuvolo Test Script for Forescout Connect App

This script validates Nuvolo configuration and tests API connectivity.
It demonstrates successful OAuth2 authentication and basic API access.

Author: Forescout
Version: 1.0.0
"""

import ssl
import logging

# Library functions are dynamically loaded - no direct import

# Initialize response dictionary
response = {}

def test_nuvolo_configuration():
    """
    Test Nuvolo configuration including:
    1. Credential validation
    2. OAuth2 authentication
    3. API connectivity by making a simple API request
    
    Returns:
        dict: Response with 'succeeded' (bool) and 'result_msg' (str) if failed
    """
    try:
        # Get connection parameters
        instance_url = params.get("connect_nuvolo_instance_url", "")
        client_id = params.get("connect_nuvolo_client_id", "")
        client_secret = params.get("connect_nuvolo_client_secret", "")
        
        # Validate credentials using library function
        cred_error = nuvolo_lib.validate_credentials(client_id, client_secret, instance_url)
        if cred_error:
            return {
                "succeeded": False,
                "result_msg": f"Configuration Error: {cred_error}"
            }
        
        logging.debug(f"Testing Nuvolo configuration for instance: {instance_url}")
        
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
        
        # Step 1: Get OAuth2 access token
        access_token, expires_in = nuvolo_lib.get_oauth2_token(
            instance_url, client_id, client_secret, opener
        )
        
        if not access_token:
            return {
                "succeeded": False,
                "result_msg": "Authentication failed: Unable to retrieve OAuth2 access token. Please verify Client ID and Client Secret."
            }
        
        logging.debug("OAuth2 authentication successful")
        
        # Step 2: Test API connectivity with a simple GET request
        # Test by verifying we can access the staging table endpoint
        test_url = f"https://{instance_url}/api/now/table/x_nuvo_eam_forescout_clinical_device_staging?sysparm_limit=1"
        
        response_data, status_code = nuvolo_lib.make_api_request(
            test_url, access_token, opener
        )

        # Treat 404 as a failure indicating a missing or inaccessible staging table
        if status_code == 404:
            return {
                "succeeded": False,
                "result_msg": "API connectivity test failed: staging table 'x_nuvo_eam_forescout_clinical_device_staging' not found or inaccessible (HTTP 404). Please verify that the table exists and that the OAuth client has sufficient permissions."
            }

        if response_data is None or status_code != 200:
            return {
                "succeeded": False,
                "result_msg": f"API connectivity test failed: HTTP {status_code}. Please verify instance URL, network connectivity, and API permissions."
            }

        # Success - we received a valid response from the staging table endpoint
        logging.debug("API connectivity test successful")
        
        return {
            "succeeded": True
        }
        
    except Exception as e:
        logging.error(f"Test script error: {str(e)}")
        return {
            "succeeded": False,
            "result_msg": f"Test failed with error: {str(e)}"
        }


# Execute test function at module level
response = test_nuvolo_configuration()
