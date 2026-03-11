"""
Twilio Connect App - Shared Library
Provides helper functions for Twilio API communication.
Library files cannot access params directly — all values must be passed as arguments.
"""

import requests
import base64


# Twilio API base URL
TWILIO_API_BASE = "https://api.twilio.com/2010-04-01"


def build_proxies(proxy_enable, proxy_ip, proxy_port, proxy_user="", proxy_pass=""):
    """Build a proxies dict for the requests library from Connect proxy settings."""
    if proxy_enable != "true":
        return None
    if proxy_user:
        proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
    else:
        proxy_url = f"http://{proxy_ip}:{proxy_port}"
    return {"http": proxy_url, "https": proxy_url}


def get_proxies_from_params(params):
    """Extract proxy settings from params and build a proxies dict."""
    return build_proxies(
        params.get("connect_proxy_enable", ""),
        params.get("connect_proxy_ip", ""),
        params.get("connect_proxy_port", ""),
        params.get("connect_proxy_username", ""),
        params.get("connect_proxy_password", "")
    )


def get_auth_header(account_sid, auth_token):
    """Build the Basic Auth header for Twilio API requests."""
    credentials = f"{account_sid}:{auth_token}"
    encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    return {"Authorization": f"Basic {encoded}"}


def twilio_request(method, endpoint, account_sid, auth_token, verify=True,
                   proxies=None, data=None):
    """
    Make an authenticated request to the Twilio API.

    Args:
        method: HTTP method ("GET", "POST", etc.)
        endpoint: API path after /2010-04-01 (e.g., "/Accounts/{sid}/Messages.json")
        account_sid: Twilio Account SID
        auth_token: Twilio Auth Token
        verify: SSL verification setting
        proxies: Proxy dict for requests
        data: Form data for POST requests

    Returns:
        requests.Response object

    Raises:
        requests.exceptions.RequestException on HTTP errors
    """
    url = f"{TWILIO_API_BASE}{endpoint}"
    headers = get_auth_header(account_sid, auth_token)

    if method.upper() == "GET":
        resp = requests.get(url, headers=headers, verify=verify, proxies=proxies)
    elif method.upper() == "POST":
        resp = requests.post(url, headers=headers, data=data, verify=verify,
                             proxies=proxies)
    else:
        resp = requests.request(method.upper(), url, headers=headers, data=data,
                                verify=verify, proxies=proxies)

    resp.raise_for_status()
    return resp


def send_sms(account_sid, auth_token, from_number, to_number, body,
             verify=True, proxies=None):
    """
    Send an SMS message via the Twilio Messages API.

    Args:
        account_sid: Twilio Account SID
        auth_token: Twilio Auth Token
        from_number: Twilio phone number to send from (E.164 format)
        to_number: Destination phone number (E.164 format)
        body: SMS message content
        verify: SSL verification setting
        proxies: Proxy dict for requests

    Returns:
        dict with the Twilio API response (message SID, status, etc.)
    """
    endpoint = f"/Accounts/{account_sid}/Messages.json"
    data = {
        "To": to_number,
        "From": from_number,
        "Body": body
    }
    resp = twilio_request("POST", endpoint, account_sid, auth_token,
                          verify=verify, proxies=proxies, data=data)
    return resp.json()


def test_connection(account_sid, auth_token, verify=True, proxies=None):
    """
    Test connectivity to Twilio by fetching account information.

    Args:
        account_sid: Twilio Account SID
        auth_token: Twilio Auth Token
        verify: SSL verification setting
        proxies: Proxy dict for requests

    Returns:
        dict with the account info from Twilio
    """
    endpoint = f"/Accounts/{account_sid}.json"
    resp = twilio_request("GET", endpoint, account_sid, auth_token,
                          verify=verify, proxies=proxies)
    return resp.json()
