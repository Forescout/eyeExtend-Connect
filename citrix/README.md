

# Forescout  
Forescout eyeExtend for Citrix VPN App README.md


### Contact Information  

All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.

For questions of feedback, please send us an email below:

**[connect-app-help@forescout.com](mailto:connect-app-help@forescout.com)**

### Forescout Documentation Portal

To access Forescout documentation, please refer to [https://docs.forescout.com/](https://docs.forescout.com/)

### Legal Notice

© 2020 Forescout Technologies, Inc. All rights reserved. Forescout Technologies, Inc. is a Delaware corporation.
A list of our trademarks and patents can be found at https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks.
Other brands, products, or service names may be trademarks or service marks of their respective owners.


### Licenses
This App includes a license file. Please review the `license.txt` file included in the distribution.

## About Connect APP for Citrix VPN

The Connect App for [Citrix VPN](https://www.citrix.com/products/citrix-gateway/) provides an interface for the eyeSight Platform to communicate with the Citrix infrastructure.  

## App Version 1.0.0

The App performs polling of the Citrix ADM to discover VPN IP endpoints active in the network.  

Additionally, eyeSight policies can be created to leverage any of the supplied properties below:

### Properties

Property                      | Type       | Description
----------------------------- | ---------- | -----------------------
`connect_citrix_ns_vpnvserver_hostname`| String     | Name of the Citrix Appliance
`connect_citrix_ns_vpnvserver_description`| String     | Citrix vServer(s) Name
`connect_citrix_vpnuser`| String     | User name connected to Citrix VPN
`connect_citrix_last_poll_datetime`| date     | Timestamp of the last poll to include connected IP


### Scripts

Script        | Function
------------- | -----------------------------
citrix_test.py | Test Script, will return the Number of VPN servers
citrix_poll.py | Poll Script, gathers Endpoints and VPN users
citrix_func.py | Library Script, Citrix functions

### Platform Requirements

The following software versions were tested:

eyeExtend Connect Plugin 1.6


## Configuring the Connect APP for Citrix VPN

There are two system panels provided with the App that must be configured.

### Citrix ADM Connection Panel

Below are descriptions for each field:

Field                            | Description
-------------------------------- | ------------------------------------------
Citrix URL and credentials    | The URL of the Citrix ADM Server without port
Citrix ADM Connection PORT   | The port number that the Citrix ADM Server is using
Username                         | Citrix ADM API Username
Password                         | Citrix ADM API Password
Validate Server Certificate      | If check, eyeSight will validate the Cert


### Citrix System Options Panel

Below are descriptions for each field:

Field                            | Description
-------------------------------- | ------------------------------------------
Enable Host Discovery            | Must be checked for polling
Discovery Frequency (Minutes)    | How often to poll Citrix for endpoints and VPN Users

## Future Enhancements

If you have suggestions for future enhancements or would like to contribute, please let us know on the [Forescout Community Slack](https://forescout.slack.com/).

## Known Issues

* This app has not been tested in a multi-tenant environment.
* If you trigger a manual Discovery of hosts via the Connect module refresh options against a large SD-WAN environment the GUI may show a timeout error.  The discovery is still running and will update hosts when complete.

### Refreshing Discovery of Hosts

Use the refresh button to manual poll for endpoints and VPN users.


