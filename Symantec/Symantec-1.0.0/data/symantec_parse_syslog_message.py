"""
Copyright © 2021 Forescout Technologies, Inc.

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

import re
from datetime import datetime

response = {}
properties = {}
IOC_NAME = "name"
IOC_DATE = "date"
IOC_HASH = "hash"
IOC_HASH_TYPE = "hash_type"
IOC_SEVERITY = "severity"
IOC_FILE_SIZE = "file_size"
IOC_FILE_NAME = "file_name"
IOC_FILE_EXISTS = "file_exists"

ioc_property_mapping = {
    IOC_NAME : "Risk name",
    IOC_DATE : "Inserted",
    IOC_FILE_NAME : "Application name",
    IOC_HASH : "Application hash",
    IOC_HASH_TYPE : "Hash type",
    IOC_SEVERITY : "Risk level",
    IOC_FILE_SIZE : "File size (bytes)"
}
# As the risk log from Symantec do not include information about the severity of the risk,
# we set it a default value as "medium" for now
# this could be changed in the future
default_severity = "medium"


def remove_till_word(input, keyword):
    """
    search for a keyword from the text input and return the string from the index after the keyword to the end
    Eg: remove_till_word("feed_name='attackframework' report_id='565644'", "feed_name=")
    --> 'attackframework' report_id='565644'
    :param input: string, the text (source) to search from
    :param keyword: string, the search term/ keyword to look for
    :return: string, the string starting after the keyword to the end
    """
    result = ""
    index = input.find(keyword)
    if index < 0:
        return result
    index += len(keyword)
    result = input[index:]
    return result

def parse_syslog_message(ioc_raw):
    """
    :param ioc_raw: a string received from syslog describing the IOC
    :return: a dictionary mapping the fields listed in the ioc string to their corresponding value
    """
    #keywords: look for these keywords when parsing the ioc string
    keywords = ["IP Address", "Risk name", "Inserted", "Application hash", "Hash type", "Application name", "File size (bytes)"]
    infection_dict = {}
    #get the value string for each keyword
    for keyword in keywords:
        #first, get the beginning of the value (right after "<keyword>:") to end of the syslog string and store in rest variable
        rest = remove_till_word(ioc_raw, keyword + ":")
        if rest:
            # Next, if rest is not null/empty, continue to extract the value from rest
            # the value is the substring from the beginning of rest to the first comma
            # otherwise, the value pattern is non comma characters from the beginning
            # For example, for keyword "Hash type", we got rest = "SHA2,Company name: ,Application name: eicarcom2.zip,Application version: ,..."
            # Now we want to extract the value "SHA2" from rest. The matching string will start from the beginning of rest till a comma occurs
            pattern = re.compile("[^,]+")
            found = pattern.findall(rest)
            if found:
                #if the found value contains white spaces, remove them
                val = found[0].strip()
                #add keyword and its value into infection_dict
                infection_dict[keyword] = val
    return infection_dict

def convert_time_str_to_epoch_num(time_str):
    """
    Convert time from string type to epoch number
    Args: str
        time_str: time in string type
    Returns:
        epoch number in int type if the time string is in correct format else None
    """
    try:
        epoch = int(datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").timestamp())
        return epoch
    except ValueError as e:
        logging.debug (f"Failed to convert time '{time_str}' to epoch num: {e}")
        return None

def get_file_exists(syslog_message, file_name):
    if file_name:
        # find the file path from syslog message using pattern search
        # - the full filepath (path + file name) lies between two commas.
        # - the path part includes one or more combination of (non comma + backslash character \). For example: 'C:\' or 'C:\folder1\'
        # - the filename part includes non-comma and non-backslash characters.
        pattern= re.compile(",([^,]+\\\\)+([^\\\\,]+),")
        file_paths = pattern.findall(syslog_message)
        for file_path in file_paths:
            if file_path[1] == file_name:
                file_exists = {
                    "file_name": file_name,
                    "file_path": file_path[0]
                }
                return file_exists
    return None

def get_ioc_infos(infection_props):
    """
    :param infection_props: the dictionary with key-value of ioc information extracted from syslog message
    :return: ioc dictionary with correct IOC keys
    """
    ioc_info = {}
    for key in ioc_property_mapping:
        if ioc_property_mapping[key] in infection_props:
            val = infection_props[ioc_property_mapping[key]]
            if key == IOC_DATE:
                ioc_info[key] = convert_time_str_to_epoch_num(val)
            else:
                ioc_info[key] = val
    ioc_info[IOC_SEVERITY] = default_severity
    return ioc_info

# Check if we have syslog message or not before processing.
if params.get("connect_syslog_message"):
    syslog_message = params.get("connect_syslog_message")
    logging.debug(f"Syslog message is: {syslog_message}")
    try:
        infection_props = parse_syslog_message(syslog_message)
        ioc_info_dict = get_ioc_infos(infection_props)
        file_exists = get_file_exists(syslog_message, ioc_info_dict.get(IOC_FILE_NAME))
        if file_exists:
            ioc_info_dict[IOC_FILE_EXISTS] = file_exists

        #resolve "connect_symantec_infection_info" property
        ip = infection_props.get("IP Address")
        infection_info = {}
        property_subfields = [IOC_NAME, IOC_DATE, IOC_FILE_NAME, IOC_HASH, IOC_HASH_TYPE, IOC_SEVERITY]
        for subfield in property_subfields:
            if subfield in ioc_info_dict:
                infection_info[subfield] = ioc_info_dict[subfield]
        properties["connect_symantec_infection_info"] = infection_info
        logging.debug(f"properties: {properties}")
        if ip:
            response["ip"] = ip
        response["properties"] = properties
        response["ioc"] = ioc_info_dict
        logging.debug("response: {}".format(response))
    except Exception as e:
        exp_error_msg =  f"Failed to process syslog message. Exception: {e}."
        response["error"] = exp_error_msg
        logging.debug(exp_error_msg)
else:
    error_msg = "No syslog message is passed."
    response["error"] = error_msg
    logging.debug(error_msg)

