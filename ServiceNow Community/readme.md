Forescout eyeExtend for ServiceNow App README.md Version 2.1.0

# **Contact Information**
- Have feedback or questions? Write to us at [**connect-app-help@forescout.com**](mailto:connect-app-help@forescout.com)
# **APP Support**
- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.
# **About the ServiceNow App**
## Use Cases
This connect app is designed to automate the onboarding and retiring of network assets in coordination with a CMDB (ServiceNow).
Automatically add new asset mac addresses into the Forescout MAR (Mac address Repository) once discovered in the CMDB.
(otional)Automatically remove assets from the Forescout MAR when the CMDB asset status is changed to retired or stolen.


## How It Works
Forescout polls ServiceNow via API at a user defined interval.  
ServiceNow returns only configuration items that contain mac address, serial number, asset tag, and install status.
Forescout updates/adds the assets in eyesight.
![App Screenshot](images/pull.png)

# **What to Do**
To set up your system for integration with eyeExtend Connect App for ServiceNow, perform the following steps:

1. Verify that the requirements are met. See Requirements.
2. Download and install the module. See How to Install.
3. Configure the module. See Configure the Module.
## Requirements
- Forescout version 8.4.x +
- ServiceNow API Account with the ability to read the cmdb_ci table.
- CMDB CIs must have asset tag, serial number, mac address, and install status populated in ServiceNow
- Forescout Connect Module

# **How to Install**
Download and install the connect app.

		

After installing the Connect plugin, ensure that it is running.

To verify:

- Select **Tools** > **Options** > **Modules**.
- Navigate to the component and hover over the name to view a tooltip indicating if it is running on Forescout devices in your deployment. In addition, next to the component name, you will see one of the following icons:
  - The component is stopped on all Forescout devices.
  - The component is stopped on some Forescout devices.
  - The component is running on all Forescout devices.
- If the component is not running, select **Start** , and then select the relevant Forescout devices.
- Select **OK**.
### Download and install the servicenow connect app from github.


### Configure the module.
	Add an instance
	- ServiceNow Connection Information
		- Service Now instance FQDN (without https://)
		- Service Now API Username
		- Service Now API Password
		- Service Now Table Name (almost always cmdb_ci)
		- Enable Host Discovery (must be checked)
		- Discovery Frequency in Minutes (how often to check for new hosts and install status updates)
		- Already have the ServiceNow Module syncing install status ( check this box if you already have the main Forescout ServiceNow module syncing install status)
	- Assign ConterACT Device
		- ConterACT Device for polling ServiceNow API
	
**Test** the API connection
	- You should see a success for the ServiceNow API.

#### Policies
There are two policies templates included with this app.

	SNOW Onboarding
		When CIs are added to eyeSight for the first time this policy will add their MAC address to the MAR (allowing network authentication via RADIUS MAB)
		This policy should be scoped to include “Hosts without a known IP address”
	SNOW Install Status (not needed if you already have the ServiceNow Module in Forescout)
		This policy allows you to see the install status for the CIs and automatically removes assets from the CI’s MAC address from the MAR if they have been retired or stolen.
		This policy should be scoped for assets with an IP address (segment choice at admins discretion)

