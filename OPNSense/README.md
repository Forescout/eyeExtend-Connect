# OPNSense Connect App

Forescout Connect App for integrating with OPNSense firewalls.

## Overview

This Connect App provides three use cases:

### Use Case 1: Firewall Telemetry

Discovers each OPNSense firewall as an endpoint in Forescout and enriches it with real-time system telemetry. This gives the security team visibility into firewall health directly from the Forescout console.

**Properties collected:**

- Hostname, firmware version, CPU type
- Memory total and usage percentage
- Disk total and usage percentage
- System temperature, uptime
- Active PF (packet filter) state count
- Per-interface details: name, device, link status, IPv4 and IPv6 addresses

All telemetry is gathered during the poll cycle so it stays current with each discovery interval. 

### Use Case 2: ARP Table Discovery

Reads the firewall's ARP table to discover network endpoints behind it. Each ARP entry becomes a Forescout endpoint with its MAC address, IP address, and hostname (from DHCP leases). This is especially useful for discovering unmanaged devices on segments where the OPNSense firewall is the gateway.

Discovered clients are tagged with:

- **Client Hostname** — hostname from DHCP leases or DNS
- **Seen By** — hostname of the OPNSense firewall that discovered the endpoint (useful in multi-firewall deployments)

### Use Case 3: Dynamic Alias Management

Adds or removes endpoint IP addresses to/from OPNSense firewall aliases through Forescout policy actions. Since aliases are referenced by firewall rules, this enables dynamic block/allow lists driven by Forescout compliance policies.

**Example workflow:**

1. Create a "host" type alias on OPNSense (e.g., `forescout_blocked`)
2. Reference the alias in a firewall block rule
3. Create a Forescout policy that triggers the "Add to OPNSense Alias" action when a host is non-compliant
4. The "cancel action" automatically removes the IP when the host becomes compliant

## Multi-Instance Support

The app supports monitoring multiple OPNSense firewalls from a single Forescout connection using controller routing. Configure comma-separated values for the Firewall URL, API Key, API Secret, and (optionally) LAN Interface fields. Each firewall is polled independently and its endpoints are tagged with the originating firewall's URL and hostname.

## Requirements

- Forescout platform with Connect module installed
- OPNSense firewall with API access enabled
- API Key + Secret generated on the OPNSense firewall (System > Access > Users > API keys)
- API user must have privileges for:
  - Diagnostics: System Information
  - Diagnostics: ARP Table
  - Firmware (read)
  - Firewall: Alias (for the alias action)

## Installation


1. Import the `.eca` file via the Forescout Connect module
2. Configure a connection with the OPNSense firewall URL, API Key, and API Secret
3. Click **Test** to verify connectivity

## How It Works

### Discovery (Poll)

The poll script runs on the configured frequency and performs two phases:

- **Phase A — Firewall Endpoint**: Identifies the firewall's management interface (MAC + IP), creates a firewall endpoint, and populates all FW telemetry properties (firmware, CPU, memory, disk, temperature, uptime, PF states, interfaces).
- **Phase B — ARP Discovery**: Reads the ARP table and creates an endpoint for each non-expired entry with MAC, IP, hostname, and the "Seen By" tag.

### Action (Add to Alias)

The Forescout action calls the OPNSense API to add or remove an IP address from a named alias. The alias must already exist on OPNSense and be referenced by a firewall rule. The undo action reverses the operation.

## Properties

### Firewall Properties (OPNSense FW group)

| Property | Type | Description |
|----------|------|-------------|
| FW Hostname | string | Firewall hostname |
| FW Firmware Version | string | Installed firmware version |
| FW CPU Type | string | CPU model and core count |
| FW Total Memory (MB) | integer | Total physical memory |
| FW Memory Usage (%) | integer | Current memory usage percentage |
| FW Disk Total (GB) | integer | Root filesystem size |
| FW Disk Usage (%) | integer | Current disk usage percentage |
| FW Temperature | string | Temperature sensor readings |
| FW Uptime | string | System uptime string |
| FW PF State Count | integer | Active packet filter states |
| FW Interfaces | composite | Per-interface name, device, status, IPv4, IPv6 |
| FW URL | string | URL of the OPNSense firewall (set during discovery) |

### Client Properties (OPNSense Clients group)

| Property | Type | Description |
|----------|------|-------------|
| Client Hostname | string | Hostname from DHCP leases |
| Seen By | string | Hostname of the discovering OPNSense firewall |

## Files

| File | Purpose |
|------|---------|
| system.conf | UI panels, fields, multi-instance routing config |
| property.conf | Properties, actions, script mappings |
| opnsense_lib.py | Shared API library (auth, ARP, system, alias) |
| opnsense_test.py | Connection test |
| opnsense_poll.py | Firewall telemetry + ARP discovery |
| opnsense_resolve.py | On-demand firewall enrichment |
| opnsense_add_to_alias.py | Add IP to alias action |
| opnsense_add_to_alias_cancel.py | Remove IP from alias (undo) |

## Troubleshooting

- **401 errors**: Verify API Key and Secret are correct and not expired
- **403 errors**: Check the API user has required privileges
- **No ARP entries**: Ensure API user has "Diagnostics: ARP Table" privilege
- **Alias action fails with 404**: The alias must be created on OPNSense first via the web UI
- **No firewall endpoint discovered**: Check that the firewall has an interface with a gateway configured
- **FW telemetry all zeros**: Ensure the API user has Diagnostics: System Information and Firmware read privileges
