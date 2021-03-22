Forescout eyeExtend Connect PulseSecure App README.md
Version: 1.0.0

## Contact Information

Have feedback or questions? Write to us at

**[connect-app-help@forescout.com](mailto:connect-app-help@forescout.com)**

## About the Documentation
- Refer to the Technical Documentation page on the Forescout website for additional documentation:
https://docs.forescout.com/

## About the eyeExtend Connect PulseSecure App
The App gathers user and endpoint information that connect to PulseSecure servers through discovery and resolve. User can also use policies or
actions to disconnect sessions from the PulseSecure Server. The App uses the admin console via REST APIs to access the
PulseSecure server.

## Requirements
The App supports:
- Pulse Connect Secure 9.1.8
- Forescout CounterACT 8.2
- Forescout eyeExtend Connect 1.4
- See license.txt file for license information

## User Interface
You can refer to the Forescout eyeExtend Connect Module: Connect Application Building Guide, in particular the
sections on ”Define system.conf File” and “User Interface Details”.
### Panels
#### Device
User can add PulseSecure server to the App.
- Server name: PulseSecure server hostname or IP address. Do not include the protocol (http://, https://, etc.)
- User: Admin that can access the PulseSecure API via admin console.
- Password: Admin password that can be used to get the API key for API calls to the PulseSecure server.
- User can test the device by clicking the TEST button after applying changes.

#### Focal Appliance
Each device shall run on one dedicated focal appliance.

#### Proxy Server
- User can connect to the PulseSecure server via proxy server.
- Fields
    - Proxy Server
    - Proxy Server Port
    - Proxy Server Username
    - Proxy Server Password
- Proxy server username and password are not required and may be left blank for proxy servers that don't require authentication.

#### Rate-limited API Count
- User can set rate-limiter for the API calls allowed to PulseSecure per unit time.
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
- User can import the PulseSecure Connect App via the eyeExtend Connect module.
- App file shall look like ForeScout-pulsesecure-1.0.0.ECA which is signed.

## Start and Stop App
- User can start and stop the PulseSecure App.
- When the App is stopped, all polling, properties resolve, actions and policies are suspended.

### Remove App
- User can remove the App if no longer needed.
- User needs to delete the PulseSecure policies first to remove the App.

## Policy Templates
- There is a default PulseSecure Template.
- After importing the App. the policy can be found under Policy > Add > PulseSecure > PulseSecure User Connection Info Policy.
- User can use the default policy to resolve properties from the endpoint on a schedule.

## Properties
There are 11 properties gathered from the PulseSecure server for the endpoint.
- PulseSecure Active Username 
- PulseSecure Agent Type
- PulseSecure Authentication Realm
- PulseSecure Endpoint Security Status
- PulseSecure Events
- PulseSecure Login Node
- PulseSecure Network Connect IP
- PulseSecure Network Connect Transport Mode
- PulseSecure Session ID
- PulseSecure User Roles
- PulseSecure User Sign-In Time

## Actions
User can disconnect a connected PulseSecure session from the endpoint. If the user is disconnected from PulseSecure,
the endpoint properties can't be resolved.

Disconnect user action is a one-time action. User needs to reconnect to the PulseSecure server for resolve and
disconnect actions to work properly again.

## Scripts
There are four scripts and a library file.
- pulsesecure_disconnect_user.py
    - User can disconnect a connected user from PulseSecure.
- pulsesecure_poll.py
    - User can enable discovery on a specified period to poll endpoint properties. Default is 4 hours.
- pulsesecure_resolve.py
    - User can get the PulseSecure properties of an endpoint.
- pulsesecure_test.py
    - User can test the connection to PulseSecure server.
- pulsesecure_library.py
    - Library classes the scripts use. All API calls happen here.

## Licenses
This App bundles with a license.txt file. Please review the license.txt file.