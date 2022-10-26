Forescout eyeExtend Connect Pulse Secure App README.md
Version: 1.0.4

## Contact Information

Have feedback or questions? Write to us at

**[connect-app-help@forescout.com](mailto:connect-app-help@forescout.com)**

## About the Documentation
- Refer to the Technical Documentation page on the Forescout website for additional documentation:
https://docs.forescout.com/

## About the eyeExtend Connect Pulse Secure App
The App gathers user and endpoint information that connect to Pulse Secure servers through discovery and resolve. User can also use policies or actions to disconnect sessions from the Pulse Secure Server. The App uses the admin console via REST APIs to access the Pulse Secure server.

## Requirements
The App supports:
- Pulse Connect Secure 9.1.8 - 9.1.12
- Forescout CounterACT 8.2.2 or higher
- Forescout eyeExtend Connect 2.0 or higher
- See license.txt file for license information

## Updates

### Version 1.0.4 
This update overwrites default active user sessions of 200 to 2500. 

### Version 1.0.3 
This update introduces Realm-based Authentication Support with backward compatibility for basic Auth. This version introduces a new Panel field named "Admin Realm" which could be populated with the Admin realm to be used for Realm-based Authentication and if left empty, original basic Auth will be used. 

### Version 1.0.2
This update introduces syslog functionality to speed up discovery of devices connecting via the Pulse Secure VPN. A new panel is included for syslog source configuration.

## User Interface
You can refer to the Forescout eyeExtend Connect Module: Connect Application Building Guide, in particular the
sections on ”Define system.conf File” and “User Interface Details”.
### Panels
#### Device
User can add Pulse Secure server to the App.
- Server name: Pulse Secure server hostname or IP address. Do not include the protocol (http://, https://, etc.)
- User: Admin that can access the Pulse Secure API via admin console.
- Password: Admin password that can be used to get the API key for API calls to the Pulse Secure server.
- Admin Realm: (New in version 1.0.3) Admin Realm name to be used (or leave empty to use Basic Auth)
- User can test the device by clicking the TEST button after applying changes.

#### Focal Appliance
Each device shall run on one dedicated focal appliance.

#### Proxy Server
- User can connect to the Pulse Secure server via proxy server.
- Fields
    - Proxy Server
    - Proxy Server Port
    - Proxy Server Username
    - Proxy Server Password
- Proxy server username and password are not required and may be left blank for proxy servers that don't require authentication.

#### Syslog Source
- Optionally enable using Syslog received from Pulse Secure
- Specify the Source Name or IP to receive Syslog events from. Only 1 source may be configured per Pulse Secure server.
	- Syslog messages should be for "VPN Tunneling: Session started" and "VPN Tunneling: Session ended", all other messages will be disregarded.

#### Rate-limited API Count
- User can set rate-limiter for the API calls allowed to Pulse Secure per unit time.
- Default in the App allows up to 100 API calls per second.
- Range is 1 to 1000 APIs.

#### Predefined fields used panels
- Certification validation
- Authorization
- Rate limiter

### Test button
- Test is enabled by default.
- Device info needs to be saved (applied) before test can be successfully run.

## Manage the App
### Import
- User can import the Pulse Secure Connect App via the eyeExtend Connect module.
- App file shall look like ForeScout-pulsesecure-1.0.1.ECA which is signed.

## Start and Stop App
- User can start and stop the Pulse Secure App.
- When the App is stopped, all polling, properties resolve, actions and policies are suspended.

### Remove App
- User can remove the App if no longer needed.
- User needs to delete the Pulse Secure policies first to remove the App.

## Policy Templates
- There is a default Pulse Secure Template.
- After importing the App. the policy can be found under Policy > Add > Pulse Secure > Pulse Secure User Connection Info Policy.
- User can use the default policy to resolve properties from the endpoint on a schedule.

## Properties
There are 11 properties gathered from the Pulse Secure server for the endpoint.
- Pulse Secure Active Username 
- Pulse Secure Agent Type
- Pulse Secure Authentication Realm
- Pulse Secure Endpoint Security Status
- Pulse Secure Events
- Pulse Secure Login Node
- Pulse Secure Network Connect IP
- Pulse Secure Network Connect Transport Mode
- Pulse Secure Session ID
- Pulse Secure User Roles
- Pulse Secure User Sign-In Time

Additionally, Syslog also provides the Source IP of the connected client.
- Pulse Secure Source IP

## Actions
User can disconnect a connected Pulse Secure session from the endpoint. If the user is disconnected from Pulse Secure, the endpoint properties can't be resolved.

Disconnect user action is a one-time action. User needs to reconnect to the Pulse Secure server for resolve and disconnect actions to work properly again.

## Scripts
There are five scripts and a library file.
- pulsesecure_disconnect_user.py
    - User can disconnect a connected user from Pulse Secure.
- pulsesecure_poll.py
    - User can enable discovery on a specified period to poll endpoint properties. Default is 4 hours.
- pulsesecure_resolve.py
    - User can get the Pulse Secure properties of an endpoint.
- pulsesecure_test.py
    - User can test the connection to Pulse Secure server.
- pulsesecure_library.py
    - Library classes the scripts use. All API calls happen here.
- pulsesecure_syslog.py
	- Processing of Syslog messages is carried out by this script.

## Licenses
This App bundles with a license.txt file. Please review the license.txt file.
