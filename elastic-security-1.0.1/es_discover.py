import requests
import ipaddress
from datetime import datetime
import json
import time

# Get parameters
username = params["connect_elasticsecurity_kibana_username"]
password = params["connect_elasticsecurity_kibana_password"]
ignore_ips = params["connect_elasticsecurity_ignore_ips"]
ignore_time = int(params["connect_elasticsecurity_ignore_time"])
recordsPerPage = int(params["connect_elasticsecurity_records_per_page"])
now = datetime.now()

logging.info("===> Elastic Security: Start Host Discovery")

# explode ignore_ips into ip networks
ip_networks = []
for ip in ignore_ips.split(","):
    try: 
        ip_networks.append(ipaddress.ip_network(ip.strip()))
    except Exception as e:
        logging.warning(f'IP Range in connect_elasticsecurity_ignore_ips does not appear to be valid: {ip.strip()}')


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
page = 0
totalRecords = recordsPerPage+1 # Force first request to fire; total records will be updated in response request
retry = 0
while(page*recordsPerPage < totalRecords and retry < 3):
    # Allow 3 tries to make an api request before failing out totally
    retry += 1
    logging.debug(f'Making endpoint request attempt {retry} for page {page}')
    url = f'{params["connect_elasticsecurity_kibana_url"]}/api/endpoint/metadata?sortField=last_checkin&pageSize={recordsPerPage}&page={page}&hostStatuses=["healthy", "unhealthy", "updating"]'
    try:
        request = requests.get(
            url,
            verify=ssl_verify,
            headers={'kbn-xsrf': 'true'},
            auth=(username, password)
        )

        if(request.status_code == 200):
            response_json = request.json()
            logging.debug(f'Endpoint request for page {page} succeded! Received {len(response_json["data"])} records in page. {response_json["total"]} records total to discover.')
            logging.debug(json.dumps(response_json))
            
            # keep track of paging
            totalRecords = response_json["total"]
            page += 1

            for agent in response_json['data']:
                logging.debug("Processing Host: " + agent['metadata']['elastic']['agent']['id'])
                logging.debug(f'Processing {len(agent["metadata"]["host"]["ip"])} IP addresses on host: {json.dumps(agent["metadata"]["host"]["ip"])}')
                
                # Ignore if Last check in time > ignore_time (minutes)
                last_checkin = datetime.strptime(agent['last_checkin'], '%Y-%m-%dT%H:%M:%S.%fz')
                minutes = (now-last_checkin).total_seconds() / 60
                if(minutes > ignore_time):
                    logging.debug(f'Ignoring IP {ip} -- Agent last check in greater than maximum allowed (connect_elasticsecurity_ignore_time) in app configuration')
                    continue

                # Discard invalid IPs in host IP list
                valid_ips = []
                for ip in agent['metadata']['host']['ip']:
                    # ignore ip ranges in app configuration exlcude list
                    if(True in map(lambda network: ipaddress.ip_address(ip) in network, ip_networks)):
                        logging.debug(f'Ignoring IP {ip} -- Contained in IP Ignore list (connect_elasticsecurity_ignore_ips) in app configuration')
                        continue
                    # ignore ipv6, loopback and link local address
                    if(ipaddress.ip_address(ip).version == 6 or ipaddress.ip_address(ip).is_link_local or ipaddress.ip_address(ip).is_loopback):
                        logging.debug(f'Ignoring IP {ip} -- Link local or loopback address')
                        continue
                    valid_ips.append(ip)

                # iterate through valid IPs
                for ip in valid_ips:
                    logging.debug(f'Creating host record for {ip}')
                    # create host record
                    endpoint = {
                        "ip": ip,
                        "properties": {
                            "connect_elasticsecurity_agent_id": agent['metadata']['elastic']['agent']['id'],
                            "connect_elasticsecurity_host_status": agent['host_status'],
                            "connect_elasticsecurity_last_checkin": int(last_checkin.strftime('%s')),
                            "connect_elasticsecurity_ips": valid_ips,
                            "connect_elasticsecurity_number_of_ips": len(valid_ips),
                            "connect_elasticsecurity_macs": list(map(lambda mac: "".join(mac.split("-")), agent['metadata']['host']['mac'])),
                            "connect_elasticsecurity_number_of_macs": len(agent['metadata']['host']['mac']),
                            "connect_elasticsecurity_meta_host": {
                                "hostname": agent['metadata']['host']['hostname'],
                                "os_variant": agent['metadata']['host']['os']['Ext']['variant'],
                                "os_kernel": agent['metadata']['host']['os']['kernel'],
                                "os_name": agent['metadata']['host']['os']['name'],
                                "os_family": agent['metadata']['host']['os']['family'],
                                "os_type": agent['metadata']['host']['os']['type'],
                                "os_version": agent['metadata']['host']['os']['version'],
                                "os_platform": agent['metadata']['host']['os']['platform'],
                                "os_full": agent['metadata']['host']['os']['full'],
                                "architecture": agent['metadata']['host']['architecture']
                            },
                            "connect_elasticsecurity_meta_endpoint": {
                                "capabilities": agent['metadata']['Endpoint']['capabilities'],
                                "configuration_isolation": agent['metadata']['Endpoint']['configuration']['isolation'],
                                "state_isolation": agent['metadata']['Endpoint']['state']['isolation'],
                                "policy_name": agent['metadata']['Endpoint']['policy']['applied']['name'],
                                "policy_endpoint_policy_version": agent['metadata']['Endpoint']['policy']['applied']['endpoint_policy_version'],
                                "policy_version": agent['metadata']['Endpoint']['policy']['applied']['version'],
                                "policy_status": agent['metadata']['Endpoint']['policy']['applied']['status'],
                                "status": agent['metadata']['Endpoint']['status']
                            },
                            "connect_elasticsecurity_meta_agent": {
                                "build": agent['metadata']['agent']['build']['original'],
                                "type": agent['metadata']['agent']['type'],
                                "version": agent['metadata']['agent']['version']
                            }
                        }
                    }
                    # Set mac address if only 1 mac present
                    if(len(agent['metadata']['host']['mac']) == 1):
                        endpoint["mac"] = "".join(agent['metadata']['host']['mac'][0].split("-"))
                    # Create host in response
                    # logging.debug(json.dumps(endpoint))
                    response['endpoints'].append(endpoint)
                # Reset retry tracker
                retry = 0
        else:
            logging.error("API Status code error: " + json.dumps(request.json()))
            time.sleep(retry * 0.2) # Delay retry
    except Exception as e:
        logging.error(f'Endpoint request for page {page}  failed: + {str(e)}')
        response["error"] = str(e)
        time.sleep(retry * 0.2) # Delay retry

logging.info("===> Elastic Security: End Host Discovery")
# print(json.dumps(response['endpoints']))