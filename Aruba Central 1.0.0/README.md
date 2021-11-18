Forescout eyeExtend Connect Aruba Central APP README.md
 

## Contact Information

- Have feedback or questions? Write to us at

        **[connect-app-help@forescout.com](mailto:connect-app-help@forescout.com)**

## APP Support

- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.

## About the eyeExtend Connect Aruba Central APP

- Originally when the Aruba Central App was developed, the API rate limit for Aruba Central was 1 million per day.  Now the limit has been reduced to 1000 per day. This means the Aruba Central App will now not function as intended.  

- WARNING:  Please contact Aruba support to change default API limits  before using this App.

### Version v1.0.0 Aruba Central APP

The APP gathers <mark>Wireless AP</mark>, <mark>Endpoint (Clients) Wired / Wireless</mark> information, allowing you to build Forescout policies relating to the Aruba Central

- Make sure '**Host Discovery**' *flag* is enabled **Recommended**

## Requirements

- Access to Aruba Central

- Forescout CounterACT 8.2, 8.1.4

- Forescout eyeExtend Connect 1.5 or higher

- See license.txt file for license information

  ## User Interface

  You can refer to the Forescout eyeExtend Connect Module: Connect Application Building Guide, in particular the
  sections on ”Define system.conf File” and “User Interface Details”.

#### Predefined fields used panels

- Certification validation
- Authorization
- Rate limiter

##### Rate-limited API Count

- User can set rate-limiter for the API allowed to the Aruba Central per second.
  - Default in the APP is allowing up to 100 API calls per second.
  - Range is 1 to 1000 APIs.

### Panels

#### Aruba Central Connection

Aruba Central Authentication credentials.

Credentials are created via Aruba Central

> Account Home**/**API Gateway**/**System APPs and Tokens

| Property| Comment|
| :------------------------------- | :-------------------------------- |
| Client ID          | *Copy from Aruba Central* |
| API Domain Gateway | Example : apigw-prod2.central.arubanetworks.com<br>**No HTTPS prefix required** |
| Client Secret      | *Copy from Aruba Central* |
| Username           | Aruba Central Username |
| Password           |  |
| Validate Certificate | Check to validate the HTTPS certificate |


### Aruba Central Options

| Property                       | Comment|
|:------------------------------ |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Enable Host Discovery          | **Required and should be checked**                                                                                                                                                |
| Discovery Frequency (Minutes) | Default **45**<br>How often to do a full poll of Aruba Central                                                                                               |
| Authorization (Minutes)        | Default **115**<br />How often to update the bearer token                                                                                                            |
| Discover Access Points | Poll for access points |
| Discover Wireless Clients | Poll for wireless connected clients |
| Discover Wired Clients | Poll for wired connected clients |
| Poll Pagination Limit | Default **100**<br />Example 1000 entries would require 10 queries to retrieve all the data. |
| Number of API queries per second | See<br />**Rate-limited API Count above** |

#### Focal appliance

Each "API Domain Gateway" shall run on one dedicated focal appliance.

### Proxy Server

Used to define proxy settings.

### Test button

- Test is enabled by default.
- Device info need to be saved (applied) before test can be successfully run.

Example Test Result

```
Test succeeded:
Successfully connected. No of Sites 1
```

## Manage the APP

### Import

- User can import the Aruba Central Connect APP via eyeExtend Connect module

- APP file shall look similar to **Forescout-arubacentral.eca** which is signed

  ## Start and Stop APP

- User can start and stop the Aruba Central App

- When the APP is stopped, all properties resolve, actions and policy are suspended.

  ### Remove APP

- User can remove the APP if no longer needed

- User need to delete the Aruba Central policy first to remove the App.

  ## Policy Templates

- There is 3 default Aruba Central Templates

- After importing the App. The policies can be found under Policy > Add > Aruba Central >

  ​	*Aruba Central Access Point Status (UP/DOWN)*

  ​	*Aruba Central Access Point Firmware Level*

  ​	*Aruba Central Client Wireless by Radio GHz*

  ## Actions

  <mark>NONE</mark>

  ## Properties

  Properties gathered from the Aruba Central.

  **Access Points**

<mark>Common Properties across ALL (AP / Wired / Wireless)</mark>

- Aruba Central Group Name
- Aruba Central AP Serial No.
- Aruba Central AP Site

<mark>Access Point</mark>
- Aruba Central AP Deployment Mode
- Aruba Central AP Group
- Aruba Central AP Cluster ID
- Aruba Central AP Firmware Version
- Aruba Central AP Labels
- Aruba Central AP Last Modified
- Aruba Central AP Mesh Role
- Aruba Central AP Model
- Aruba Central AP Name
- Aruba Central AP Public IP Address
- Aruba Central AP Radios
  - AP Radio Band
  - AP Radio Index
  - AP Radio MAC Address
  - AP Radio Status
- Aruba Central AP Status
- Aruba Central AP Subnet Mask
- Aruba Central AP Swarm ID
- Aruba Central AP Swarm Master

<mark>Wireless</mark>
- Aruba Central Client Wireless Band
- Aruba Central Client Wireless Channel
- Aruba Central Client Wireless Connection
- Aruba Central Client Wireless Encryption Method
- Aruba Central Client Wireless Group ID
- Aruba Central Client Wireless Health
- Aruba Central Client Wireless HT Type
- Aruba Central Client Wireless Associated Device MAC
- Aruba Central Client Wireless Manufacturer
- Aruba Central Client Wireless Maxspeed
- Aruba Central Client Wireless Name
- Aruba Central Client Wireless Network
- Aruba Central Client Wireless OS Type
- Aruba Central Client Wireless PHY Type
- Aruba Central Client Wireless Radio MAC
- Aruba Central Client Wireless Radio Number
- Aruba Central Client Wireless SNR
- Aruba Central Client Wireless Speed
- Aruba Central Client Wireless Swarm ID
- Aruba Central Client Wireless Username
- Aruba Central Client Wireless VLAN

<mark>Wired</mark>

- Aruba Central Client Wired Associated Device MAC Address
- Aruba Central Client Wired Group ID
- Aruba Central Client Wired Interface MAC Address
- Aruba Central Client Wired Interface Port
- Aruba Central Client Wired Manufacturer
- Aruba Central Client Wired Name
- Aruba Central Client Wired OS Type
- Aruba Central Client Wired Swarm ID
- Aruba Central Client Wired Username
- Aruba Central Client Wired VLAN


## Scripts

* Authorization used to get / updated the bearer token
  **arubacentral_authorization.py**

* Discovery used to poll for full discovery of AP / Wireless / Wired.
  **arubacentral_poll.py**

  <mark>Aruba Central Options TAB (Discover AP / Wireless / Wired check boxes, effects this poll)</mark>

* Resolve scripts for AP / Wireless / Wired

  **arubacentral_ap_resolve.py**

  **arubacentral_wired_resolve.py**

  **arubacentral_wireless_resolve.py**

* Test authentication to Aruba Central
  **arubacentral_test.py**

## Inventory

A lot of the properties are available in the Inventory TAB.

I would like to explain what I mean my common properties (from above properties details)

- Aruba Central Group Name
- Aruba Central AP Serial No.
- Aruba Central AP Site

The above are common across the various types of Aruba Central assets (Access Point / Wireless / Wired)
For example when you select the "AP Serial No." property, you will see every asset(s) associated with that *access point*.

Same for "AP Site" and "Group Name"

There are properties that will not group, because they are only associated with a particular type. i.e
Wireless property "Aruba Central Client Wireless Channel", it has nothing in common with Wired asset(s).

## Notes
