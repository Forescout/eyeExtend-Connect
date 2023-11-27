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
import csv
import requests

url = params.get("connect_iocimport_url")
match_col = params.get("connect_iocimport_match_col")
match_value = params.get("connect_iocimport_match_val")
name_col = params.get("connect_iocimport_name_col")
os_col = params.get("connect_iocimport_os_col")
file_col = params.get("connect_iocimport_file_col")
md5_col = params.get("connect_iocimport_md5_col")
sha1_col = params.get("connect_iocimport_sha1_col")
sha256_col = params.get("connect_iocimport_sha256_col")
cnc_col = params.get("connect_iocimport_cnc_col")
sev_col = params.get("connect_iocimport_sev_col")
critical_score = params.get("connect_iocimport_critical_score")
high_score = params.get("connect_iocimport_high_score")
medium_score = params.get("connect_iocimport_medium_score")

extract_col = []
hash_col = []

for x in name_col, os_col, file_col, md5_col, sha1_col, sha256_col, cnc_col, sev_col:
    if x is not "":
        extract_col.append(x)

for x in md5_col, sha1_col, sha256_col:
    if x is not "":
        hash_col.append(x)

response = {}
ioc_infos = []

ioc_property_mapping = {
    name_col : "name",
    os_col : "platform",
    file_col : "file_name",
    md5_col : "md5",
    sha1_col : "sha1",
    sha256_col : "sha256",
    cnc_col: "cnc",
    sev_col : "severity"
}

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

logging.debug("***IOC Import*** Columns to extract: [ {} ]".format(extract_col))

def download_csv(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, verify=False, headers=headers, proxies=proxies)
        if response.status_code == 200:
            return response.content
        else:
            logging.debug("***IOC Import*** Failed to download the CSV. Status code: {}".format(response.status_code))
            return None
    except Exception as e:
        logging.debug("***IOC Import*** Error while downloading the file: {}".format(e))
        return None

def get_column_indices(header_row, columns_to_extract):
    indices = []
    for column in columns_to_extract:
        if column in header_row:
            indices.append(header_row.index(column))
    return indices

def generate_generic_name(hash_column_name, hash_value):
    logging.debug("***IOC Import*** Generating Name using [ {} ] and [ {} ]".format(hash_column_name, hash_value))
    generated_name = "IOC {} starting {}".format(hash_column_name, hash_value[:4])
    logging.debug("***IOC Import*** Returning name: {}".format(generated_name))
    return generated_name
    

def evaluate_severity(severity_value):
    severity_thresholds = [critical_score, high_score, medium_score]
    severity_strings = ["Critical", "High", "Medium"]

    if severity_value is None:
        logging.debug("***IOC Import*** No severity defined, setting default")
        return "Medium"

    for i, threshold in enumerate(severity_thresholds):
        logging.debug("***IOC Import*** Evaluating Severity")
        if int(severity_value) >= int(threshold):
            logging.debug("***IOC Import*** Evaluating Severity: Value {} Threshold {}".format(severity_value, threshold))
            return severity_strings[i]

    return "Low"

def match_os(os_value, predefined_os_list):
    for predefined_os in predefined_os_list:
        if predefined_os in os_value:
            if "Windows" in predefined_os:
                return f"Microsoft {predefined_os}"
            return predefined_os
    return "All"

def split_by_hashes(data_hold, hash_column):
    split_data = []

    logging.debug("***IOC Import*** Starting to split data [ {} ] by hashes [ {} ]".format(data_hold, hash_column))

    for hash_key in hash_column:
        new_data = {}
        logging.debug("***IOC Import*** Checking for Hash: {}".format(hash_key))
        for data_key, data_value in data_hold.items():
            if data_key in hash_column:
                logging.debug("***IOC Import*** Checking for Data: {}".format(data_key))
                if data_key == hash_key:
                    new_data["hash_type"] = data_key
                    new_data["hash"] = data_value
            else:
                new_data[data_key] = data_value

        if name_col == "" or (new_data.get("name") == ""):
            logging.debug("***IOC Import*** Name not defined, using file name instead")
            new_data["name"] = data_hold["file_name"]
            logging.debug("***IOC Import*** Name added to data set: [ {} ]".format(new_data["name"]))
            
        logging.debug("***IOC Import*** New data lines: {}".format(new_data))
        split_data.append(new_data)

    logging.debug("***IOC Import*** Returning data: {}".format(split_data))
    return split_data

def extract_columns_from_matching_value(csv_content, match_column_name, match_values, columns_to_extract):
    ioc_infos = []
    reader = csv.reader(csv_content.decode('utf-8').splitlines())
    header = next(reader)

    if match_column_name is not None:
        match_column_index = header.index(match_column_name)
    else:
        match_column_index = None

    columns_to_extract_indices = get_column_indices(header, columns_to_extract)

    for row in reader:
        logging.debug("***IOC Import*** Working on Row: {}".format(row))
        if match_column_index is None or row[match_column_index] in match_values:
            data_hold = {}
            for i, index in enumerate(columns_to_extract_indices):
                key_name = ioc_property_mapping.get(columns_to_extract[i])
                logging.debug("***IOC Import*** Key Names: {}".format(key_name))
                if not key_name:
                    logging.debug("***IOC Import*** Property mapping missing for column: {}".format(columns_to_extract[i]))
                    raise ValueError("Property mapping missing for column:", columns_to_extract[i])
                data_hold[key_name] = row[index]
            
            logging.debug("***IOC Import*** Main key names: {}".format(data_hold))

            severity_value = data_hold.get("severity")
            if "severity" not in ioc_property_mapping.values():
                logging.debug("***IOC Import*** Severity not defined")
                severity_value = None

            data_hold["severity"] = evaluate_severity(severity_value)
            logging.debug("***IOC Import*** Severity defined: {}".format(data_hold["severity"]))

            if "platform" in ioc_property_mapping.values():
                os_value = data_hold.get("platform")
                predefined_os_list = ["Linux", "Windows 7", "Windows 8", "Windows Vista", "Windows XP", "Windows 10", "macOS"]
                data_hold["platform"] = match_os(os_value, predefined_os_list)
                logging.debug("***IOC Import*** Platform defined: {}".format(data_hold["platform"]))

            ioc_info = {}

            if len(hash_col) > 1:
                logging.debug("***IOC Import*** Splitting Data...")
                split_data = split_by_hashes(data_hold, hash_col)
                for x in split_data:
                    ioc_info = x
                    ioc_infos.append(ioc_info)
            elif name_col == "" or (data_hold.get("name") == ""):
                logging.debug("***IOC Import*** Name not defined, using file name instead")
                data_hold["name"] = data_hold["file_name"]
                logging.debug("***IOC Import*** Name added to data set: [ {} ]".format(data_hold["name"]))
                
                ioc_info = data_hold
                ioc_infos.append(ioc_info)

    logging.debug("***IOC Import*** Returning IOC Info: {}".format(ioc_infos))
    return ioc_infos

csv_content = download_csv(url)
if csv_content:
    match_column_name = match_col
    match_values = match_value

    columns_to_extract = extract_col

    ioc_infos = extract_columns_from_matching_value(csv_content, match_column_name, match_values, columns_to_extract)

    if not ioc_infos:
        logging.debug("***IOC Import*** No data found for the specified criteria.")
    else:
        logging.debug("***IOC Import*** Returning to IOC Scanner: [ {} ]".format(ioc_infos))
        response["ioc"] = ioc_infos