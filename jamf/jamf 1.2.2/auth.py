import requests
import re
import logging

url = params["connect_jamf_url"]
username = params["connect_jamf_username"]
password = params["connect_jamf_password"]

def get_jamf_token(username: str, password: str, url: str) -> str:
    try:
        response = requests.post(f"{url}/api/v1/auth/token", auth=(username, password), verify=False)
        response.raise_for_status()
        if response.json().get('token'):
            return response.json().get('token')
        else:
            raise ValueError("Token not found in the response")

    except requests.exceptions.RequestException as e:
        logging.error(f"JAMF FAILED TO GET TOKEN: {e}")
        return None
    except Exception as e:
        logging.error(f"JAMF FAILED TO GET TOKEN: {e}")
        return None

response = {}
token = get_jamf_token(username, password, url)

if token is not None:
    response['token'] = token
    response['succeeded'] = True
else:
    response['token']= ""
    response['succeeded'] = False


