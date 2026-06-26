"""
Nuvolo Library for Forescout Connect App

This library provides shared functions for OAuth2 authentication and API communication
with the Nuvolo ServiceNow platform.

Author: Forescout
Version: 1.0.0
"""

import json
import urllib.request
import urllib.parse
from urllib.error import HTTPError, URLError
import socket
import logging


def handle_proxy_configuration(proxy_enable, proxy_ip, proxy_port, proxy_username, proxy_password, ssl_context):
    """
    Configure proxy handler for API requests.
    
    Args:
        proxy_enable: Proxy enable setting from params
        proxy_ip: Proxy server IP address
        proxy_port: Proxy server port
        proxy_username: Proxy username (optional)
        proxy_password: Proxy password (optional)
        ssl_context: SSL context for secure connections
        
    Returns:
        urllib.request.OpenerDirector: Configured opener with proxy settings
    """
    try:
        # Create HTTPS handler with SSL context
        https_handler = urllib.request.HTTPSHandler(context=ssl_context)
        
        # Check if proxy is enabled
        if proxy_enable and str(proxy_enable).lower() == 'true':
            if proxy_ip and proxy_port:
                proxy_url = f"http://{proxy_ip}:{proxy_port}"
                
                # Configure proxy with authentication if provided
                if proxy_username and proxy_password:
                    proxy_auth = urllib.request.HTTPPasswordMgrWithDefaultRealm()
                    proxy_auth.add_password(None, proxy_url, proxy_username, proxy_password)
                    proxy_handler = urllib.request.ProxyHandler({'https': proxy_url})
                    proxy_auth_handler = urllib.request.ProxyBasicAuthHandler(proxy_auth)
                    opener = urllib.request.build_opener(proxy_handler, proxy_auth_handler, https_handler)
                else:
                    proxy_handler = urllib.request.ProxyHandler({'https': proxy_url})
                    opener = urllib.request.build_opener(proxy_handler, https_handler)
                
                logging.debug(f"Configured proxy: {proxy_ip}:{proxy_port}")
                return opener
        
        # No proxy configuration
        opener = urllib.request.build_opener(https_handler)
        return opener
        
    except Exception as e:
        logging.error(f"Error configuring proxy: {str(e)}")
        # Fallback to default opener
        https_handler = urllib.request.HTTPSHandler(context=ssl_context)
        opener = urllib.request.build_opener(https_handler)
        return opener


def get_oauth2_token(instance_url, client_id, client_secret, opener):
    """
    Retrieve OAuth2 access token from Nuvolo ServiceNow instance.
    
    Args:
        instance_url: ServiceNow instance URL (e.g., ven05225.service-now.com)
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        opener: urllib opener with proxy/SSL configuration
        
    Returns:
        tuple: (access_token, expires_in) or (None, None) on error
    """
    try:
        # Construct token endpoint URL
        token_url = f"https://{instance_url}/oauth_token.do"
        
        # Prepare OAuth2 token request data
        data = urllib.parse.urlencode({
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }).encode('utf-8')
        
        # Build request
        token_request = urllib.request.Request(token_url, data=data, method='POST')
        token_request.add_header("Content-Type", "application/x-www-form-urlencoded")
        token_request.add_header("Accept", "application/json")
        
        logging.debug(f"Requesting OAuth2 token from: {token_url}")
        
        # Make request with timeout
        response_handle = opener.open(token_request, timeout=30)
        response_data = response_handle.read().decode("utf-8")
        
        # Parse response
        response_json = json.loads(response_data)
        
        if 'access_token' in response_json:
            access_token = response_json['access_token']
            expires_in = response_json.get('expires_in', 1799)
            logging.debug("OAuth2 token retrieved successfully")
            return access_token, expires_in
        else:
            logging.error("OAuth2 token not found in response")
            return None, None
            
    except socket.timeout:
        logging.error("Timeout during OAuth2 token retrieval")
        return None, None
    except HTTPError as e:
        logging.error(f"HTTP error during OAuth2 token retrieval: {e.code}")
        if hasattr(e, 'read'):
            error_response = e.read().decode('utf-8')
            logging.error(f"Error response: {error_response}")
        return None, None
    except URLError as e:
        logging.error(f"URL error during OAuth2 token retrieval: {e.reason}")
        return None, None
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {str(e)}")
        return None, None
    except Exception as e:
        logging.error(f"Unexpected error during OAuth2 token retrieval: {str(e)}")
        return None, None


def make_api_request(url, access_token, opener, method='GET', data=None):
    """
    Make authenticated API request to Nuvolo ServiceNow instance.
    
    Args:
        url: API endpoint URL
        access_token: OAuth2 access token
        opener: urllib opener with proxy/SSL configuration
        method: HTTP method (GET, POST, etc.)
        data: Request payload (for POST requests)
        
    Returns:
        tuple: (response_data, status_code) or (None, error_code) on error
    """
    try:
        # Build request
        if data and method == 'POST':
            if isinstance(data, dict):
                data = json.dumps(data).encode('utf-8')
            request = urllib.request.Request(url, data=data, method=method)
            request.add_header("Content-Type", "application/json")
        else:
            request = urllib.request.Request(url, method=method)
        
        # Add authentication and headers
        request.add_header("Authorization", f"Bearer {access_token}")
        request.add_header("Accept", "application/json")
        
        logging.debug(f"Making {method} request to: {url}")
        
        # Make request with timeout
        response_handle = opener.open(request, timeout=30)
        response_data = response_handle.read().decode("utf-8")
        status_code = response_handle.getcode()
        
        # Parse JSON response
        response_json = json.loads(response_data)
        
        return response_json, status_code
        
    except socket.timeout:
        logging.error("Timeout during API request")
        return None, None
    except HTTPError as e:
        logging.error(f"HTTP error during API request: {e.code}")
        if hasattr(e, 'read'):
            error_response = e.read().decode('utf-8')
            logging.error(f"Error response: {error_response}")
        return None, e.code
    except URLError as e:
        logging.error(f"URL error during API request: {e.reason}")
        return None, None
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {str(e)}")
        return None, None
    except Exception as e:
        logging.error(f"Unexpected error during API request: {str(e)}")
        return None, None


def validate_credentials(client_id, client_secret, instance_url):
    """
    Validate that required credentials are provided.
    
    Args:
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        instance_url: ServiceNow instance URL
        
    Returns:
        str: Error message if validation fails, None if successful
    """
    if not instance_url:
        return "Nuvolo Instance URL is required"
    if not client_id:
        return "Client ID is required"
    if not client_secret:
        return "Client Secret is required"
    return None
