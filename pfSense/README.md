Forescout eyeExtend Connect pfSense App README.md  

**About the eyeExtend Connect pfSense App**

The pfSense Connect App is used to Tag / Untag Endpoints with Aliases that are associated with Firewall policies. It also reads from pfSense DHCP Server lease assets and update property of hostname.

## **Support Requirements**
- pfSense 2.4.4 or later.
- Forescout CounterACT 8.2.2
- Forescout eyeExtend Connect 1.5
## **Features and updates with v1.0.0 pfSense App**
This version adds supports for

- Reads pfSense DHCP Lease Assets (Mac / IP / Hostname / Online).
- Tag endpoint (assign endpoint to an alias).
- Untag endpoint (remove endpoint from an alias).
### Configuration required on pfSense
- Create Alias(es) to be used as tag(s).
- Associate Alias(es) to Firewall rules / Nat Rules.
- Install pfSense API
- Authentication mode JWT
### Test button
- Test is enabled by default.
### Policy Templates
- Includes one template policy to detect assets based on assigned alias(es).
- The template checks for the example aliases “Approved” and “FS-Restricted”, which can be modified to any required Alias and as per requirements.
- The policy shows the assets that have been previously assigned to Alias and then removed, as the “pfSense Alias” value will be empty.
### Actions
- Tag endpoint (assign endpoint to an alias).
- Up Untag endpoint (remove endpoint from an alias).







