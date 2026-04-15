"""
Oracle KVM Connect App - Authorization Script
Obtains an OAuth2 SSO token from the OLVM engine.
"""

import requests

# params and response are pre-injected by the Connect framework

base_url = params.get("connect_oraclekvm_url", "").rstrip("/")
username = params.get("connect_oraclekvm_username", "")
domain = params.get("connect_oraclekvm_domain", "internal")
password = params.get("connect_oraclekvm_password", "")

proxies = oraclekvm_lib.get_proxies_from_params(params)

token_url = f"{base_url}/ovirt-engine/sso/oauth/token"

response = {}

try:
    payload = {
        "grant_type": "password",
        "scope": "ovirt-app-api",
        "username": f"{username}@{domain}",
        "password": password,
    }

    resp = requests.post(
        token_url,
        data=payload,
        headers={"Accept": "application/json"},
        verify=ssl_verify,
        proxies=proxies,
    )
    resp.raise_for_status()
    token_data = resp.json()

    access_token = token_data.get("access_token", "")
    if access_token:
        response["token"] = access_token
        logging.info("Oracle KVM authorization: token obtained successfully")
    else:
        response["token"] = ""
        response["error"] = "No access_token in SSO response"
        logging.error("Oracle KVM authorization: no access_token returned")

except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response is not None else "unknown"
    if status_code == 401:
        response["error"] = "Authorization failed: invalid credentials"
    else:
        response["error"] = f"SSO token request failed with HTTP {status_code}"
    logging.error(f"Oracle KVM authorization HTTP error: {status_code}")
except requests.exceptions.ConnectionError:
    response["error"] = f"Could not connect to OLVM SSO endpoint at {token_url}"
    logging.error("Oracle KVM authorization: connection error")
except Exception as e:
    response["error"] = f"Authorization error: {str(e)}"
    logging.error(f"Oracle KVM authorization error: {str(e)}")
