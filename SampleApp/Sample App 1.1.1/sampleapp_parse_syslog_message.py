"""
This sample script shows how a Connect App can parse Syslog message into correct IOC data format using regex
then send IOC data to IOC Scanner.
The Syslog message in this example replicates the Syslog message received by Carbon Black.
Different Syslog server will send Syslog message in different format, the app writer should
customize their codes to handle and process the syslog message respectively.
To check and get any available syslog, use: params.get("connect_syslog_message")
If available, params["connect_syslog_message"] will be in String format
Sample Syslog message used in this script (added line separators for easy reading):
-------
Syslog message: <28>Dec 10 09:51:22 2020-12-10 09: 51:22 [2783] <warning> reason=feed.storage.hit
type=event process_guid=00000002-0000-069c-01d6-cf1b37991278 segment_id=1607622682337 host='mliu-2k12'
comms_ip='10.100.6.111' interface_ip='10.100.6.111' sensor_id=2 feed_id=22 feed_name='attackframework'
report_id='565644' report_title='(Unknown)' ioc_type='query' ioc_value='{"index_type":"events",
"search_query":"cb.urlver=1&q=%28%28cmdline%3A.ps%2A%20OR%20cmdline%3A.bat%20OR%20cmdline%3A.py%20OR
%20cmdline%3A.cpl%20OR%20cmdline%3A.cmd%20OR%20cmdline%3A.com%20OR%20cmdline%3A.lnk%20OR%20cmdline%
3A.reg%20OR%20cmdline%3Ascr%20OR%20cmdline%3A.vb%2A%20OR%20cmdline%3A.ws%2A%20OR%20cmdline%3A.xsl%
29%20-process_name%3Acrashpad_handler%20OR%20-process_name%3AChrome.exe%29"}' timestamp='1607622682.338'
start_time='2020-12-10T17:38:05.785Z' group='default group' process_md5='2e8d4a6fedf90e265d2370a543b4fd2a'
process_sha256='4747d091f230bf409af6a42c32cca30d845541d2c3200bb275f0fa179bd5e082' process_name='cscript.exe'
process_path='c:\windows\system32\cscript.exe' last_update='2020-12-10T17:38:05.972Z' alliance_score_attackframework='1'
alliance_link_attackframework='https://attack.mitre.org/techniques/T1059/' alliance_data_attackframework='565644'
alliance_updated_attackframework='2020-09-28T20:22:00.000Z'
-------
The response dictionary must contain a dictionary or a list of dictionary called "ioc" so that IOC data can be sent to IOC Scanner
"""

import re
import hashlib
import random

IOC_NAME = "name"
IOC_HASH = "hash"
IOC_HASH_TYPE = "hash_type"
IOC_FILE_NAME = "file_name"
IOC_FILE_SIZE = "file_size"
IOC_PLATFORM = "platform"
IOC_DATE = "date"
IOC_SEVERITY = "severity"
IOC_FILE_EXISTS = "file_exists"
IOC_FILE_PATH = "file_path"
IOC_CNC = "cnc"
IOC_DNS = "dns"
IOC_MUTEX = "mutex"
IOC_SERVICE = "service"
IOC_PROCESS = "process"
IOC_PROCESS_NAME = "process_name"
IOC_PROCESS_HASH = "process_hash"
IOC_PROCESS_HASH_TYPE = "process_hash_type"
IOC_REGISTRY = "registry"
IOC_REGISTRY_ELEMENT = "registry_element"
IOC_REGISTRY_DATA = "registry_data"

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
    if index<0:
        return result
    index+=len(keyword)
    result = input[index:]
    return result

def parse_syslog_message(ioc_raw):
    """
    At this stage, the input consists of key=value pairs, separated by spaces.
    The value itself may include spaces (in which case it'll be surrounded by single quotes ('),
    e.g.: file_version='6.1.7600.16471 (win7_gdr_oob_havtool(wmbla).090930-1630)'
    The value may not be surrounded by single quotes, in which case it shouldn't contain spaces,
    e.g.: sensor_id=8
    It's also possible that the value is surrounded by squarely brackets ([,]),
    e.g.: group=['Default Group']
    the regex in re.compile is used to separate these values from the rest of the input.
    :param ioc_raw: a string received from syslog describing the IOC
    :return: a dictionary mapping the fields listed in the ioc string to their corresponding value
    """
    #keywords look for these keywords when parsing the ioc string
    keywords = ["reason", "type", "md5", "host", "sensor_id", "watchlist_id", "watchlist_name", "timestamp",
                "first_seen", "group", "desc", "company_name", "product_name", "product_version", "file_version", "signed",
                "ioc_type", "ioc_value", "process_path", "parent_path", "target_path", "file_path", "comms_ip", "interface_ip",
                "local_ip", "feed_name", "process_md5", "remote_ip"]
    infection_dict = {}
    #get the value string for each keyword
    for keyword in keywords:
        #first, get the beginning of the value to end of the string
        rest = remove_till_word(ioc_raw, keyword + "=")
        if rest:
            #pattern of the value
            pattern= re.compile("([^\']\\S*|\'.+?\'|\\[.+?\\])\\s*")
            found = pattern.findall(rest)
            if found:
                #if the found value contains single quote, eg: 'some_value', remove the quote
                val = found[0].replace("'","")
                #add keyword and its value into infection_dict
                infection_dict[keyword] = val
    return infection_dict

def set_ioc_name(event, infection_props, ioc_dict):
    """
    get IOC name from the infection info dictionary parsing from syslog message and set name for ioc
    :param event: "reason" key value of preliminary infection info dictionary,
                    indicates what syslog message is about.
    :param infection_props: a dictionary of the preliminary infection info parsing from syslog message
    :param ioc_dict:  final ioc data dictionary
    :return: no turn, set key-value of ioc name for ioc dictionary
    """
    ioc_name = ""
    if infection_props.get("feed_name"):
        ioc_name = infection_props.get("feed_name")
    elif event.startswith("watchlist.hit") and infection_props.get("watchlist_name"):
        ioc_name = infection_props.get("watchlist_name")
    elif infection_props.get("type"):
        if infection_props.get("ioc_value") and not infection_props.get("ioc_value").startswith("{"):
            ioc_name = infection_props.get("ioc_type") + " " + infection_props.get("ioc_value")
        else:
            ioc_name = infection_props.get("ioc_type")
    if ioc_name:
        ioc_dict[IOC_NAME] = ioc_name

def set_file(infection_props, ioc_dict):
    """
    set file and file exists information for ioc. File information can be stored in one of four keywords
    including "process_path", "parent_path", "target_path" or "file_path" in syslog message
    :param infection_props: a dictionary of the preliminary infection info parsing from syslog message
    :param ioc_dict: final ioc data dictionary
    :return: no return. set key-value of file_name and file_exists for ioc dictionary
    """
    file_name = ""
    file_path = ""
    for path_type in ["process_path", "parent_path", "target_path", "file_path"]:
        if infection_props.get(path_type):
            file_info = get_file_info(infection_props[path_type])
            file_name = file_info[0]
            file_path = file_info[1]
            break
    if not file_name and infection_props.get("desc"):
        file_name = infection_props["desc"]
    if file_name and file_name not in ["//", ".//"]:
        ioc_dict[IOC_FILE_NAME] = file_name
        if file_path:
            ioc_file_exists = {
                IOC_FILE_NAME : file_name,
                IOC_FILE_PATH : file_path
            }
            ioc_dict[IOC_FILE_EXISTS] = ioc_file_exists

def set_hash(infection_props, ioc_dict):
    """
    set hash information for ioc. For Carbon Black specifically, hash information can be stored in one of two keywords
    including "process_md5" or "md5" in syslog message
    :param infection_props: a dictionary of the preliminary infection info parsing from syslog message
    :param ioc_dict: final ioc data dictionary
    :return: no return. set key-value of hash and hash_type for ioc dictionary
    """
    #set hash type and hash value
    #Carbon black normally only sends md5 hash
    hash_value = ""
    hash_type = ""
    md5_keywords = ["process_md5", "md5"]
    for md5_keyword in md5_keywords:
        if infection_props.get(md5_keyword):
            hash_type = "md5"
            hash_value = infection_props[md5_keyword]
    if not hash_type:
        #generate random md5 hash and set type "none" if no hash available
        hash_type = "none"
        hash_value = generate_random_md5()
    ioc_dict[IOC_HASH_TYPE] = hash_type
    ioc_dict[IOC_HASH] = hash_value

def set_severity(raw_ioc_data, ioc_dict):
    """
    set ioc severity. We use get_severity() to extract severity information from syslog message
    :param infection_props: a dictionary of the preliminary infection info parsing from syslog message
    :param ioc_dict: final ioc data dictionary
    :return: no return. set key-value of severity for ioc dictionary
    """
    ioc_severity = get_severity(raw_ioc_data)
    if ioc_severity:
        ioc_dict[IOC_SEVERITY] = ioc_severity

def set_cnc_dns(ioc_type, infection_props, ioc_dict):
    """
    set cnc or dns data for ioc
    :param ioc_type: type of ioc (cnc or dns)
    :param infection_props: a dictionary of the preliminary infection info parsing from syslog message
    :param ioc_dict: final ioc data dictionary
    :return: no return. set key-value of cnc address or dns query for ioc dictionary
    """
    if infection_props.get("ioc_type") and infection_props.get("ioc_value") and infection_props["ioc_type"] == ioc_type:
        ioc_type_value = infection_props["ioc_value"]
        ioc_dict[ioc_type] = ioc_type_value

def set_service(infection_props, ioc_dict):
    """
    set service information for ioc
    :param infection_props: a dictionary of the preliminary infection info parsing from syslog message
    :param ioc_dict: final ioc data dictionary
    :return:  no return. set key-value of service for ioc dictionary
    """
    ioc_service = ""
    if infection_props.get("product_name"):
        ioc_service = infection_props["product_name"]
    if infection_props.get("product_version"):
        ioc_service += infection_props["product_version"]
    if ioc_service:
        ioc_dict[IOC_SERVICE] = ioc_service

def set_platform(ioc_dict):
    #set platform for ioc
    #Some 3rd parties don't normally report the OS (eg: Carbon Black)
    ioc_dict[IOC_PLATFORM] = "none"

def get_file_info(file_path):
    """
    get the separate file name and file path information by splitting the whole path using the last "\" character
    :param file_path: complete file path from which we extract the last part, i.e. the file name
    :return: a list of file name and file path
    """
    pos = file_path.rfind("\\")
    if pos>0:
        file_name = file_path[pos+1:]
        path_name = file_path[:pos+1]
        return [file_name, path_name]
    return [file_path, file_path]

def get_severity(infection):
    """
    extract severity score from the raw data then map its value to severity category
    :param infection: the raw infection data or syslog message
    :return: string, severity category of the infection
    """
    LOW_SEVERITY_SCORE = 25
    MEDIUM_SEVERITY_SCORE = 50
    HIGH_SEVERITY_SCORE = 75
    LOW_SEVERITY = "low"
    MEDIUM_SEVERITY = "medium"
    HIGH_SEVERITY = "high"
    CRITICAL_SEVERITY = "critical"
    feed_score_name = "alliance_score_"
    severity = ""
    score_index = infection.find(feed_score_name)
    if score_index > 0:
        score_value_index = infection.find("=", score_index)
        rest = infection[score_value_index + 1 :]
        pattern = re.compile("([^\']\\S*|\'.+?\'|\\[.+?\\])\\s*")
        found = pattern.findall(rest)
        if found:
            val = found[0].replace("\\","").replace("'","")
            score = int(val)
            if score < 0:
                return severity
            elif score <= LOW_SEVERITY_SCORE:
                severity = LOW_SEVERITY
            elif score <= MEDIUM_SEVERITY_SCORE:
                severity = MEDIUM_SEVERITY
            elif score <= HIGH_SEVERITY_SCORE:
                severity = HIGH_SEVERITY
            else:
                severity = CRITICAL_SEVERITY
    return severity

def generate_random_md5():
    #generate a random md5 hash
    m = hashlib.md5(get_salt_string().encode())
    return m.hexdigest()

def get_salt_string():
    salt_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    salt_list = []
    #create a random md5 hash containing 18 alphanumeric characters
    while len(salt_list)<18:
        random_index = random.randint(len(salt_chars))
        salt_list.append(salt_chars[random_index])
    return "".join(salt_list)

def get_ioc_infos(ioc_raw):
    #get preliminary infection info as a dictionary from raw syslog message
    infection_props = parse_syslog_message(ioc_raw)
    ioc_infos = {}
    #"reason" key value indicates what syslog message is about.
    # If the "reason" value starts with "feed.", "watchlist.hit" or "binaryinfo", we know that syslog message contains IOC information
    event = infection_props.get("reason")
    if event and (event.startswith("feed.") or event.startswith("watchlist.hit") or event.startswith("binaryinfo")):
        #set ioc name
        set_ioc_name(event, infection_props, ioc_infos)
        #set platform
        set_platform(ioc_infos)
        #set file and file exists
        set_file(infection_props, ioc_infos)
        #set ioc severity
        set_severity(ioc_raw, ioc_infos)
        #set hash
        set_hash(infection_props, ioc_infos)
        #set ioc type - cnc
        set_cnc_dns(IOC_CNC, infection_props, ioc_infos)
        #set ioc type - dns
        set_cnc_dns(IOC_DNS, infection_props, ioc_infos)
        #set ioc type - service
        set_service(infection_props, ioc_infos)
    return ioc_infos

response = {}
logging.debug("SampleApp parse syslog message.")
# Check if we have syslog message or not before processing.
if params.get("connect_syslog_message"):
    syslog_message = params.get("connect_syslog_message")
    logging.debug(f"Syslog message is: {syslog_message}")
    try:
        # Do parsing
        ioc_info_dict = get_ioc_infos(syslog_message)
        """
        For IOC polling, the response dictionary must contain a dictionary or a list of dictionary called "ioc",
        which contains IOC information (single IOC or multiple IOCs respectively).
        Each IOC should be formatted as a dictionary with four mandatory keys of "name", "file_name", "hash" and "severity".
        To get more details about "ioc" response format, please refer to Connect help file.
        """
        response["ioc"] = ioc_info_dict
        logging.debug("response: {}".format(response))
    except Exception as e:
        response["error"] = f"Could not connect to SampleApp. {e}."
else:
    # In the response, put 'error' to indicate the error message.
    # 'connect_app_instance_cache' is optional when it has error.
    # if connect_app_instance_cache is in the response object, it will overwrite previous cache value.
    # Otherwise, the previous cache value will remain the same.
    response["error"] = "No syslog message is passed."
