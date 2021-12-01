# Nutanix Connect App v1.0.0

This first version of Nutanix eyeExtend Connect App v1.0.0 is used to leverage PRISM v3 API to Poll / Resolve Properties from Nutanix Hyperconverged Platform through Prism Central. 

 Prism v3 is an Intentful API designed for full environment management via Nutanix Prism Central. We leveraged four API Endpoitns to List Hosts (Poll), or get an update of a specific Host Details (Resolve), in addition to List VMs (Poll) and update a specific VM Details (Resolve). For Poll queries, recursive Paging has been implemented to ensure all Hosts / VMs, including their properties details are Polled via Prism Central. 
 
## Host Properties Polled / Resolved 

For Hosts, the following properties will be learned: 
- Host uuid 
- Host Details (Composite)

The Host Details Composite includes the following sub-fields: 
- Name
- State 
- Serial Number 
- Number of VMs 
- Hypervisor Full Name
- Host Type
- CPU Model
- CPU Capacity (Hz)
- Num. of CPU Cores
- Controller VM IP
- Controller Op Log Usage(%)
- Memory Size (MB)

## VM Properties Polled / Resolved 

For Virtual Machines, the following properties will be learned: 
- VM uuid 
- VM Details (Composite)

The VM Details Composite includes the following sub-fields: 
- Name
- State
- Num vCPU per Socket
- Num. Sockets
- Threads per Core
- is Agent VM
- VGA Console Enabled
- Protection Type
- Memory Size (MB)
- Machine Type
- Host Ref Kind
- Host Ref uuid
- Host Ref Name
- Hypervisor Type
- CPU Passthru Enabled
- Power State
- Branding Disabled
- Cluster Ref Kind
- Cluster Ref uuid
- Cluster Ref Name 
- NIC uuid (per Endpoint)
- NIC Connected (per Endpoint)
- NIC Vlan Mode (per Endpoint)
- NIC Type (per Endpoint)
- NIC Subnet Ref (per Endpoint)

## Community Support Requirements
•	Prism v3 API. 
•	Forescout CounterACT 8.2.2
•	Forescout eyeExtend Connect 1.6

## Configuration required on Nutanix App

Default port is 9440 (if custom port is needed we can easily modify the App to accomodate this requirement).  

- Prism API(v3) IP 
- Username 
- Password 

User Account needed requires read-only access to the following API endpoints: 
- /api/nutanix/v3/vms/list
- /api/nutanix/v3/vms/{vm_uuid}
- /api/nutanix/v3/hosts/list
- /api/nutanix/v3/hosts/{host_uuid}
    
## Verifying Connectivity 

Use Test button (which is enabled by default) to verify connectivity to PRISM v3 API. 

## Policy Templates

Includes one template policy to identify endoints with Host Details / Host uuid and VM Details / VM uuid. 
