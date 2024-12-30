import logging
import requests
import re

# Values from system.conf
server = params.get("connect_infoblox_server")
port = params.get("connect_infoblox_port")
username = params.get("connect_infoblox_user")
password = params.get("connect_infoblox_password")
inboundapi = params.get("connect_infoblox_inboundapi")

# Generic values
response = {}

# Requests Proxy
is_proxy_enabled = params.get("connect_proxy_enable")
if is_proxy_enabled == "true":
    proxy_ip = params.get("connect_proxy_ip")
    proxy_port = params.get("connect_proxy_port")
    proxy_user = params.get("connect_proxy_username")
    proxy_pass = params.get("connect_proxy_password")
    if not proxy_user:
        proxy_url = f"https://{proxy_ip}:{proxy_port}"
        proxies = {"https" : proxy_url}
        logging.debug ("Proxy enabled / no user")
    else:
        proxy_url = f"https://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
        proxies = {"https" : proxy_url}
        logging.debug ("Proxy enabled / user")
else:
    logging.debug ("Proxy disabled")
    proxies = None

# Connection URL
url = "https://{}:{}/wapi/v2.12.3/networkview?is_default=true".format(server,port)

headers = {}

error = ""

if inboundapi == "true":

    logging.debug("***Infoblox*** Querying URL: {} Username: {}".format(url,username))

    # Auth and retrieve cookie for subsequent authorization
    try:
        resp = requests.get(url,headers=headers, verify=ssl_verify, proxies=proxies, auth=(username,password))
        
        logging.debug("***Infoblox*** Response: [{}]".format(resp))

        resp_auth_headers = resp.headers["set-cookie"]

        logging.debug("***Infoblox*** Headers: [{}]".format(resp_auth_headers))

        match = re.search(r'ibapauth=([^;]+);', resp_auth_headers)
        if match:
            ibapauth_value = match.group(1)
            logging.debug("***Infoblox*** Retrieved authentication cookie: {}".format(ibapauth_value))

            token = "ibapauth={}".format(ibapauth_value)
        else:
            logging.debug("***Infoblox*** No authentication cookie found")

        resp_code = resp.status_code
        resp.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logging.debug("***Infoblox*** API Client Query returned HTTP error:{}".format(errh))
        error = errh
    except requests.exceptions.ConnectionError as errc:
        logging.debug("***Infoblox*** API Client Query returned Connecting error:{}".format(errc))
        error = errc
    except requests.exceptions.Timeout as errt:
        logging.debug("***Infoblox*** API Client Query returned Timeout error:{}".format(errt))
        error = errt
    except requests.exceptions.RequestException as err:
        logging.debug("***Infoblox*** API Client Query returned error:{}".format(err))
        error = err

    if resp_code == 200:
        logging.debug("***Infoblox*** Connection to Infoblox Grid Master successful. Verifying token.")

        if token:
            logging.debug("***Infoblox*** Token retrieved.")
            response["token"] = token
        else:
            response["error"] = "Failed to obtain token"
            logging.debug("***Infoblox*** {}".format(response["error"]))

    elif resp_code:
        response["error"] = "Did not get a 200 code from API query. Error: {} Please check Infoblox configuration.".format(resp_code)
        logging.debug("***Infoblox*** {}".format(response["error"]))
    else:
        response["error"] = "Did not get a 200 code from API query. Error: {} Please check Infoblox configuration.".format(error)
        logging.debug("***Infoblox*** {}".format(response["error"]))
else:
    response["error"] = "Using the Infoblox Inbound API is disabled, no authorization is required."
    logging.debug("***Infoblox*** {}".format(response["error"]))