Forescout eyeExtend Connect Kaseya VSA Patch Management App README.md
 

## Legal Notice
© 2020 Forescout Technologies, Inc. All rights reserved. Forescout Technologies, Inc. is a Delaware corporation.
A list of our trademarks and patents can be found at https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks.
Other brands, products, or service names may be trademarks or service marks of their respective owners.

## About the eyeExtend Connect Kaseya VSA Patch Management
The App gathers patch information for all Windows endpoint assets registered to Kaseya VSA Patch Management. The current version is able to detect the following:

 - Kaseya VSA - Get Agent Status
 - Kaseya VSA - Get Endpoint Details
 - Kaseya VSA - Get Patch Compliance
 - Kaseya VSA - Get Patch Scan Date Compliance

User can also use policies or trigger actions to send email notification and/or run custom scripts. The App uses URL API interface to access the Kaseya VSA server.

## Requirements
The App supports:
- Kaseya VSA Build Version: 9.5.0.2, Patch Level 27
- Forescout CounterACT 8.2
- Forescout eyeExtend Connect 1.1.0
- User name & password to connect to Kaseya VSA server with either Master or Policy Management role.
- See license.txt file for license information

Note:
This app was tested using the Patch Management module of Kaseya VSA. I understand that Kaseya has another module called Software Management--that can also be used for patch management. This app does not support integration with the Kaseya Software Management module, as there was no API available during the time of development.

## User Interface
You can refer to the Forescout eyeExtend Connect Module: Connect Application Building Guide, in particular the sections on ”Define system.conf File” and “User Interface Details”.

### Panels
#### Device
User can add Kaseya VSA Patch Management server to the App.
- Server name shall be the Kaseya VSA Patch Management server in "http://<ManageEngineServerNameOrIP>:<port>" format
- User shall be admin that can access Kaseya VSA web APIs via management interface
- Password shall be the admin password that can be used to do web API call to Kaseya VSA Patch Management server
- User can test the device by clicking TEST button after applying changes.
- User can add multiple devices, they need to be unique and has a dedicated focal appliance.

#### Focal appliance
Each device shall run on one dedicated focal appliance.

### Test button
- Test is enabled by default.
- Device info need to be saved (applied) before test can be successfully run.

## Manage the App

### Import
- User can import the Kaseya VSA Patch Management Connect App via eyeExtend Connect module

## Start and Stop App
- User can start and stop the Kaseya VSA Patch Management App
- When the App is stopped, all properties resolve, actions and policy are suspended.

### Remove App
- User can remove the App if no longer needed
- User need to delete the Kaseya VSA Patch Management policies first to remove the App.

## Policy Templates
- There is a default Kaseya VSA Patch Management Patch Template
- After importing the App. the policy can be found under Policy > Add > Kaseya VSA 
- User can use the default policy to resolve properties from endpoint on a schedule or policy match.
- The policies included are as follows:
    a. Kaseya VSA - Get Endpoint Details  - This policy MUST BE created first, since the obtained Resource ID from this policy is used to gather endpoint patch management details from the Kaseya VSA Patch Management server.
    b. Kaseya VSA - Get Agent Status - This policy checks all managed Windows endpoints for the presence of patch management agent.
	c. MEPM Patch Scan Status - This policy shows the patch scan status applied to the endpoint.
	d. MEPM Endpoint Vulnerability Status - This policy shows the health status of an endpoint based on the following category: Highly Vulnerable, Vulnerable, Healthy and Unknown.

## Properties
The following properties are captured from the Kaseya VSA Patch Management server for the endpoint.
- Endpoint Agent ID
- Endpoint Asset ID
- Endpoint Machine Group
- Endpoint OS Name
- Endpoint Last Seen Date
- Endpoint Last Patch Scan Date
- Endpoint Has Patch Scan History
- Endpoint Asset is Patch Compliant
- Endpoint Missing Patches with the following details:
    - Patch Update Classification
    - KB Article ID
    - Update Title
    - Product Name

## Actions
Two (2) actions are available in this App, and they are the following:
    - Run Patch Scan Now
    - Run Patch Update Now

Note: During the time of development, although an API for the Patch Update action is available, we found out that it was not working properly. A ticket was raised to the vendor, and the vendor admitted that there's a defect in the said API.

## Scripts
There are eight (8) scripts that comes with this app.
- KASEYAVSA_API_LIB.py
This file serves as the program library, and serves as the repository for all commonly used program functions.
- kaseyavsa_test.py
Script used to validate connectivity to the patch management server.
- kaseyavsa_resolve.py
This script is used to resolve the endpoint properties.
- kaseyavsa_poll.py
This script is used to regularly poll the Kaseya VSA server to resolve endpoint properties.
- kaseyavsa_patch_now.py
This script is used to trigger the Kaseya VSA server to initiate a patch.
- kaseyavsa_last_patch_scan_date_resolve.py
This script is used to resolve the last patch scan date of the endpoint.


## Licenses
This App bundles with a license.txt file. Please review the license.txt file.
