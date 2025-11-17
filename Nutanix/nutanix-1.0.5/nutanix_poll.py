from base64 import b64encode
import requests
import logging
import json

def get_property(obj:dict, path:str): 
    """returns the value of a path(dot notations) of a provided Object"""
    if '.' in list(path): 
        path_list = path.split('.')
        rel_obj = obj.copy() 
        for item in path_list: 
            if hasattr(rel_obj, 'get'):
                rel_obj = rel_obj.get(item, {})
            else: 
                rel_obj = {}
        if type(rel_obj) != dict and type(rel_obj) != list:
            return str(rel_obj) # other types like int, float, bool => convert to string
        else: 
            return rel_obj
    else: 
        return obj.get(path, '') # either get the value or return empty string if key do not exist
    

    
    
def get_host_endpoint(host:dict)->dict: 
    endpoint = {}
    properties = {}
    
    if host == {}:
        return {}
    
    if 'status' not in host or 'metadata' not in host: 
        return {}

    # ip is the key for the hosts endpoints
    endpoint["ip"] = get_property(host, 'status.resources.hypervisor.ip')
    host_uuid = get_property(host, 'metadata.uuid')
    
    properties['name'] = get_property(host, 'status.name')
    properties['state']= get_property(host, 'status.state')
    properties['serial_number'] = get_property(host, 'status.resources.serial_number')
    properties['num_vms'] = get_property(host, 'status.resources.hypervisor.num_vms')
    properties['hypervisor_full_name'] = get_property(host, 'status.resources.hypervisor.hypervisor_full_name')
    properties['host_type'] = get_property(host, 'status.resources.host_type')
    properties['cpu_model'] = get_property(host, 'status.resources.cpu_model')
    properties['num_cpu_sockets'] = get_property(host, 'status.resources.num_cpu_sockets')
    properties['num_cpu_cores'] = get_property(host, 'status.resources.num_cpu_cores')
    properties['controller_vm_ip'] = get_property(host, 'status.resources.controller_vm.ip')
    properties['controller_vm_op_log_usage'] = get_property(host, 'status.resources.controller_vm.oplog_usage.oplog_disk_pct')
    properties['cpu_capacity_hz'] = get_property(host, 'status.resources.cpu_capacity_hz')
    properties['memory_capacity_mib'] = get_property(host, 'status.resources.memory_capacity_mib')

    endpoint["properties"] = {}
    endpoint["properties"]['connect_nutanix_host_details'] = properties
    endpoint["properties"]['connect_nutanix_host_uuid'] = host_uuid

    return endpoint 

def get_vm_endpoint(vm: dict, endpoints:list)->list: # returns endpoints list after appending the new endpoints 
    """parse vm properties and add one or multiple endpoints and returns the new appended endpoints. """
    properties = {}

    mac_list=[]
    ip_list=[]
    is_connected_list=[]
    nic_type_list = []
    vlan_mode_list = []
    nic_uuid_list = []
    subnet_reference_list = []

    for nic in get_property(vm, 'status.resources.nic_list'):
        mac_list.append(get_property(nic, 'mac_address'))
        nic_type_list.append(get_property(nic, 'nic_type'))
        vlan_mode_list.append(get_property(nic, 'vlan_mode'))
        nic_uuid_list.append(get_property(nic, 'uuid'))
        subnet_reference_list.append(get_property(nic, 'subnet_reference.name'))

        if get_property(nic, 'is_connected') == True: 
            is_connected_list.append('true')
        else: 
            is_connected_list.append('false')
        nic_ips = get_property(nic, 'ip_endpoint_list' )

        if len(nic_ips) == 1: 
            ip_list.append(nic_ips[0].get('ip', ''))
        else: 
            ip_list.append([x.get('ip', '') for x in nic_ips]) # corner case 
            # there could be a case with multiple IPs for a single mac?

    # logging errors if mac or ip are not found for that vm
    if len(mac_list)==0 and len(ip_list)==0: 
        logging.error("Neither MAC nor IP address are found for vm with UID: " + get_property(vm, 'metadata.uuid'))
        return endpoints
    
    elif len(mac_list)==0: 
        logging.error("MAC is not found for vm with UID: " + get_property(vm, 'metadata.uuid'))
    elif len(ip_list)==0: 
        logging.error("IP is not found for vm with UID: " + get_property(vm, 'metadata.uuid'))

    if len(mac_list)>0 or len(ip_list)>0: 
        properties['name'] = get_property(vm, 'status.name') 
        properties['state'] = get_property(vm, 'status.state')
        vm_uuid = get_property(vm, 'metadata.uuid')
        properties['num_vcpus_per_socket'] = get_property(vm, 'status.resources.num_vcpus_per_socket')
        properties['num_sockets'] = get_property(vm, 'status.resources.num_sockets')
        properties['num_threads_per_core'] = get_property(vm, 'status.resources.num_threads_per_core')
        properties['is_agent_vm'] = get_property(vm, 'status.resources.is_agent_vm')
        properties['protection_type'] =  get_property(vm, 'status.resources.protection_type')
        properties['memory_size_mib'] =  get_property(vm, 'status.resources.memory_size_mib')
        properties['machine_type'] =  get_property(vm, 'status.resources.machine_type')
        properties['vga_console_enabled'] = get_property(vm, 'status.resources.vga_console_enabled')
        properties['host_reference_kind'] = get_property(vm, 'status.resources.host_reference.kind')
        properties['host_reference_uuid'] = get_property(vm, 'status.resources.host_reference.uuid')
        properties['host_reference_name'] = get_property(vm, 'status.resources.host_reference.name')
        properties['hypervisor_type'] =  get_property(vm, 'status.resources.hypervisor_type')
        properties['power_state'] = get_property(vm, 'status.resources.power_state')
        properties['enable_cpu_passthrough'] = get_property(vm, 'status.resources.enable_cpu_passthrough')
        properties['disable_branding'] = get_property(vm, 'status.resources.disable_branding')
        properties['cluster_reference_kind'] = get_property(vm, 'status.cluster_reference.kind')
        properties['cluster_reference_uuid'] = get_property(vm, 'status.cluster_reference.uuid')
        properties['cluster_reference_name'] = get_property(vm, 'status.cluster_reference.name')
        for i in range(len(nic_uuid_list)): 
            endpoint={}
            local_props = properties.copy()

            local_props['vm_nic_uuid'] = nic_uuid_list[i]

            if i< len(vlan_mode_list):
                local_props['vm_nic_vlan_mode'] = vlan_mode_list[i]

            if i< len(is_connected_list):
                local_props['vm_nic_is_connected'] = is_connected_list[i]

            if i< len(nic_type_list):
                local_props['vm_nic_type'] = nic_type_list[i]

            if i< len(subnet_reference_list):
                local_props['vm_nic_subnet_reference'] = subnet_reference_list[i]

            if i < len(mac_list):
                endpoint["mac"] = mac_list[i].replace(":", "")


            if i < len(ip_list):
                ip_item = ip_list[i]
                if type(ip_item) == list:
                    i = 0
                    for ip in ip_item: 
                        ep = endpoint.copy()
                        new_local_props = local_props.copy()
                        if i > 0:
                            new_local_props['vm_nic_mac'] = ep['mac']
                            del ep['mac']
                        ep['ip'] = ip
                        ep["properties"]={}
                        ep["properties"]['connect_nutanix_vm_details'] = new_local_props
                        ep["properties"]['connect_nutanix_vm_uuid'] = vm_uuid
                        ep["properties"]['connect_nutanix_controller_ip'] = prism_api_ip
                        endpoints.append(ep)
                        i+=1
                else: 

                    endpoint['ip'] = ip_item
                    endpoint["properties"]={}
                    endpoint["properties"]['connect_nutanix_vm_details'] = local_props
                    endpoint["properties"]['connect_nutanix_vm_uuid'] = vm_uuid
                    endpoint["properties"]['connect_nutanix_controller_ip'] = prism_api_ip
                    endpoints.append(endpoint)
        
    return endpoints
    
logging.info('===>Starting Nutanix Poll Script')

prism_api_ip = params.get('connect_nutanix_prism_api_ip', '')
username = params.get('connect_nutanix_username', '')
password = params.get('connect_nutanix_password', '')

# prepare encoded credentials based on username/password
encoded_credentials = b64encode(bytes(f'{username}:{password}',\
                                      encoding='ascii')).decode('ascii')
# prepare the headers
auth_header = f'Basic {encoded_credentials}'

headers = { 
            'Accept': 'application/json', 
            'Content-Type': 'application/json',
            'Authorization': f'{auth_header}', 
            'cache-control': 'no-cache'
          }

# base api URI
base_uri = f'https://{prism_api_ip}:9440/api/nutanix/v3'

# final polled endpoints
endpoints = []

# final response to be shared
response = {}

# Number of hosts to rectrieve per request 
length_limit = 100 
hosts_offset = 0

# 1. Retrieve list of Hosts 
url = f'{base_uri}/hosts/list'
data = f'{{"kind":"host", "offset":{hosts_offset}, "length":{length_limit} }}'

try:
    logging.info("Polling Hosts Started.")
    resp = requests.request('post', url, data=data, headers=headers, verify=False)
    
    if resp.status_code == 200: 
        content = json.loads(resp.content)
        
        total_hosts = int(get_property(content, 'metadata.total_matches'))
        length = get_property(content, 'metadata.length')

        logging.debug("Polling Hosts response: " + str(length) + " hosts found in metadata, total: " + str(total_hosts))

        if length=={}:
            received_length = total_hosts
        elif type(length)==str: 
            received_length = int(length)
        
        if total_hosts >0: 
            for host in content.get('entities', {}):
                endpoint = get_host_endpoint(host)
                if endpoint != {}:
                    endpoints.append(endpoint)
                else: 
                    logging.error(f'Error while parsing host: {host}')
                    
        if total_hosts>0 and total_hosts == received_length:  
            logging.info("Polling Hosts completed")
            # endpoints is now populated with the hosts properties  
        
        elif total_hosts > received_length:
            remaining = total_hosts - received_length 
            while remaining > 0:
                logging.info(f"Polled {received_length} hosts, remaining: {remaining}")
                hosts_offset += received_length
                if remaining > length_limit: 
                    length = length_limit 
                else: 
                    length = remaining 
                
                logging.info(f"sending poll request for hosts with offset {hosts_offset}, and length : {length}") 
                
                data = f'{{"kind":"host", "offset":{hosts_offset}, "length":{length} }}'
                resp = requests.request('post', url, data=data, headers=headers, verify=False)
                if resp.status_code == 200: 
                    content = json.loads(resp.content)
                    received_length = int(get_property(content, 'metadata.length'))
                    if received_length > 0: 
                        for host in content.get('entities', {}):
                            endpoint = get_host_endpoint(host)
                            if endpoint != {}:
                                endpoints.append(endpoint)
                            else: 
                                logging.error(f'Error while parsing host: {host}')
                        
                        remaining -=received_length
                    else: 
                        remaining = 0 
                        logging.error(f'Error received Zero hosts from last query with offset: {hosts_offset}')
                        
                        response["succeeded"] = False
                        response["error"] = "Error polling remaining Hosts as received length was Zero!"
            
                else:
                    remaining = 0 
                    response['succeeded'] = False
                    response['result_msg'] = 'Could not connect to Nutanix Server'
                    logging.info(f'Poll Script was not successful - status code: {resp.status_code}')        
                
        elif total_hosts==0: 
            logging.error(" No Hosts were found in metadata")
            response["succeeded"] = False
            response["error"] = "Error polling Hosts as no hosts were found in metadata."
            
    else:
        response['succeeded'] = False
        response['result_msg'] = 'Could not connect to Nutanix Server'
        logging.info(f'Poll Script was not successful - status code: {resp.status_code}')

except requests.exceptions.RequestException as e: 
    response['succeeded'] = False
    response['result_msg'] = f'Could not connect to Nutanix Server.. Exception occured: {e}'


# Number of hosts to retrieve per request
length_limit = 100 
vms_offset = 0

# 2. Retrieve list of VMs 
url = f'{base_uri}/vms/list'
data = f'{{"kind":"vm", "offset":{vms_offset}, "length":{length_limit} }}'

try:
    logging.info("Polling VMs Started.")
    resp = requests.request('post', url, data=data, headers=headers, verify=False)
    
    if resp.status_code == 200: 
        content = json.loads(resp.content)
        total_vms = int(get_property(content, 'metadata.total_matches'))
        length = get_property(content, 'metadata.length')
        if length=={}:
            received_length = total_vms
        elif type(length)==str: 
            received_length = int(length)
        
        if total_vms>0:  
            for vm in content.get('entities', {}):
                endpoints = get_vm_endpoint(vm, endpoints)
        
        if total_vms>0 and total_vms == received_length:  
            logging.info("Polling VMs completed")
            # endpoints is now populated with the hosts properties  
        
        elif total_vms > received_length:
            remaining = total_vms - received_length 
            while remaining > 0:
                logging.info(f"Polled {received_length} VMs, remaining: {remaining}")
                vms_offset += received_length
                if remaining > length_limit: 
                    length = length_limit 
                else: 
                    length = remaining 
                
                logging.info(f"sending poll request for VMs with offset {vms_offset}, and length : {length}") 
                
                data = f'{{"kind":"vm", "offset":{vms_offset}, "length":{length_limit} }}'
                resp = requests.request('post', url, data=data, headers=headers, verify=False)
                if resp.status_code == 200: 
                    content = json.loads(resp.content)
                    received_length = int(get_property(content, 'metadata.length'))
                    if received_length > 0: 
                        for vm in content.get('entities', {}):
                            endpoints = get_vm_endpoint(vm, endpoints)
                        
                        remaining -=received_length
                    else: 
                        remaining = 0 
                        logging.error(f'Error received Zero VMs from last query with offset: {vms_offset}')
                        
                        response["succeeded"] = False
                        response["error"] = "Error polling remaining VMs as received length was Zero!"
            
                else:
                    remaining = 0 
                    response['succeeded'] = False
                    response['result_msg'] = 'Could not connect to Nutanix Server'
                    logging.info(f'Poll Script for VMs was not successful - status code: {resp.status_code}')  
        else: 
            logging.error(" No Hosts were found in metadata")
            response["succeeded"] = False
            response["error"] = "Error polling Hosts as no hosts were found in metadata."
            
                   
        logging.debug("Polling VMs completed")

        # endpoints is now populated with the VMs properties  
        response["endpoints"] = endpoints
        logging.info('===>Ending Nutanix Poll Script')
        logging.debug('Poll Script replied with the following response: '+str(response))
            

            
    else:
        response['succeeded'] = False
        response['result_msg'] = 'Could not connect to Nutanix Server'
        logging.info(f'Poll Script was not successful - status code: {resp.status_code}')

except requests.exceptions.RequestException as e: 
    response['succeeded'] = False
    response['result_msg'] = f'Could not connect to Nutanix Server.. Exception occured: {e}'
