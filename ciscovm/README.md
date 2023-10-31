# Cisco Vulnerability Management (Cisco VM) App

### About the App
The app exports endpoints' data to Cisco Vulnerability Management.

#### Versions
- 1.0.0 - base release

#### Contact Information
Forescout Technologies, Inc. 190 West Tasman Drive San Jose, CA 95134 USA https://www.Forescout.com/support/ Toll-Free (US): 1.866.377.8771 Tel (Intl): 1.408.213.3191 Support: 1.708.237.6591

#### About the Documentation
Refer to the Technical Documentation page on the Forescout website for additional documentation: https://www.Forescout.com/company/technical-documentation/
Have feedback or questions? Write to us at documentation@forescout.com

#### Legal Notice
© 2020 Forescout Technologies, Inc. All rights reserved. Forescout Technologies, Inc. is a Delaware corporation. A list of our trademarks and patents can be found at https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks. Other brands, products, or service names may be trademarks or service marks of their respective owners.

#### Requirements
The App supports:
- ForeScout CounterACT 8.4
- ForeScout eyeExtend Connect 2.0.15
- ForeScout Connect Plugin 1.7.4

#### Licenses
This App includes a license file. Please review the `license.txt` file included in the distribution.

### How it works
Forescout Cisco VM App exports endpoints' data to Cisco Vulnerability Management REST API.
The app contains Policy template that controls the export process by applying Export or Reset actions.

#### Export flow
1. By default, the policy exports data only for new endpoints or endpoints that were changed from the last export. 
By default, the recheck for the changed endpoints happens every day at 12 AM (Forescout Appliance time zone).  
2. If export for an endpoint fails, the app retries an export in 10 minutes. If the export fails again, the app attempts to reexport every 2 hours.
3. In case the endpoint doesn't have any changes for the exported properties for 1 month, it's reexported.
4. Endpoints that have Exported and Unchanged state are also following a daily recheck schedule. They are not moved to the Pending state before the recheck to avoid redundant execution of the Reset action.

#### Exported properties mapping
Forescout        | Cisco Vulnerability Management
------------- | -----------------------------
MAC Address | MAC Address
DHCP Hostname | Hostname
IPv4 Address | IP Address
NetBIOS Host name | NetBIOS
DNS Name | FQDN
Operating System | Operating System
Segment path | "FS Segment path" tag
Function | "FS Function" tag
Vendor and Model | "FS Vendor and Model" tag
NIC Vendor | "FS NIC Vendor" tag

#### Properties
Property        | Description
------------- | -----------------------------
Cisco VM Exported State | Defines the state of the latest export (Pending, Failed, Exported, Unchanged)
Cisco VM Exported Hash | Hash of the latest exported payload

### Configuration
Before starting the configuration process, Forescout connector must be created in Cisco Vulnerability Management UI.
The connector generates configuration parameters that are required to configure Cisco VM eyeExtend Connect app.

#### Configure App
Parameters required during the configuration process:
* URL - URL of Cisco VM Webhook which saves the exported data to Cisco VM environment
* UID - a unique identifier defined per client per connector
* AUTH Token - Token for Cisco VM REST API

#### Apply policy
The policy must be added manually after the app is imported and configured.
1. Go to ForeScout Policy tab -> Add -> "Cisco VM" policy template group -> "Cisco VM Export" template
2. Follow configuration instructions. The user must set IP range of endpoints that should be exported. Other configuration steps are optional as the template includes default configuration. 