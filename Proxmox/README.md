# Proxmox Connect App for Forescout

## Overview

This Connect App integrates Proxmox VE v9 with the Forescout platform, discovering all virtual machines (QEMU), LXC containers, and PVE hypervisor hosts from a Proxmox cluster. Discovered endpoints are created in Forescout with their MAC and IP addresses mapped to core properties, and Proxmox-specific metadata exposed as custom properties.

Version 2 adds 8 actions for power management, snapshotting, and tagging — all with policy-driven undo support. Version 3 adds PVE host node discovery with hardware, OS, and update status properties.

## Requirements

- Forescout platform with Connect module installed
- Proxmox VE v9 (or compatible) with API access enabled
- A Proxmox API Token with the required privileges:
  - **Discovery only:** `PVEAuditor` role (read-only)
  - **With PVE update checks:** `PVEAuditor` + `Sys.Modify` (for `/nodes/{node}/apt/update`)
  - **With actions:** `PVEAuditor` + `VM.PowerMgmt` + `VM.Snapshot` + `VM.Config.Options`
  ```
  pveum aclmod / -token 'USER@REALM!TOKENID' -role PVEAuditor
  pveum aclmod / -token 'USER@REALM!TOKENID' -role PVEAdmin
  ```
  Alternatively, create the token with **Privilege Separation disabled** under an account that already has the needed permissions.
- Network connectivity from the Forescout appliance to the Proxmox API (default port 8006)

## Installation


1. In the Forescout Console, go to **Options > Connect > Import** and select the `.eca` file.
2. Configure the connection in the **Proxmox Connection** panel:
   - **Server URL**: Base URL of your Proxmox server (e.g. `https://192.168.1.3:8006`)
   - **API Token ID**: Full token ID in the format `USER@REALM!TOKENID` (e.g. `root@pam!forescout`)
   - **API Token Secret**: The UUID secret generated when the token was created
3. Assign a focal appliance in the **Assign CounterACT Devices** panel.
4. Configure discovery frequency and rate limiting in the **Proxmox Options** panel.
5. Click **Test** to verify connectivity, then **Apply**.

## How It Works

### Guest Discovery (Poll)

The poll script runs on the configured discovery interval and:

1. Calls `GET /api2/json/cluster/resources?type=vm` to get all VMs and LXC containers across the cluster.
2. For each guest, fetches the config to extract the MAC address from `net0` and the OS type.
3. For running guests, fetches live IP addresses from the QEMU guest agent or LXC interfaces endpoint. For stopped guests with static IPs configured, parses the IP from the config.
4. For running QEMU VMs, fetches detailed OS information from the guest agent.
5. Returns endpoints with MAC mapped to Forescout core `$mac` and IP to core `$ip`.
6. Sets `$online = true` for running guests and `$online = false` for stopped/paused/suspended guests.

### PVE Host Discovery (Poll)

The same poll script also discovers PVE hypervisor nodes:

1. Calls `GET /api2/json/cluster/resources?type=node` to get all cluster nodes.
2. For each node, fetches detailed status (`/nodes/{node}/status`) for CPU model, kernel version, and PVE version.
3. Fetches network interfaces (`/nodes/{node}/network`) to identify the management interface MAC and IP.
4. Checks for pending package updates (`/nodes/{node}/apt/update`) — requires `Sys.Modify` privilege; gracefully skips if denied.
5. Returns PVE host endpoints in the same discovery response as guest endpoints.

### Property Resolution (Resolve)

Two resolve scripts handle the different endpoint types:
- **proxmox_resolve.py** — matches by MAC or IP against Proxmox guests and returns guest properties.
- **proxmox_resolve_node.py** — matches by MAC or IP against PVE nodes and returns host properties.

## Properties

### Guest Properties (Proxmox group)

| Property | Type | Description |
|----------|------|-------------|
| Proxmox VM ID | integer | Proxmox VMID number |
| Proxmox Guest Hostname | string | VM or container name |
| Proxmox Node | string | Cluster node hosting the guest |
| Proxmox Status | string | running, stopped, paused, or suspended |
| Proxmox Guest Type | string | qemu (VM) or lxc (Container) |
| Proxmox OS Type | string | Proxmox config ostype (e.g. l26, win11, ubuntu) |
| Proxmox Guest OS | string | Detailed OS from guest agent (e.g. "Ubuntu 22.04.3 LTS") |
| Proxmox CPU Cores | integer | Number of allocated vCPUs |
| Proxmox Guest Memory (MB) | integer | Allocated memory in megabytes |
| Proxmox Guest Disk Size (GB) | integer | Allocated disk in gigabytes |
| Proxmox Uptime (seconds) | integer | Guest uptime |
| Proxmox Tags | string | Proxmox tags |
| Proxmox Template | boolean | Whether the guest is a template |
| Proxmox Description | string | Guest description from config |
| Proxmox QEMU Guest Agent Installed | boolean | Whether the QEMU guest agent is responding |

### PVE Host Properties (Proxmox PVE Host group)

| Property | Type | Description |
|----------|------|-------------|
| Proxmox PVE Hostname | string | PVE node hostname |
| Proxmox PVE Status | string | online, offline, or unknown |
| Proxmox PVE CPU Model | string | CPU model name (e.g. "Intel Core i7-12700") |
| Proxmox PVE CPU Cores | integer | Total CPU cores (cores x sockets) |
| Proxmox PVE CPU Sockets | integer | Number of CPU sockets |
| Proxmox PVE Total Memory (GB) | integer | Total system RAM in gigabytes |
| Proxmox PVE Root Disk (GB) | integer | Root filesystem size in gigabytes |
| Proxmox PVE Kernel Version | string | Linux kernel version |
| Proxmox PVE Version | string | Proxmox VE software version |
| Proxmox PVE Uptime (seconds) | integer | Node uptime |
| Proxmox PVE Updates Available | boolean | Whether package updates are pending |

## Actions

| Action | Description | Undo | Notes |
|--------|-------------|------|-------|
| Start VM/Container | Start a stopped guest | Stop | |
| Stop VM/Container | Force stop (immediate power off) | Start | |
| Shutdown VM/Container | Graceful ACPI shutdown | — | Requires guest agent for VMs |
| Reboot VM/Container | Graceful reboot | — | |
| Suspend VM | Pause execution, preserve state | Resume | QEMU VMs only |
| Resume VM | Resume a suspended VM | Suspend | QEMU VMs only |
| Create Snapshot | Point-in-time snapshot | — | Params: name, description |
| Set Tags | Set tags on a guest | Restore previous tags | Replaces all existing tags |

### Action Permissions

Actions require additional Proxmox API token privileges beyond the read-only `PVEAuditor` role:

| Action | Required Privilege |
|--------|--------------------|
| Start, Stop, Shutdown, Reboot, Suspend, Resume | `VM.PowerMgmt` |
| Create Snapshot | `VM.Snapshot` |
| Set Tags | `VM.Config.Options` |



## Files

| File | Purpose |
|------|---------|
| system.conf | Connection UI panels and settings |
| property.conf | Property definitions, actions, groups, and script mappings |
| proxmox_lib.py | Shared library (auth, HTTP, MAC/IP parsing, action helpers) |
| proxmox_test.py | Connectivity test via Proxmox version endpoint |
| proxmox_poll.py | Discovery script - enumerates all VMs, LXCs, and PVE hosts |
| proxmox_resolve.py | Per-host guest property resolution |
| proxmox_resolve_node.py | Per-host PVE node property resolution |
| proxmox_start.py | Start action |
| proxmox_start_cancel.py | Cancel start (stop) |
| proxmox_stop.py | Stop action |
| proxmox_stop_cancel.py | Cancel stop (start) |
| proxmox_shutdown.py | Graceful shutdown action |
| proxmox_reboot.py | Reboot action |
| proxmox_suspend.py | Suspend action (QEMU only) |
| proxmox_suspend_cancel.py | Cancel suspend (resume) |
| proxmox_resume.py | Resume action (QEMU only) |
| proxmox_resume_cancel.py | Cancel resume (suspend) |
| proxmox_snapshot.py | Create snapshot action |
| proxmox_set_tags.py | Set tags action |
| proxmox_set_tags_cancel.py | Cancel set tags (restore previous) |

## Troubleshooting

**Test succeeds but no endpoints discovered:**
The API token likely has Privilege Separation enabled and lacks permissions. Grant `PVEAuditor` role or recreate the token with Privilege Separation disabled.

**Actions fail with HTTP 403:**
The API token needs additional privileges for actions. Grant the required privileges listed in the Action Permissions table above, or assign the `PVEAdmin` role.

**Suspend/Resume fails on LXC container:**
Suspend and Resume are only supported for QEMU VMs. LXC containers do not support suspend/resume.

**No IP addresses for stopped guests:**
Only guests with static IPs configured in Proxmox will show IP addresses when stopped. DHCP guests require the guest agent (VMs) or running state (LXCs) to report their IP.

**No Guest OS property:**
The Guest OS field requires the QEMU guest agent to be installed and running inside the VM. LXC containers do not support this field. The OS Type field (from Proxmox config) is always available.

**PVE host not discovered:**
The node's management interface MAC and IP are read from `/nodes/{node}/network`. If the management bridge (typically `vmbr0`) or its physical port doesn't have a standard configuration, the node may be skipped. Check the Forescout Connect logs for details.

**PVE Updates Available always false:**
The `Proxmox PVE Updates Available` property requires `Sys.Modify` privilege on the API token. If the token only has `Sys.Audit`, the updates check gracefully returns false. Grant `Sys.Modify` or run `apt update` manually on the PVE host for accurate results.

**Log location:**
```
/usr/local/forescout/plugin/connect_module/python_logs/python_server.log
```
