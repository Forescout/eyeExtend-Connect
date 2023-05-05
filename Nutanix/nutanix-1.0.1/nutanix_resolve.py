from base64 import b64encode
import requests
import logging
import json

logging.info('===>Starting nutanix Resolve Script')
logging.debug("Resolve Script for nutanix has been called with the following Params:")
logging.debug(params)


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
    

    
    
def resolve_host_endpoint(host:dict)->dict: 
    endpoint = {}
    properties = {}
    
    if host == {}:
        return {}
    
    if 'status' not in host or 'metadata' not in host: 
        return {}

    # ip is the key for the hosts endpoints
    #endpoint["ip"] = get_property(host, 'status.resources.hypervisor.ip')
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

def resolve_vm_endpoint(vm: dict, ip:str) ->dict: # returns updated info of that endpoint
    """parse vm properties and add one or multiple endpoints and returns the new appended endpoints. """
    properties = {}
    
    nics = get_property(vm, 'status.resources.nic_list')   
    sel_nic = {}
    
    for nic in nics:
        nic_ips = get_property(nic, 'ip_endpoint_list' )
        for nic_ip_ep in nic_ips: 
            _ip = nic_ip_ep.get('ip', '')
            if ip == _ip:
                sel_nic = nic 
    
    vm_uuid = get_property(vm, 'metadata.uuid')
    properties['name'] = get_property(vm, 'status.name') 
    properties['state'] = get_property(vm, 'status.state')
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
    if sel_nic == {}:
        logging.warning(f"Resolve Script: Warning the provided IP {ip} do not exist in the NICs IPs. Re-poll is needed.")
    else: 
        mac = get_property(nic, 'mac_address').replace(":", "")
        properties['vm_nic_uuid'] = get_property(sel_nic, 'uuid')
        properties['vm_nic_vlan_mode'] = get_property(sel_nic, 'vlan_mode')
        properties['vm_nic_is_connected'] = get_property(sel_nic, 'is_connected')
        properties['vm_nic_type'] = get_property(sel_nic, 'nic_type')
        properties['vm_nic_subnet_reference'] = get_property(nic, 'subnet_reference.name')
        response['ip'] = ip
        response['mac'] = mac
    
    response["properties"]={}
    response['properties']['connect_nutanix_vm_details'] = properties 
    response["properties"]['connect_nutanix_vm_uuid'] = vm_uuid
        
    return response

prism_api_ip = params.get('connect_nutanix_prism_api_ip', '')
username = params.get('connect_nutanix_username', '')
password = params.get('connect_nutanix_password', '')

host_uuid = params.get('connect_nutanix_host_uuid', '')
vm_uuid = params.get('connect_nutanix_vm_uuid', '')
ip = params.get('ip', '')


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

# implement Host GET method if host_uuid is not empty
response = {}
if host_uuid != '':
    url = f'{base_uri}/hosts/{host_uuid}'
    try: 
        resp = requests.request('get', url,  headers=headers, verify=False)

        
        if resp.status_code == 200: 
            host = json.loads(resp.content)
            response = resolve_host_endpoint(host)
        else: 
            response['error'] = f'Could not connect to Nutanix Server while resolving host_uuid: {host_uuid}'
            logging.info(f'Resolve Script for host uuid: {host_uuid} was not successful - status code: {resp.status_code}')
    except requests.exceptions.RequestException as e: 
        response['error'] = f'Could not connect to Nutanix Server while resolving host_uuid: {host_uuid}. Exception: {e}'
        logging.info(f'Resolve Script failed for host uuid: {host_uuid} - Exception: {e}')

# implement VM GET method if vm_uuid is not empty
if vm_uuid != '':
    url = f'{base_uri}/vms/{vm_uuid}'
    try:
        resp = requests.request('get', url,  headers=headers, verify=False)
        if resp.status_code == 200: 
            vm = json.loads(resp.content)
            response = resolve_vm_endpoint(vm, ip)
        else: 
            response['error'] = f'Could not connect to Nutanix Server while resolving vm_uuid: {vm_uuid}'
            logging.info(f'Resolve Script for VM uuid: {vm_uuid} was not successful - status code: {resp.status_code}')
    except requests.exceptions.RequestException as e: 
        response['error'] = f'Could not connect to Nutanix Server while resolving vm_uuid: {vm_uuid}. Exception: {e}'
        logging.info(f'Resolve Script failed for VM uuid: {vm_uuid} - Exception: {e}')

if host_uuid == '' and vm_uuid == '':
    response['error'] = f'No Host UUID neither VM UUID are found on this host {ip} - skipping.'
    logging.info(f'No Host UUID neither VM UUID are found on this host {ip} - skipping.')

logging.info('===>Ending nutanix Resolve Script')
