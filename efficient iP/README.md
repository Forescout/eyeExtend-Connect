# efficientiP
eyeExtend Connect App for efficientiP - Get EfficientIP IPAM and DHCP context for Forescout discovered devices

## Versions
1.0.0

## Configurations
### Connection
IP or FQDN and port along with username and password to with the permissions are required. Once configured leverage the test function to ensure a connection has been established.
### Polling Options
Check the enable Host discovery box along with the polling period. This will determine how often the App will attempt to discover new endpoints from efficientiP instance

## Supported Use Cases
* Discover IP endpoints from efficientiP
* Learn endpoint context from efficientiP following new properties supported
  * EfficientIP IPAM Company
  * EfficientIP IPAM Class
  * EfficientIP IPAM Parent Network
  * EfficientIP IPAM Network
  * EfficientIP IPAM Name
  * EfficientIP IPAM Mac Address
  * EfficientIP IPAM Company Path
  * EfficientIP IPAM Pool
  * EfficientIP DHCP Scope
  * EfficientIP DHCP Server
  * EfficientIP DHCP Version
  * EfficientIP DHCP Type


* Policy template to to add EfficientIP's IPAM and DHCP Device Context as well as verify device's presence into EfficientIP IPAM
