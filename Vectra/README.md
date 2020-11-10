# Vectra
eyeExtend Connect App for Vectra - Gain visibility of threats discovered by Vectra on the Forescout Platform

## Versions
1.0.0

## Configurations
### Connection
IP or FQDN for Vectra brain and the API token are required to establish a connection. Once configured leverage the test function to ensure a connection has been established.
### Polling Options
Check the enable Host discovery box along with the polling period. This will determine how often the App will attempt to discover new endpoints from Vectra

## Supported Use Cases
* Discover endpoints from Vectra
* Learn endpoint context from Vectra following new properties supported
  * Vectra IP
  * Vectra Threat Score
  * Vectra Certainty Score
  * Vectra Tags
  * Vectra Sensor
  * Vectra Sensor Name
  * Vectra Severity
  * Vectra User ID
  * Vectra State
  * Inventory of Vectra Detection List: Category, Type, Threat and Certainty

* Policy template to categorize based on threat severity level of device detected by Vectra
