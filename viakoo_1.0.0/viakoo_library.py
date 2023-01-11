import requests
import logging


API_URL = 'https://api1.viakoo.com'

CURRENT_NAV_ENDPOINT = "navigation/getCurrentNav"
SEARCH_ENDPOINT = "navigation/search"
LIST_ENDPOINT = "component/list"

DEVICE_TYPES = ["genericDevice", "camera", "accessControlDevice", "switch"]

# Mapping between viakoo response fields to CounterACT properties
FIELD_RESOLVE_MAP = {
     "id" : "connect_viakoo_id", 
     "deviceName" : "connect_viakoo_device_name", 
     "manufacturer" : "connect_viakoo_manufacturer", 
     "model" : "connect_viakoo_model", 
     "firmwareVersion" : "connect_viakoo_firmware_version", 
     "deviceType" : "connect_viakoo_device_type", 
     "macAddress" : "connect_viakoo_mac_address", 
     "ipAddress" : "connect_viakoo_ip_address", 
     "classType" : "connect_viakoo_class_type", 
     "complianceState" : "connect_viakoo_compliance_state", 
     "isPingable" : "connect_viakoo_is_pingable", 
     "lastUpdated" : "connect_viakoo_last_updated", 
     "dateCreated" : "connect_viakoo_date_created", 
     "snmpDescription" : "connect_viakoo_snmp_description", 
     "isOnline" : "connect_viakoo_isOnline", 
     "reporter" : "connect_viakoo_reporter", 
     "motionPercent" : "connect_viakoo_motion_percent", 
     "resolution" : "connect_viakoo_resolution", 
     "status" : "connect_viakoo_status", 
     "serialNumber" : "connect_viakoo_serial_number", 
     "codec" : "connect_viakoo_codec", 
    
}

def validate_site(request_session, device_headers, site):
    message_info = {}
    message_info['response'] = "Failed"
    message_info['site_id'] = None

    #Check if the "site" is an ID first if no match do a search
    try:
        site_id = int(site)

        nav_body = {
            "navigable_id" : site_id
        }

        device_headers['Content-Type'] = 'application/x-www-form-urlencoded'

        resp_site_check = request_session.post("{}/{}".format(API_URL, CURRENT_NAV_ENDPOINT), data=nav_body, headers=device_headers)

        if resp_site_check.status_code == requests.codes.ok:
            resp_json = resp_site_check.json()

            if 'currentNav' in resp_json:
                if resp_json['currentNav']['id'] == site_id:
                    logging.info("Site found: {}".format(resp_json['currentNav']['name']))
                    message_info['response'] = "Connection successful"
                    message_info['site_id'] = site_id
                else:
                    logging.info("No site with ID {}, running a search")
            else:
                logging.info("Failed to check site ID, trying a search")
        else:
            logging.info("Request failed. {}".format(resp_site_check.status_code))
    except Exception:
        logging.info("Site could not convert to long, must be a name")

    #Search for the Site
    if not message_info['site_id']:
        logging.info("Searching for site: {}".format(site))
        search_data = { 
                    "location": site,
                    "device": "",
                    "ipAddress": "",
                    "macAddress": ""
                }

        device_headers['Content-Type'] = 'application/json'

        resp_site_check = request_session.post("{}/{}".format(API_URL, SEARCH_ENDPOINT), json=search_data, headers=device_headers)

        if resp_site_check.status_code == requests.codes.ok:
            resp_json = resp_site_check.json()
            logging.debug(resp_json)

            #Failed to run the search
            if resp_json and 'message' in resp_json:
                message_info['response'] = resp_json['message']
            else:
                if len(resp_json['locations']) == 0:
                    message_info['response'] = "No sites found with this name: {}".format(site)

                if resp_json['locations'][0]["class"] != "Realm":
                    for location in resp_json['locations']:
                        if location['name'] == site:
                            message_info['response'] = "Connection successful"
                            message_info['site_id'] = location['id']
                    
                    if not message_info['site_id']:
                        message_info['response'] = "No exact match for site {} found. {} possibilities. Use siteId if issues continue.".format(site, len(resp_json['locations']))
                else:
                    message_info['response'] = "Site used cannot be of type Realm."
        else:
            message_info['response'] = "Failed to search. Use Site ID if issue continues. {}".format(resp_site_check.status_code)


    return message_info