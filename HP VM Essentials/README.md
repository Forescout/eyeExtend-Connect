# HP VME Connect App

Integrates HPE VM Essentials (Morpheus) with Forescout. The app discovers VMs and hypervisor hosts as endpoints, adds their properties for use in policies, and lets policies control VMs.

This app was built against VM Essentials 9.1.0.2.

## Requirements

- Forescout with the Connect module.
- HTTPS access from the connecting Forescout appliance to each manager
- A VM Essentials user for each manager. Use a dedicated service account. Its role must allow the actions you plan to use.

## Installation

1. In Forescout, go to **Options > Connect** and import `ForeScout-eca-hpvme-1.0.1.eca`.
2. Add a system and enter the **Manager URL**, **Username**, and **Password**.
3. Leave certificate validation on if the manager has a trusted certificate. Turn it off for a self-signed lab manager.
4. Assign the connecting CounterACT device, and a proxy if you use one.
5. Click **Test**. It reports the manager's version and how many hosts and VMs it can see.

**More than one manager:** add each manager as a separate entry in the GUI. One manager can already handle several clusters.

## How it works

- **Login:** the app logs in with the username and password each time a script runs. Tokens from this login last about 30 days, so the app stores none.
- **Discovery:** runs every 10 minutes by default. VMs appear once per NIC, by MAC and IP. A host appears once, by the NIC holding its management IP. Host `vnet*` NICs mirror VM NICs and are ignored.
- **Online status:** follows the power state, so stopped and suspended VMs show as offline.
- **Resolve:** refreshes one endpoint using the server ID stored by discovery. Endpoints that discovery never found cost no API calls.

## Actions

| Action | What it does | Undo |
|---|---|---|
| Start VM | Start a stopped or suspended VM (also resumes a suspended VM) | Restore original power state |
| Stop VM (Graceful) | Gracefully shut down the VM. If the guest does not stop within five minutes, the VM stays running | Restore original power state |
| Force Power Off VM | Immediately power off the VM without a guest shutdown. Unsaved data in the VM can be lost | Restore original power state |
| Restart VM | Restart the VM | None |
| Suspend VM | Suspend the VM, keeping its memory state, without shutting down the guest OS | Restore original power state |
| Create Forensic Snapshot | Request a point-in-time snapshot of the VM, for example before containing it | None |
| Lock VM | Lock the VM so it cannot be deleted until an operator unlocks it in HP VME | None (manual unlock required) |
| Add or Remove Tag | Add or remove one tag on the VM | Restore Tag |

Actions apply only to VMs managed as instances. The app refuses them in these cases:

- **Hypervisor hosts:** all actions are refused.
- **Discovered VMs:** all actions are refused, because they have no instance record.
- **The manager's own VM:** Stop, Force Power Off, Restart, and Suspend are refused if any VM in the instance is the manager, even when a non-manager sibling is selected.
- **Missing or stale routing:** an unmatched manager route is always refused. A missing route is allowed only when exactly one manager is configured.
- **Unsafe power transitions:** Stop and Force Power Off refuse suspended VMs, because powering them off loses their saved memory state. Start them first. Suspend refuses powered-off VMs.
- **Mixed or unknown power states:** reversible power actions require every VM in the instance to have the same known power state.

### Before you use actions in a policy

- **Success means the request was accepted.** The next discovery shows the actual power state. A graceful stop waits up to five minutes and leaves the VM running if the guest does not stop.
- **Power undo uses a stored action cookie.** Actions already in the requested state do nothing, and their undo also does nothing. Otherwise undo restores the original state only for the same manager, server, and instance membership, with a live state consistent with the action. Missing or invalid cookies fail without issuing a power request; old actions without cookies cannot be automatically undone.
- **Lock undo is deliberately disabled.** The Morpheus 9.1 lock/unlock API exposes neither a lock-owner token nor a conditional unlock. A second read cannot prove ownership, so automatic undo could release another actor's lock. Unlock manually in HP VME. Legacy Lock undo requests fail explicitly rather than unlocking.
- **Stop and start loops are possible.** A stopped VM goes offline, which may take it out of the policy. If that triggers the undo, the VM starts again. Test on a disposable VM first.
- **Multi-VM instances:** actions apply to the whole instance, so every VM in it is affected.
- **Other critical VMs:** the app only protects the manager. Scope policies so they cannot match Forescout or other critical VMs.

## Properties

### VM

| Property | Type | Description |
|---|---|---|
| HP VME Server ID | integer | Server ID of this VM or host, unique within one manager |
| HP VME Endpoint Type | string | Whether this endpoint is a VM or a hypervisor host |
| HP VME VM Name | string | VM name |
| HP VME VM Power State | string | Power state of the VM. This is the reliable state to use in policies |
| HP VME Instance ID | integer | Instance ID. Discovered VMs have none |
| HP VME Instance Status | string | Instance status. This can change briefly during power operations, so prefer Power State |
| HP VME Managed VM | boolean | True if the VM is managed by HP VME, false if it was discovered |
| HP VME Is Manager VM | boolean | True if this VM is the HP VME manager itself |
| HP VME VM OS | string | Operating system |
| HP VME VM OS Type | string | Operating system type, such as linux |
| HP VME VM Cloud | string | Cloud |
| HP VME VM Group | string | Group. Discovered VMs have none |
| HP VME VM Cluster | string | Cluster. Discovered VMs have none |
| HP VME VM Host | string | Hypervisor host running this VM |
| HP VME VM Plan | string | Service plan |
| HP VME VM CPU Cores | integer | Number of CPU cores |
| HP VME VM Memory (MB) | integer | Assigned memory in MB |
| HP VME VM Storage (GB) | integer | Assigned storage in GB |
| HP VME VM Networks | string | Networks the VM's NICs are attached to |
| HP VME VM Tags | string | Tags, written as name=value and separated by semicolons |
| HP VME VM Labels | string | Labels, separated by commas |
| HP VME VM Agent Installed | boolean | True if the HP VME agent is installed |
| HP VME VM Agent Version | string | HP VME agent version |
| HP VME VM Guest Agent Status | string | Guest agent status, such as connected |
| HP VME VM Locked | boolean | True if the VM is locked against deletion |
| HP VME VM Owner | string | Owner username |
| HP VME VM Environment | string | Environment, such as production |
| HP VME VM Created | date | When the VM was created |

### Host

| Property | Type | Description |
|---|---|---|
| HP VME Host Name | string | Hypervisor host name |
| HP VME Host Power State | string | Power state of the host |
| HP VME Host Status | string | Host status, such as provisioned |
| HP VME Host Type | string | Host type, such as HVM Hypervisor |
| HP VME Host OS | string | Host operating system and version |
| HP VME Host Cluster | string | Cluster this host belongs to |
| HP VME Host Cloud | string | Cloud this host belongs to |
| HP VME Host Hardware | string | Hardware vendor and product |
| HP VME Host CPU Model | string | CPU model |
| HP VME Host CPU Cores | integer | Number of CPU cores |
| HP VME Host CPU Sockets | integer | Number of CPU sockets |
| HP VME Host CPU Usage (%) | integer | CPU usage percentage at the last update |
| HP VME Host Memory (GB) | integer | Total memory in GB |
| HP VME Host Memory Used (GB) | integer | Used memory in GB at the last update |
| HP VME Host Storage (GB) | integer | Total storage in GB |
| HP VME Host Storage Used (GB) | integer | Used storage in GB at the last update |
| HP VME Host VM Count | integer | Number of VMs on this host |
| HP VME Host Agent Installed | boolean | True if the HP VME agent is installed |
| HP VME Host Agent Version | string | HP VME agent version |
| HP VME Host Maintenance Mode | boolean | True if the host is in maintenance mode |

Use **Power State** rather than **Instance Status** in policies. Instance status was seen flipping between stopped and running while a VM was powered off.

## Files

| File | Purpose |
|---|---|
| `system.conf` | Connection settings shown in the Connect GUI |
| `property.conf` | Properties, actions, and script mappings |
| `hpvme_lib.py` | Shared API, mapping, and safety code |
| `hpvme_test.py` | The Test button |
| `hpvme_poll.py` | Discovery |
| `hpvme_resolve.py` | Per-endpoint property refresh |
| `hpvme_<action>.py` | One script per action |
| `hpvme_<action>_cancel.py` | Undo for an action |
| `images/` | Icons, using the Morpheus symbol |

## Troubleshooting

Logs are in `/usr/local/forescout/plugin/connect_module/python_logs/python_server.log`.

| Symptom | Likely cause |
|---|---|
| Login failed | Wrong username or password |
| TLS certificate validation failed | Self-signed certificate with validation turned on |
| HTTP 403 on an action | The user's role lacks that permission |
| Action refused: discovered VM | No instance association was found, including in the live instance inventory |
| Action refused: no server ID | Discovery has not found the endpoint yet |
| Power state looks out of date | It updates at the next discovery or property refresh |

## Development validation

Run the focused offline regression tests from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The tests require `requests`, the same dependency as the app. They mock API calls and do not contact a manager.
