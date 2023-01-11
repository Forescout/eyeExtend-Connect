Forescout eyeExtend Connect Viakoo App README.md
Version: 1.2.1
 
## Contact Information
Viakoo, Inc.
650 Castro St. Suite 120-203
Mountain View, CA 94041

https://www.viakoo.com/

Support: https://viakoo.zendesk.com/hc/en-us
Toll-Free (US): (650) 263-8225

## About the Documentation
- Refer to the Technical Documentation page on the Forescout website for additional documentation:
https://www.Forescout.com/company/technical-documentation/
- Have feedback or questions? Write to us at documentation@forescout.com

## Legal Notice
© 2020 Forescout Technologies, Inc. All rights reserved. Forescout Technologies, Inc. is a Delaware corporation.
A list of our trademarks and patents can be found at https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks.
Other brands, products, or service names may be trademarks or service marks of their respective owners.

## About the eyeExtend Connect Viakoo App
The [Viakoo Action Platform](https://www.viakoo.com/) is used to track and perform remediation on enterprise level IoT devices.

The Viakoo App polls device information from the Viakoo Action Platform showing up to date information on devices including information on camera streams and firmware versions.

## Requirements
The App supports:
- Forescout CounterACT 8.4
- Forescout eyeExtend Connect 1.7.x

## User Interface
You can refer to the Forescout eyeExtend Connect Module: Connect Application Building Guide, in particular the
sections on ”Define system.conf File” and “User Interface Details”.
### Panels
#### Device
User can add Viakoo Site connection to the App.
- Site name or id to gather devices from
- User email connected to the Viakoo Action Platform with permission for specified site
- Password for the user in the Viakoo Action Platform
- User can test the device by clicking TEST button after applying changes.
- User can add multiple sites, they need to be unique and have a dedicated focal appliance.

#### Focal appliance
Each device shall run on one dedicated focal appliance.

#### Rate-limited API Count
- User can set rate-limiter for the API allowed to the Viakoo Action Platform per unit time.
- Default in the App is allowing up to 100 API calls per second.
- Range is 1 to 1000 APIs.

#### Predefined fields used panels
- Certification validation
- Rate limiter

### Test button
- Test is enabled by default.
- Connection info needs to be saved (applied) before test can be successfully run.

## Manage the App
### Import
- User can import the Viakoo Connect App via eyeExtend Connect module
- App file shall look like ViakooApp.ECA which is signed

## Start and Stop App
- User can start and stop the Viakoo App
- When the App is stopped, all properties resolve, actions and policy are suspended.

### Remove App
- User can remove the App if no longer needed
- User need to delete the Viakoo Compliance policy first to remove the App.

## Policy Templates
- There is one template that sorts device by firmware version compliance

## Properties
There are a few properties gathered from the Viakoo server for each endpoint.
- Firmware Version
- Video Codec
- ADD MORE

## Scripts
There are 3 scripts and 1 library file.
- viakoo_resolve.py
User can get the Viakoo properties of an endpoint.
- viakoo_test.py
User can test the connection to Viakoo server with defined device.
- viakoo_poll.py
User can enable discovery on a specified period to poll endpoint properties. Default is 4 hours.
- viakoo_library.py
Library file scripts use.

## Licenses
This App bundles with a license.txt file. Please review the license.txt file.

## About 1.0
- Able to use name or id of site to poll devices from Viakoo