# Forescout
eyeExtend Connect for Nutanix App README.md Version: 1.0.0

## Configuration Guide
**Version 3.0.0**
- Added OAuth 2.0 authentication mechanism

**Version 3.0.1**
- Resolved issue with proxy usage

## Release Notes

### Version 1.0.5 (February 2026)
#### Prerequisite
- connect_module need to be on v2.0.5 or above for multi-cluster support
- Host Discovery has to be enabled so that each endpoint knows under which controller

#### New Features
- **VM NIC Control Actions**: Added two new remediation actions for managing VM network interfaces
  - **Disable VM NIC**: Action to disconnect VM network adapters through Prism API
  - **Enable VM NIC**: Action to connect VM network adapters through Prism API
  - Undo capability: "Disable VM NIC" action includes automatic undo that re-enables the NIC
- **Controller IP Property**: Added new property `connect_nutanix_controller_ip` to track Nutanix VM Controller IP address for each endpoint
- **Controller Routing**: Enabled controller routing configuration with support for managing endpoints based on controller IP

#### Enhancements
- **Multi-cluster support**. Added controller IP property to all VM endpoints during poll and resolve operations
- Enhanced polling script with debug logging for host metadata to improve troubleshooting
- Added action icons for all action states (normal, failed, gray, waiting) for both enable and disable operations

#### Script Changes
- New scripts:
  - `nutanix_disable_nic.py`: Implements VM NIC disconnection via Prism v3 API
  - `nutanix_enable_nic.py`: Implements VM NIC connection via Prism v3 API and serves as undo action
- Updated scripts:
  - `nutanix_poll.py`: Added controller IP tracking and enhanced logging
  - `nutanix_resolve.py`: Updated to include controller IP in resolved properties
  - `nutanix_test.py`: Fixed comment typos

#### Configuration Updates
- Updated property.conf:
  - Added `connect_nutanix_controller_ip` property definition
  - Added action definitions for enable/disable VM NIC operations
  - Configured undo relationship between disable and enable actions
  - Added script mappings for new action scripts
- Updated system.conf:
  - Version bump: 1.0.1 → 1.0.5
  - Enabled controller routing
  - Added controller config field name mapping

### Version 1.0.1
- Initial release with Prism v3 API integration
- Host and VM polling and resolution capabilities

## Contact Information  
- Have feedback or questions? Write to us at

 <connect-app-help@forescout.com>

## App Support

- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.

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
