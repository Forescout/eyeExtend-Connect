# NetBox Connect App 0.3.0

eyeExtend Connect App that looks every endpoint up in [NetBox](https://netboxlabs.com/oss/netbox/) and tells Forescout whether it is recorded in the IP address plan (IPAM), together with what NetBox knows about it.

Status: 0.1.0 was imported into a Forescout 9.1.6 Console: the Test button, property resolution (also for endpoints without a MAC) and the policy work. 0.3.0 is imported in the same Console; the extra IPAM properties show in the endpoint profile. The Add to NetBox action (0.2) is tested with scripts against NetBox 4.7.2 only.

Troubleshooting: properties Irresolvable but no request in the Connect logs means the endpoint's network is not assigned to any appliance (Options > IP Assignment). "Name or service not known" means the appliance cannot resolve the NetBox host name; check its DNS forwarders, since public resolvers do not know internal names.

## What it resolves

| Property | Content |
|---|---|
| NetBox Status | `documented`, `other_ip`, `mac_mismatch`, `not_found_private_mac` or `not_found` |
| NetBox IPAM Summary | One line: address, status, DNS name, device, description, prefix and VLAN. Only set when NetBox has a record for the endpoint |
| NetBox IP Address, IP Status, IP Role, VRF, DNS Name, MAC Address, Description, Comments, Tenant, Tags, Last Updated, Record URL | From the IP address record (MAC from the assigned interface or the record's text) |
| NetBox Interface, Device, Device Role, Device Status, Device Type, Platform, Serial Number, Asset Tag, Site, Location | From the interface, device or virtual machine the address is assigned to |
| NetBox Prefix, Prefix Description, VLAN | The most specific prefix that contains the address, and its VLAN |
| NetBox IP Range | The IP range that holds the address (for example a DHCP pool), with its role |

Properties are only set when NetBox has the data. The summary, the address record fields and the device inventory fields are shown in the device profile of the Asset Portal; IP Status, Device Type, Platform and IP Range also have an Inventory view.

How the status is decided:

- **documented**: the IP address has a record (not `deprecated`), and the endpoint's MAC matches when NetBox has a MAC for it.
- **mac_mismatch**: the IP address has a record, but for a different MAC.
- **other_ip**: no record for the IP address, but the MAC is recorded elsewhere.
- **not_found_private_mac**: no record, and the MAC is a private (locally administered) address, typical of phones and laptops on Wi-Fi.
- **not_found**: no record.

MAC addresses come from the interface the address is assigned to (NetBox 4.2+ MAC address objects and the older interface field) and, optionally, from MAC addresses written in the description or comments of the IP address record.

## Action

**Add to NetBox** (right-click an endpoint > NetBox, or use it in a policy): creates the IP address record with the mask of the prefix it belongs to, the chosen status (default `active`) and a description that ends with the endpoint's MAC. It refuses when the address is already recorded. It needs a write-enabled token whose user may add IP addresses; everything else works with a read-only token. Recheck the endpoint afterwards to refresh NetBox Status. The Actions column shows the result: a blue plus when the record was created, an amber icon while it runs and a red exclamation mark when it failed, with the reason in the tooltip.

## Policy template

**NetBox IPAM Check** (Policy > Add > NetBox): one sub-rule per status, no actions.

## Configuration

1. In NetBox, create a user with view permission on IPAM, DCIM, Virtualization and Tenancy, and an API token for it (read-only).
2. Import `Forescout-eca-netbox-0.3.0.eca` in **Options > Connect > Import**. The package is unsigned.
3. Add a NetBox server: URL (without `/api`), API token, certificate validation, connecting appliance.
4. Run **Test**, then add the policy from the template.

## Support boundary

This is a community Connect App. Apps published in Forescout's public `eyeExtend-Connect` repository are community supported and are not covered by Forescout Customer Support.
