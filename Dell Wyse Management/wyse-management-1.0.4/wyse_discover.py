import requests
from datetime import datetime
import ipaddress
import json
import time
import logging
import math

# CONFIGURATION
logging.info('===>Starting Wyse Management Suite Discover Script')

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params.get("connect_dellwysemanagementsuite_url", '')
baseURI = url + "/wms-api"
token = params.get('connect_authorization_token', '')

# ***** START - AUTH API CONFIGURATION ***** #
headers = {
  'X-Auth-Token': f'{token}'
}

logging.debug(f'Retrieved token from connect: {token[:5]}...')

#initialize response 
response = {
    "endpoints": []
}

# Endpoint object must look like:
# {
#   # Either mac or ip (or both) must be present
#   "mac": "string",
#   "ip": "string",
#   # a map/dictionary that contains host properties; the key will be the property name and the value will be the property value
#   "properties" : {}
# }

# Prepare to page through results
morePages = True
nextPageLink = None
retry = 0
while(morePages and retry < 3):
    # Allow 3 tries to make an api request before failing out totally
    retry += 1
    logging.debug(f'Making endpoint request attempt {retry} for page')
    # Create Request URL
    if not nextPageLink:
        api_request_url = f"{baseURI}/wms/v1/Systems?$filter = status eq 'Online'"
    else:
        api_request_url = f"{baseURI}{nextPageLink}&$filter = status eq 'Online'"

    # Make API Call
    try:
        resp = requests.get(api_request_url, headers=headers, verify=ssl_verify)
        if(resp.status_code == 200):
            response_json = resp.json()
            logging.debug(f'Request for page succeded! Received {len(response_json["Members"])} records in page. {response_json["Members@odata.count"]} records total to discover.')
            logging.debug(json.dumps(response_json))
            
            # keep track of paging
            if "Members@odata.nextLink" in response_json:
                logging.debug(f'Next page found in response: {response_json["Members@odata.nextLink"]}')
                nextPageLink = response_json["Members@odata.nextLink"]
                morePages = True
            else:
                logging.debug(f'No next page link in response request')
                nextPageLink = None
                morePages = False

            # Process members
            for member in response_json['Members']:
                logging.debug("Processing Host: " + member['@odata.id'])
                logging.debug("Raw Host Data: " + json.dumps(member))
                
                # Make sure some OEM data exists in response
                if "Oem" not in member:
                    logging.debug(f'Ignoring Host {member["@odata.id"]} -- Oem data missing')
                    continue
                    
                # Make sure some ip address data exists in response
                if "IpAdddress" not in member["Oem"]:
                    logging.debug(f'Ignoring Host {member["@odata.id"]} -- IP Address missing')
                    continue

                # Make sure last check in was today(), skip if not
                #if datetime.strptime(member["Oem"].get("LastCheckinTime", 'Jan 01 1970'), '%b %d %Y').date() != datetime.now().date():
                #    logging.debug(f'Ignoring Host {member["@odata.id"]} -- last check in date older than today')
                #    continue

                # Break out listed IPs
                ips = member["Oem"]["IpAdddress"].split(" , ")
                logging.debug(f'Processing {len(ips)} IP addresses on host: {json.dumps(ips)}')
                # Discard invalid or IPv6 IPs in host IP list
                valid_ips = []
                for ip in ips:
                    # ignore link local and ipv6 link local address, ignore ipv6 totally
                    try:
                        if(ipaddress.ip_address(ip).version != 4 or ipaddress.ip_address(ip).is_link_local or ipaddress.ip_address(ip).is_loopback):
                            logging.debug(f'Ignoring IP {ip} -- Link local, loopback, or IPv6 address')
                            continue
                    except Exception as e:
                        logging.debug(f'Ignoring IP {ip} -- Could not process with ipaddress: {str(e)}')
                        continue
                    valid_ips.append(ip)
                
                # Create host record for each valid IP
                for ip in valid_ips:
                    logging.debug(f'Creating host record for {ip}')
                    # create host record
                    endpoint = {
                        "ip": ip,
                        "properties": {
                            "connect_dellwysemanagementsuite_id": member['@odata.id'].replace('/wms/v1/Systems/', ''),
                            "connect_dellwysemanagementsuite_last_seen_in_api": math.floor(datetime.now().timestamp()),
                            "connect_dellwysemanagementsuite_device_details": {
                                "platform_type": member["Oem"].get("PlatformType", ''),
                                "system_name": member["Oem"].get("SystemName", ''),
                                "compliance": member["Oem"].get("Compliance", '0') == "1",
                                "type": member["Oem"].get("Type", ''),
                                "os_version": member["Oem"].get("OSVersion", ''),
                                "serial": member["Oem"].get("Serial", ''),
                                "last_user": member["Oem"].get("LastUser", ''),
                                "group": member["Oem"].get("Group", ''),
                                "last_checkin_date": int(datetime.strptime(member["Oem"]["LastCheckinTime"], '%b %d %Y').timestamp())
                            }
                        }
                    }
                    
                    # Create host in response to Forescout
                    response['endpoints'].append(endpoint)

            # Reset retry tracker
            retry = 0

        else:
            logging.error(f'Non-200 ({resp.status_code}) API Status code received. Will rety in a moment. Error: ' + json.dumps(resp.json()))
            time.sleep(retry * 0.2) # Delay retry

    except Exception as e:
        logging.error(f'Error in processing page: {str(e)}')
        time.sleep(retry * 0.2) # Delay retry

logging.info('===>Ending Wyse Management Suite Discovery Script')
logging.debug(json.dumps(response['endpoints']))