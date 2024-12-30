import logging
import requests
import json
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

# Test URL
url = "https://{}:{}/wapi/v2.12.3/networkview?is_default=true".format(server,port)

headers = {}

error = ""

if inboundapi == "true":

    logging.debug("***Infoblox*** Test URL: {} Username: {}".format(url,username))

    # Connectivity Test
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
        json_resp = json.loads(resp.content)
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
        if token:
            headers = {'Cookie': token}
            
            logging.debug("***Infoblox*** Set Header: [ {} ]".format(headers))
            
            resp2 = requests.get(url,headers=headers, verify=ssl_verify, proxies=proxies)
            resp2_code = resp2.status_code

            if resp2_code == 200:
                response["succeeded"] = True
                response["result_msg"] = "Authentication to Infoblox Grid Master with token successful"
                logging.debug("***Infoblox*** {}".format(response["result_msg"]))
            else:
                response["succeeded"] = False
                response["result_msg"] = "Did not get a 200 code from API query. Error: {} Please check configuration.".format(resp_code)
                logging.debug("***Infoblox*** {}".format(response["result_msg"]))
    elif resp_code:
        response["succeeded"] = False
        response["result_msg"] = "Did not get a 200 code from API query. Error: {} Please check Infoblox configuration.".format(resp_code)
        logging.debug("***Infoblox*** {}".format(response["result_msg"]))
    else:
        response["succeeded"] = False
        response["result_msg"] = "Did not get a 200 code from API query. Error: {} Please check Infoblox configuration.".format(error)
        logging.debug("***Infoblox*** {}".format(response["result_msg"]))
else:
    response["succeeded"] = False
    response["result_msg"] = "Using the Infoblox Inbound API is disabled. Test cannot be completed, enable Inbound API and test again. Alternatively, ensure Syslog source has been defined to work with Syslog only."
    logging.debug("***Infoblox*** {}".format(response["result_msg"]))