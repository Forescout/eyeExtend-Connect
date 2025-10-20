import logging
import requests
from requests.exceptions import SSLError, RequestException

logging.basicConfig(level=logging.INFO)
logging.info("Sepio Test Connection Script Started")

base_url = params['connect_sepio_url'].strip()

if not base_url.startswith('http://') and not base_url.startswith('https://'):
    base_url = 'https://' + base_url

if not base_url.endswith('/prime/webui/Auth/LocalLogin'):
     SEPIO_API_AUTH_URL = f"{base_url.rstrip('/')}/prime/webui/Auth/LocalLogin"
else:
    SEPIO_API_AUTH_URL = base_url

SEPIO_API_USERNAME = params['connect_sepio_username']
SEPIO_API_PASSWORD = params['connect_sepio_password']

response = {}
logging.info(f"Sepio URL: {SEPIO_API_AUTH_URL}")

def fetch_sepio_token():
    headers = {'Content-Type': 'application/json'}
    body = {
        "username": SEPIO_API_USERNAME,
        "password": SEPIO_API_PASSWORD
    }

    try:

        logging.info(f'SSL verification is set to: {ssl_verify}')

        res = requests.post(SEPIO_API_AUTH_URL, headers=headers, json=body, verify=ssl_verify)
        res.raise_for_status()  # Raise an exception for 4xx/5xx status codes

        # Check for a successful response
        if res.status_code == 200:
            response_data = res.json()
            token = response_data.get('token')

            if token:
                logging.info("Token received successfully")
                response["succeeded"] = True
                response["result_msg"] = "Successfully connected."
            else:
                logging.error("Authentication failed")
                response["succeeded"] = False
                response["result_msg"] = "Authentication failed."
        else:
            logging.error(f"Error: {res.status_code}. Could not connect to the Sepio server.")
            response["succeeded"] = False
            response["result_msg"] = f"Error: {res.status_code}. Could not connect to the Sepio server."
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        response["succeeded"] = False
        response["result_msg"] = f"HTTP error occurred: {http_err}"
    except SSLError as ssl_err:
        logging.error(f"SSL error occurred: {ssl_err}")
        response["succeeded"] = False
        response["result_msg"] = f"SSL issue occurred: {ssl_err}"
    except RequestException as req_err:
        logging.error(f"Request error occurred: {req_err}")
        response["succeeded"] = False
        response["result_msg"] = f"Request error occurred: {req_err}"
    except Exception as err:
        logging.error(f"An unexpected error occurred: {err}")
        response["succeeded"] = False
        response["result_msg"] = "An unexpected error occurred."

# Run the token fetch function
fetch_sepio_token()

# Output the final result
if response["succeeded"]:
    logging.info(response["result_msg"])
else:
    logging.error(response["result_msg"])
