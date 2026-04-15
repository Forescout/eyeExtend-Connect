# Oracle KVM (OLVM) Connect App

## About

This Forescout eyeExtend Connect App integrates with **Oracle Linux Virtualization Manager (OLVM) 4.5** (based on oVirt) to discover and monitor virtual machines and hypervisor hosts.

## Requirements

| Requirement | Details |
|---|---|
| Forescout Platform | 8.x with eyeExtend Connect module |
| OLVM Version | 4.5 (oVirt-compatible REST API) |
| Credentials | OLVM admin account (e.g. `admin@internal`) |
| Network | HTTPS access from Forescout appliance to OLVM Engine (port 443) |

## Authentication

The app uses **OAuth2 token authentication**. An SSO token is obtained from `/ovirt-engine/sso/oauth/token` and refreshed on a configurable interval (default 28 minutes).

## Properties

### VM Properties (14)

| Property | Tag | Type |
|---|---|---|
| VM ID | `connect_oraclekvm_vm_id` | String |
| VM Name | `connect_oraclekvm_name` | String |
| VM Status | `connect_oraclekvm_status` | String (options) |
| VM Online | `connect_oraclekvm_online` | Boolean |
| VM Type | `connect_oraclekvm_type` | String (options) |
| VM Description | `connect_oraclekvm_description` | String |
| OS Type | `connect_oraclekvm_os_type` | String |
| FQDN | `connect_oraclekvm_fqdn` | String |
| CPU Cores | `connect_oraclekvm_cpu_cores` | Integer |
| Memory (MB) | `connect_oraclekvm_memory_mb` | Integer |
| Cluster | `connect_oraclekvm_cluster` | String |
| Running Host | `connect_oraclekvm_host_affinity` | String |
| Creation Time | `connect_oraclekvm_creation_time` | Date |
| Uptime | `connect_oraclekvm_uptime` | String |

### Host Properties (12)

| Property | Tag | Type |
|---|---|---|
| Host ID | `connect_oraclekvm_host_id` | String |
| Host Name | `connect_oraclekvm_host_name` | String |
| Host Status | `connect_oraclekvm_host_status` | String (options) |
| Host Online | `connect_oraclekvm_host_online` | Boolean |
| Host Address | `connect_oraclekvm_host_address` | String |
| CPU Model | `connect_oraclekvm_host_cpu_model` | String |
| CPU Cores | `connect_oraclekvm_host_cpu_cores` | Integer |
| Memory (MB) | `connect_oraclekvm_host_memory_mb` | Integer |
| Host OS | `connect_oraclekvm_host_os` | String |
| Cluster | `connect_oraclekvm_host_cluster` | String |
| SPM Status | `connect_oraclekvm_host_spm_status` | String (options) |
| VDSM Version | `connect_oraclekvm_host_version` | String |

## Scripts

| Script | Purpose |
|---|---|
| `oraclekvm_lib.py` | Shared library (auth, HTTP, parsing helpers) |
| `oraclekvm_authorization.py` | OAuth2 SSO token acquisition |
| `oraclekvm_test.py` | Connectivity and authentication test |
| `oraclekvm_poll.py` | Discovery of VMs and hosts |
| `oraclekvm_resolve.py` | Resolve VM properties by MAC/IP |
| `oraclekvm_resolve_host.py` | Resolve host properties by MAC/IP |

## API Endpoints Used

| Endpoint | Purpose |
|---|---|
| `GET /ovirt-engine/api` | Connectivity test, version info |
| `POST /ovirt-engine/sso/oauth/token` | OAuth2 token acquisition |
| `GET /ovirt-engine/api/vms?follow=nics,reported_devices` | List VMs with inline NIC and reported-device data |
| `GET /ovirt-engine/api/hosts?follow=nics` | List hosts with inline NIC data |
| `GET /ovirt-engine/api/clusters` | Cluster name resolution |
| `GET /ovirt-engine/api/vms/{id}/reporteddevices` | VM MAC/IP fallback (if inline data missing) |
| `GET /ovirt-engine/api/vms/{id}/nics` | VM NIC definitions fallback |
| `GET /ovirt-engine/api/hosts/{id}/nics` | Host NIC fallback |

The `follow` parameter inlines sub-resources in a single API call, reducing per-VM/host requests. Individual NIC endpoints are only called as a fallback when inline data is absent.

## Configuration

1. Install the Connect App on the Forescout platform.
2. Add a new Oracle KVM connection.
3. Enter the OLVM Engine URL (e.g. `https://olvm.example.com`).
4. Enter admin credentials and auth domain.
5. Assign focal appliance(s) and optionally configure a proxy.
6. Test the connection.
7. Set discovery frequency and rate limiting in Options.

## Version History

| Version | Changes |
|---|---|
| 1.0.8 | Added license.txt to package. |
| 1.0.7 | Removed Basic Auth — OAuth2 token only. Simplified authorization flow. |
| 1.0.6 | Fixed MAC format (12-char uppercase hex, no separators) and date properties (epoch seconds). Stripped diagnostic logging. Resolve scripts use inline extraction. |
| 1.0.5 | Removed `__name__` usage (Forescout sandbox blacklist). |
| 1.0.4 | Added diagnostic logging to debug missing properties. |
| 1.0.3 | Use oVirt `follow` parameter to inline NICs/reported devices — fewer API calls. |
| 1.0.2 | Fixed single-object normalization (`ensure_list`) for oVirt single-result responses. |
| 1.0.1 | Initial packaging fixes. |
| 1.0.0 | Initial release — VM and host discovery, dual auth support. |
