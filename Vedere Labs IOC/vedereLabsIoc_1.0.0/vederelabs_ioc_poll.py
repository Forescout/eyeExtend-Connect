"""
Copyright © 2023 Forescout Technologies, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import re
from datetime import datetime

api_details ={}

api_details["subscriber_api_key"] = params.get("connect_vederelabsioc_subscriber_api_key")
api_details["lookback"] = params.get("connect_vederelabsioc_lookback_days")
api_details["enable_ipv4_ioc"] = params.get("connect_vederelabsioc_enable_ipv4_ioc")
api_details["enable_dns_ioc"] = params.get("connect_vederelabsioc_enable_dns_ioc")
api_details["enable_hash_ioc"] = params.get("connect_vederelabsioc_enable_hash_ioc")
api_details["minimum_confidence"] = params.get("connect_vederelabsioc_minimum_confidence")
api_details["ioc_severity"] = params.get("connect_vederelabsioc_ioc_severity")
api_details["ssl_verify"] = ssl_verify

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

api_details["proxies"] = proxies

phases = {}
phases["medium"] = ["reconnaissance","resource-development","initial-access"]
phases["high"] = ["execution","persistence","privilege-escalation","defense-evasion","credential-access","discovery","lateral-movement","collection","command-and-control"]
phases["critical"] = ["exfiltration","impact"]

def get_ioc_infos():
    ioc_response = []
    try:
        logging.debug("***Vedere Labs*** Attempting to retrieve IOC data from the Vedere Labs API with the following parameters: API Key={}".format(api_details["subscriber_api_key"]))

        code, vl_response = VEDERE_API.VL_RETRIEVE_INDICATORS(api_details)
        logging.debug("***Vedere Labs*** Response code from Vedere Labs API was {}".format(code))
        
        if code == 200:
            logging.debug("***Vedere Labs*** Parsing IOC entries from response")
            ioc_payload = vl_response
            logging.debug("***Vedere Labs*** Successfully loaded response into object for processing IOC Objects: {}".format(len(ioc_payload["objects"])))
            for entry in ioc_payload["objects"]:
                if entry["type"] == "indicator" and entry["confidence"] >= int(api_details["minimum_confidence"]):
                    logging.debug("***Vedere Labs*** Parsing entry: {}".format(entry))
                    ioc_entry = {}
                    ioc_entry["name"] = entry["id"]
                    ## Handle CNC IPs
                    if api_details["enable_ipv4_ioc"]:
                        if "ipv4-addr:value" in entry["pattern"]:
                            cnc_ips = re.search(r"[0-9]+(?:\.[0-9]+){3}", entry["pattern"])
                            ioc_entry["cnc"] = cnc_ips.group(0)
                            ioc_entry["hash"] = entry["pattern"]
                            ioc_entry["hash_type"] = "none"
                    ## Handle DNS (Domain Names & URLs)
                    if api_details["enable_dns_ioc"]:
                        if "url:value" in entry["pattern"]:
                            dns_entry = re.search(r"url:value\s*=\s*'([^']*)'", entry["pattern"])
                            ioc_entry["dns"] = dns_entry.group(1)
                            ioc_entry["hash"] = entry["pattern"]
                            ioc_entry["hash_type"] = "none"
                        elif "domain-name:value" in entry["pattern"]:
                            dns_entry = re.search(r"domain-name:value\s*=\s*'([^']*)'", entry["pattern"])
                            ioc_entry["dns"] = dns_entry.group(1)
                            ioc_entry["hash"] = entry["pattern"]
                            ioc_entry["hash_type"] = "none"
                    ## Handle DNS (Domain Names & URLs)
                    if api_details["enable_hash_ioc"]:
                        if "file:hashes." in entry["pattern"]:
                            hash_ioc = re.search(r"\[file:hashes\.'(.*?)' = '([^']*)'\]", entry["pattern"])
                            if hash_ioc.group(1) == "SHA-256":
                                ioc_entry["hash_type"] = "sha256"
                            elif hash_ioc.group(1) == "SHA-1":
                                ioc_entry["hash_type"] = "sha1"
                            elif hash_ioc.group(1) == "MD5":
                                ioc_entry["hash_type"] = "md5"
                            else:
                                ioc_entry["hash_type"] = "none"
                            ioc_entry["hash"] = hash_ioc.group(2)
                    ioc_entry["file_name"] = entry["description"]
                    if entry["valid_from"]:
                        try:
                            date = datetime.strptime(entry["valid_from"], "%Y-%m-%dT%H:%M:%S.%fZ")
                        except ValueError:
                            date = datetime.strptime(entry["valid_from"], "%Y-%m-%dT%H:%M:%SZ")
                        date_epoch = int(date.timestamp() * 1000)
                        ioc_entry["date"] = date_epoch
                    if "kill_chain_phases" in entry:
                        for phase_entry in entry["kill_chain_phases"]:
                            phase_name = phase_entry.get("phase_name")
                            if phase_name in phases["critical"]:
                                ioc_entry["severity"] = "critical"
                            elif phase_name in phases["high"]:
                                ioc_entry["severity"] = "high"
                            elif phase_name in phases["medium"]:
                                ioc_entry["severity"] = "medium"
                            else:
                                ioc_entry["severity"] = api_details["ioc_severity"]
                    else:
                        ioc_entry["severity"] = api_details["ioc_severity"]
                    ioc_response.append(ioc_entry)
                    logging.debug("***Vedere Labs*** Returning: {}".format(ioc_entry))
        if code == 404:
            if vl_response == "No valid indicators":
                response["error"] = "No valid indicators"
                logging.debug("***Vedere Labs*** {}".format(response["error"]))
            else:
                vl_response.raise_for_status()
    except Exception as e:
        response["error"] = f"Could not resolve properties: {e}."
        logging.debug("***Vedere Labs*** Failure {}".format(response["error"]))
    return ioc_response

response = {}
logging.debug("***Vedere Labs*** Vedere Labs IOC polling.")
if api_details["subscriber_api_key"]:
    try:
        ioc_infos = get_ioc_infos()
        logging.debug("***Vedere Labs*** Retrieved ioc info: {}".format(ioc_infos))
        if ioc_infos:
            logging.debug("***Vedere Labs*** Preparing IOCs for IOC Scanner Load")
            response["ioc"] = ioc_infos
            response["result_msg"] = "Subscribed to {} IOCs".format(str(len(ioc_infos)))
            logging.debug("***Vedere Labs*** Finished IOC Poll - {}".format(response["result_msg"]))
        else:
            response["error"] = "No IOC data available"
            logging.debug("***Vedere Labs*** {}".format(response["error"]))
    except Exception as e:
        response["error"] = "Could not retrieve IOC data. Error: {}".format(str(e))
        logging.debug("***Vedere Labs*** {}".format(response["error"]))
else:
    response["error"] = "No API Key Defined for Polling"
    logging.debug("***Vedere Labs*** {}".format(response["error"]))