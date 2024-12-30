import logging
import requests
import json

# Values from system.conf
server = params.get("connect_infoblox_server")
port = params.get("connect_infoblox_port")
username = params.get("connect_infoblox_user")
password = params.get("connect_infoblox_password")
normalise = params.get("connect_infoblox_normalisemac")
inboundapi = params.get("connect_infoblox_inboundapi")
token = params.get("connect_authorization_token")

# Generic values
response = {}
properties = {}
conflict = False
fingerprint = None

if inboundapi == "true":

    # Check IP retrieved
    if "ip" in params:
        ip = params.get("ip")
        logging.debug("***Infoblox*** Retrieved IP Address for API query [{}]".format(ip))
    else:
        response["error"] = "IP Address not Found"
        logging.debug("***Infoblox*** {}".format(response["error"]))
        exit()

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

    if token:
        headers = {'Cookie': token}

        # Resolve IP URL
        ip_url = "https://{}:{}/wapi/v2.12.3/ipv4address?ip_address={}&_return_fields=fingerprint,names,is_conflict,mac_address".format(server,port,ip)

        # Resolve IP Address in Infoblox
        try:
            resp = requests.get(ip_url,headers=headers, verify=ssl_verify, proxies=proxies)
            resp_code = resp.status_code
            json_resp = json.loads(resp.content)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logging.debug("***Infoblox*** API Client Query returned HTTP error:{}".format(errh))
        except requests.exceptions.ConnectionError as errc:
            logging.debug("***Infoblox*** API Client Query returned Connecting error:{}".format(errc))
        except requests.exceptions.Timeout as errt:
            logging.debug("***Infoblox*** API Client Query returned Timeout error:{}".format(errt))
        except requests.exceptions.RequestException as err:
            logging.debug("***Infoblox*** API Client Query returned error:{}".format(err))

        if resp_code == 200:
            logging.debug("***Infoblox*** Response Received for IP Query [{}]".format(json_resp))

            for entry in json_resp:
                logging.debug("***Infoblox*** Processing data in [{}]".format(entry))
                for key, value in entry.items():
                    if key == "is_conflict":
                        if value == False:
                            properties["connect_infoblox_conflict"] = "No Conflict Detected"
                        elif value == True:
                            properties["connect_infoblox_conflict"] = "Conflict Detected"
                            conflict = True
                            break
                    elif key == "mac_address":
                        if normalise == True:
                            normalised_mac = value.replace(":", "").lower()
                            properties["connect_infoblox_macaddress"] = normalised_mac
                        else:
                            properties["connect_infoblox_macaddress"] = value
                    elif key == "fingerprint":
                        if value == "nomatch":
                            pass
                        else:
                            fingerprint = value
                    elif key =="names":
                        names_list = []
                        for name in value:
                            names_list.append(name)
                        properties["connect_infoblox_devicename"] = names_list
                properties["connect_infoblox_fingerprint"] = fingerprint

            logging.debug("***Infoblox*** IP Query complete, properties learnt: [{}]".format(properties))
        else:
            response["error"] = "Did not get a 200 code from API query. Error: {} Please check Infoblox configuration.".format(resp_code)
            logging.debug("***Infoblox*** {}".format(response["error"]))

        lease_url = "https://{}:{}/wapi/v2.12.3/lease?address={}&_return_fields=client_hostname".format(server,port,ip)

        try:
            lease_resp = requests.get(lease_url,headers=headers, verify=ssl_verify, proxies=proxies)
            lease_resp_code = lease_resp.status_code
            json_lease_resp = json.loads(lease_resp.content)
            lease_resp.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logging.debug("***Infoblox*** API Client Lease Query returned HTTP error:{}".format(errh))
        except requests.exceptions.ConnectionError as errc:
            logging.debug("***Infoblox*** API Client Lease Query returned Connecting error:{}".format(errc))
        except requests.exceptions.Timeout as errt:
            logging.debug("***Infoblox*** API Client Lease Query returned Timeout error:{}".format(errt))
        except requests.exceptions.RequestException as err:
            logging.debug("***Infoblox*** API Client Lease Query returned error:{}".format(err))

        if lease_resp_code == 200:
            logging.debug("***Infoblox*** Response Received for Lease Query [{}]".format(json_lease_resp))
            for entry in json_lease_resp:
                logging.debug("***Infoblox*** Processing data in [{}]".format(entry))
            for key, value in entry.items():
                if key == "client_hostname":
                    properties["connect_infoblox_clienthostname"] = entry
                else:
                    properties["connect_infoblox_clienthostname"] = None
            logging.debug("***Infoblox*** Lease Query complete, properties learnt: [{}]".format(properties["connect_infoblox_clienthostname"]))
        else:
            properties["connect_infoblox_clienthostname"] = None
            logging.debug("***Infoblox*** Did not get a 200 code from API query. Error: {} Please check Infoblox configuration.".format(resp_code))

        if conflict is True:
            logging.debug("***Infoblox*** IP Conflict detected within Infoblox, no further properties will be resolved.")
        elif fingerprint is None:
            logging.debug("***Infoblox*** No fingerprint found, no further properties will be resolved.")
            properties["connect_infoblox_deviceclass"] = None
            properties["connect_infoblox_optionsequence"] = []
        else:
            # Resolve Fingerprint URL
            fingerprint_url = "https://{}:{}/wapi/v2.12.3/fingerprint?name={}&_return_fields=device_class,option_sequence".format(server,port,fingerprint)

            try:
                resp = requests.get(fingerprint_url,headers=headers, verify=ssl_verify, proxies=proxies)
                resp_code = resp.status_code
                json_resp = json.loads(resp.content)
                resp.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                logging.debug("***Infoblox*** API Client Query returned HTTP error:{}".format(errh))
            except requests.exceptions.ConnectionError as errc:
                logging.debug("***Infoblox*** API Client Query returned Connecting error:{}".format(errc))
            except requests.exceptions.Timeout as errt:
                logging.debug("***Infoblox*** API Client Query returned Timeout error:{}".format(errt))
            except requests.exceptions.RequestException as err:
                logging.debug("***Infoblox*** API Client Query returned error:{}".format(err))

            if resp_code == 200:
                logging.debug("***Infoblox*** Response Received for Fingerprint Query [{}]".format(json_resp))

                for entry in json_resp:
                    logging.debug("***Infoblox*** Processing data in [{}]".format(entry))
                    for key, value in entry.items():
                        if key == 'device_class':
                            properties["connect_infoblox_deviceclass"] = value
                        elif key == 'option_sequence':
                            seq_list = []
                            for seq in value:
                                seq_list.append(seq)
                            properties["connect_infoblox_optionsequence"] = seq_list
                logging.debug("***Infoblox*** Fingerprint Query complete, properties learnt: [{}]".format(properties))
            else:
                response["error"] = "Did not get a 200 code from API query. Error: {} Please check Infoblox configuration.".format(resp_code)
                logging.debug("***Infoblox*** {}".format(response["error"]))

        response["properties"] = properties
        logging.debug("***Infoblox*** Returning response object to infrastructure. response=[{}]".format(response))

    else:
        response["error"] = "No token available for authorization"
        logging.debug("***Infoblox*** {}".format(response["error"])) 

else:
    response["error"] = "Inbound API is disabled, resolve query cannot be completed."
    logging.debug("***Infoblox*** {}".format(response["error"]))