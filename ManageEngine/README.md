Forescout eyeExtend Connect ManageEngine Patch Manager Plus App README.md
 

## Legal Notice
© 2021 Forescout Technologies, Inc. All rights reserved. Forescout Technologies, Inc. is a Delaware corporation.
A list of our trademarks and patents can be found at https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks.
Other brands, products, or service names may be trademarks or service marks of their respective owners.

## Updates / Features(as of July 16, 2022):
-----------------------------------------------
1. Changed to version 2.1, minor code revisions;
2. Added Session Expiry Timer(3 minutes) in the ManageEngine DesktopCentral Connect app configuration;
3. Resource ID is now retreived from the MEDesktop Central server using NetBIOS hostname as parameter;
4. The Connect app leverages the ManageEngine version 1.3 API;
5. Tested to work on following software:
	- ManageEngine Desktop Central Build Version:10.0.652;
	- Forescout version 8.3.0-233;
	- Forescout eyeExtend Connect ver. 1.7.2;



## Updates / Features(as of February 21, 2021):
-----------------------------------------------
1. Changed to version 2.0, due to major code revisions;
2. ManageEngine version 1.3 API;
3. Set the default port to TCP Port 8020(previously port 80)
4. Revised the policies:
    - Get Resource ID       : Query the Windows registry to get the ManageEngine Resource ID
    - Agent Windows Service : Query the endpoints Windows Services for the Agent Service Status
    - Agent Status          : Query the ManageEngine Server for the Agent Installation status of the host
    - Missing MS Patches    : Query the ManageEngine Server for missing Microsoft patches on the host
    - Missing 3rd-Party Patches: Query the ManageEngine Server for missing 3rd-party patches on the host
5. Added the following endpoint actions:
    - Initiate Patch scan        : will trigger the ManageEngine server to initiate patch scan on the target endpoint. 
                                 : calls the /api/1.3/patch/computers/scan url
    - Install all Missing Patches: will trigger the ManageEngine server to initiate patch scan on the target endpoint.
                                 : calls the /api/1.3/patch/installpatch url
6. Added the following computer details / endpoint properties:
    - Device Model
    - Device Type
    - Device Manufacturer
    - Serial number
    - Processors
    - Memory(Megabytes)
    - Disk Summary - Percentage Use
    - Disk Summary - Total Disk Size
    - ManageEngine Agent software version
    - Missing MS Patch IDs
    - Missing 3rd-party Patch IDs

## ManageEngine ver. 2.0 supports:
- ManageEngine Patch Manager Plus Build Version:10.0.652
- Forescout CounterACT 8.2.x
- Forescout eyeExtend Connect 1.7.0



## April 22, 2020
## About the eyeExtend Connect ManageEngine Patch Manager Plus(PM)
The App gathers patch information for all Windows endpoint assets registered to ManageEngine Patch Manager Plus. The current version is able to detect the following:

 - ManageEngine Patch Status
 - Endpoint Vulnerability Status
 - Patch Scan Status

User can also use policies or trigger actions to send email notification and/or run custom scripts. The App uses URL API interface to access the ManageEngine Patch Management Plus server.

## Requirements
The App supports:
- ManageEngine Patch Manager Plus Build Version:10.0.421
- Forescout CounterACT 8.2
- Forescout eyeExtend Connect 1.1.0
- See license.txt file for license information

## User Interface
You can refer to the Forescout eyeExtend Connect Module: Connect Application Building Guide, in particular the sections on ”Define system.conf File” and “User Interface Details”.

### Panels
#### Device
User can add ManageEngine Patch Manager server to the App.
- Server name shall be the ManageEngine server in "http://<ManageEngineServerNameOrIP>" format
- User shall be admin that can access MnageEngine web APIs via management interface
- Password shall be the admin password that can be used to do web API call to ManageEngine server
- User can test the device by clicking TEST button after applying changes.
- User can add multiple devices, they need to be unique and has a dedicated focal appliance.

#### Focal appliance
Each device shall run on one dedicated focal appliance.

### Test button
- Test is enabled by default.
- Device info need to be saved (applied) before test can be successfully run.

## Manage the App

### Import
- User can import the GlobalProtect Connect App via eyeExtend Connect module

## Start and Stop App
- User can start and stop the ManageEngine Patch Manager(PM) App
- When the App is stopped, all properties resolve, actions and policy are suspended.

### Remove App
- User can remove the App if no longer needed
- User need to delete the ManageEngine Patch Manager policies first to remove the App.

## Policy Templates
- There is a default ManageEngine Patch Manager(PM) Template
- After importing the App. the policy can be found under Policy > Add > ManageEngine PM 
- User can use the default policy to resolve properties from endpoint on a schedule or policy match.
- The policies included are as follows:
    a. MEPM Get Resource ID - This policy MUST BE created first, since the obtained Resource ID from this policy is used to gather endpoint patch management details from the ManageEngine server.
    b. MEPM Agent Status - This policy checks all managed Windows endpoints for the presence of patch management agent.
	c. MEPM Patch Scan Status - This policy shows the patch scan status applied to the endpoint.
	d. MEPM Endpoint Vulnerability Status - This policy shows the health status of an endpoint based on the following category: Highly Vulnerable, Vulnerable, Healthy and Unknown.

## Properties
The following properties are gathered from the ManageEngine Patch Management server for the endpoint.
- Endpoint Operating System 
- Endpoint Service Pack
- Endpoint Resource Health Status
- Endpoint Branch Office
- Endpoint Patch Scan Status
- Endpoint Vulnerabilities
- Endpoint Last Successful Scan
- Endpoint Agent Last Contact Time

## Actions
No available endpoint action is created for this version.

## Scripts
There are three scripts that comes with this app.
- fs_connect_get_resid.bat
This script attempts to capture the Resource ID number that will be used as a parameter by the app to capture endpoint details from the server. This needs to be uploaded to the FS appliance. The script is required in the MEPM Get Resource ID policy.
- mepm_test.py
Script used to validate connectivity to the patch management server.
- mepm_resolve.py
This script is used to resolve the endpoint properties.

## Notes
- The batch file script(that captures the Resource ID) needs to be uploaded first to the ForeScout appliance.
- Do not modify the action of the MEPM Get Resource ID policy. Doing so will change the internal script reference number that is coded in the policy. To fix this, just uninstall and re-install the MEPM Get Resource ID policy.
- The batch file script may not work on some Windows endpoints.

## Licenses
This App bundles with a license.txt file. Please review the license.txt file.
