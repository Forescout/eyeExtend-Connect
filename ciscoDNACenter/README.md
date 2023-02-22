

# Forescout  
Forescout eyeExtend for Cisco DNA Center README.md


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

## About Connect APP for Cisco DNA Center

The Connect App for [Cisco DNA Center](https://www.cisco.com/site/us/en/products/networking/dna-center-platform/index.html) provides an interface for the eyeSight Platform to communicate with Cisco infrastructure.  

## App Version 1.0.0

The App performs polling of the Cisco DNA Center to discover Cisco wireless sensors.  

Additionally, eyeSight policies can be created to leverage any of the supplied properties below:

### Properties

Property                      | Type       | Description
----------------------------- | ---------- | -----------------------
`connect_ciscodna_sensor_name`| String     | Name of Cisco Wireless Sensor
`connect_ciscodna_sensor_status`| String     | Status of Cisco Wireless Sensor
`connect_ciscodna_sensor_version`| String     | Version of Cisco Wireless Sensor
`connect_ciscodna_sensor_backhaultype`| String     | Backhaul Type for Cisco Wireless Sensor
`connect_ciscodna_sensor_lastseen`| Date    | Cisco Wireless Sensor Last Seen Date
`connect_ciscodna_sensor_serialnumber`| String     | Serial Number of Cisco Wireless Sensor

### Scripts

Script        | Function
------------- | -----------------------------
ciscodna_test.py | Test Script, will return the Cisco DNA Server version
ciscodna_poll.py | Poll Script, gathers Cisco Wireless sensor information
ciscodna_func.py | Library Script, Cisco DNA functions

### Platform Requirements

The following software versions were tested:

eyeExtend Connect Plugin 1.7.2


## Configuring the Connect APP for Cisco DNA Center

There are two system panels provided with the App that must be configured.

### Cisco DNA Center Connection Panel

Below are descriptions for each field:

Field                            | Description
-------------------------------- | ------------------------------------------
Cisco DNA Center URL   | The URL of the Cisco DNA Server without port
Cisco DNA Center Connection PORT   | The port number that the Cisco DNA Center Server is using
Username                         | Cisco DNA Center API Username
Password                         | Cisco DNA Center API Password
Validate Server Certificate      | If check, eyeSight will validate the Cert


### Cisco DNA Center System Options Panel

Below are descriptions for each field:

Field                            | Description
-------------------------------- | ------------------------------------------
Enable Host Discovery            | Must be checked for polling
Discovery Frequency (Minutes)    | How often to poll Cisco DNA Center for Wireless Sensors

## Future Enhancements

If you have suggestions for future enhancements or would like to contribute, please let us know on the [Forescout Community Slack](https://forescout.slack.com/).

## Known Issues

### Refreshing Discovery of Hosts

Use the refresh button to manual poll for endpoints and VPN users.


