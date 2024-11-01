import logging
import requests
import json

# Values from system.conf
server = params.get("connect_infoblox_server")
port = params.get("connect_infoblox_port")
username = params.get("connect_infoblox_user")
password = params.get("connect_infoblox_password")

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

logging.debug("***Infoblox*** Test URL: {} Username: {} Password: {}".format(url,username,password))

# Connectivity Test
try:
    resp = requests.get(url,headers=headers, verify=ssl_verify, proxies=proxies, auth=(username,password))
    
    logging.debug("***Infoblox*** Response: [{}]".format(resp))

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
    count = len(json_resp)
    response["succeeded"] = True
    response["result_msg"] = "Connection successful, {} default network discovered in Infoblox".format(count)
    logging.debug("***Infoblox*** {}".format(response["result_msg"]))
elif resp_code:
    response["succeeded"] = False
    response["result_msg"] = "Did not get a 200 code from API query. Error: {} Please check Infoblox configuration.".format(resp_code)
    logging.debug("***Infoblox*** {}".format(response["result_msg"]))
else:
    response["succeeded"] = False
    response["result_msg"] = "Did not get a 200 code from API query. Error: {} Please check Infoblox configuration.".format(error)
    logging.debug("***Infoblox*** {}".format(response["result_msg"]))