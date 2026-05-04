"""
Nuvolo OAuth2 Authorization Script for Forescout Connect App

This script handles OAuth2 token retrieval for the Nuvolo ServiceNow API.
It implements the client credentials OAuth2 flow as documented in the ServiceNow API.

Author: Forescout
Version: 1.0.0
"""

import ssl
import logging

# Library functions are dynamically loaded - no direct import

# Get connection parameters
instance_url = params.get("connect_nuvolo_instance_url", "")
client_id = params.get("connect_nuvolo_client_id", "")
client_secret = params.get("connect_nuvolo_client_secret", "")

# Proxy configuration
proxy_enable = params.get("connect_proxy_enable")
proxy_ip = params.get("connect_proxy_ip", "")
proxy_port = params.get("connect_proxy_port", "")
proxy_username = params.get("connect_proxy_username", "")
proxy_password = params.get("connect_proxy_password", "")

# SSL context configuration
ssl_context = ssl.create_default_context()

# Certificate validation setting
cert_validation = params.get("connect_certification_validation")
if cert_validation and str(cert_validation).lower() == 'false':
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
else:
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED

# Initialize response dictionary
response = {}

try:
    # Validate credentials using library function
    cred_error = nuvolo_lib.validate_credentials(client_id, client_secret, instance_url)
    if cred_error:
        response = {"token": ""}
        logging.error(f"Credential validation failed: {cred_error}")
    else:
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
        
        # Get OAuth2 access token
        access_token, expires_in = nuvolo_lib.get_oauth2_token(
            instance_url, client_id, client_secret, opener
        )
        
        if access_token:
            response = {"token": access_token}
            logging.debug(f"OAuth2 token retrieved successfully, expires in {expires_in} seconds")
        else:
            response = {"token": ""}
            logging.error("Failed to retrieve OAuth2 access token")

except Exception as e:
    response = {"token": ""}
    logging.error(f"Authorization script error: {str(e)}")
