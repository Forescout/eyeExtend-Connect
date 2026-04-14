# Forescout  
eyeExtend Connect App for Meraki MX README.md Version: 1.0.0
  
## Contact Information  
Forescout Technologies, Inc.  
190 West Tasman Drive  
San Jose, CA 95134 USA  
[https://www.Forescout.com/support/](https://www.forescout.com/support/)  
Toll-Free (US): 1.866.377.8771  
Tel (Intl): 1.408.213.3191  
Support: 1.708.237.6591  
  
## About the Documentation  
- Refer to the Technical Documentation page on the Forescout website for additional documentation: [https://www.Forescout.com/company/technical-documentation/](https://www.forescout.com/company/technical-documentation/)  
- Have feedback or questions? Write to us at [documentation@forescout.com](mailto:documentation@forescout.com)  
  
## Legal Notice  
© 2026 Forescout Technologies, Inc. All rights reserved. Forescout Technologies, Inc. is a Delaware corporation. A list of our trademarks and patents can be found at [https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks](https://urldefense.proofpoint.com/v2/url?u=https-3A__www.forescout.com_company_legal_intellectual-2Dproperty-2Dpatents-2Dtrademarks&amp;d=DwMFAg&amp;c=L5E2d05je37i-dadkViuXA&amp;r=Z3cI4QPLlfMimB_63ipHyFuWSHGqqAs50hjX-2X1CEw&amp;m=ypFjb5tb21hH81CxdGe-3FT8l4QXZe-hzuDh-eBT-wQ&amp;s=ATQ1mJb4KkN8L9fn2BnpRuwmDWJcze7zyqTbG1PTwkc&amp;e=). Other brands, products, or service names may be trademarks or service marks of their respective owners.  
  
# About eyeExtend Connect for Meraki MX
  
  
# Customer Support  
The Connect Plugin is supported by Forescout Customer Support. See [https://forescout.force.com/support/s/](https://forescout.force.com/support/s/).  
  
Connect Apps, including those provided by Forescout, are not supported by Forescout.  
  
# About This Module  
 
# What to Do  
To set up your system for integration with eyeExtend Connect for Meraki MX, perform the following steps:  
  
1. Verify that the requirements are met. Requirements.
2. Download and install the module. See How to Install.  
3. Configure the module. See Configure the Module.  
4. Configure policy templates. See Configure Meraki MX Policy Templates.  
5. Configure properties. See Configure Properties.  
6. Configure actions. See Configure Actions.  
  
# Use Cases & Requirements
This section describes important use cases and requirements supported by Forescout eyeExtend Connect for Meraki MX.  

## Use Cases
eyeExtend Connect for Meraki MX supports VLAN Assignment by VLAN ID only. This requires that devices can be seen within the Meraki MX LLDP table, as well as the below requirements.

## Meraki Requirements
Discovery of device switch port information when connected to Meraki MX devices has several requirements within Meraki. The below have been identified during testing of this Connect App.
- Meraki MX75 or higher models only
- Devices must have LLDP enabled in their configuration
	- Windows 10 Onwards has MAC Address advertisement over LLDP enabled by default
	- MacOS requires 3rd party software to enable LLDP advertisement

## Forescout Requirements
- A single Forescout device connects to the Meraki Dashboard, handling communication for a cluster of Forescout devices. The Forescout devices in the cluster can support only 1 Meraki Org.  
- For multiple Meraki Orgs, separate connections can be configured from different Forescout devices.

This Connect App has been tested on:
- Forescout version 8.5.3, 9.1.4
- eyeExtend Connect Plugin version 2.0.6
  
# How to Install  
Get Forescout eyeExtend Connect plugin and Meraki MX App from Forescout.  
  
## Ensure That the Plugin is Running  
After installing the Connect plugin, ensure that it is running.  
  
To verify:  
  
1. Select **Tools** > **Options** > **Modules**.  
2. Navigate to the component and hover over the name to view a tooltip indicating if it is running on Forescout devices in your deployment. In addition, next to the component name, you will see one of the following icons:  
  
- The component is stopped on all Forescout devices.  
- The component is stopped on some Forescout devices.  
- The component is running on all Forescout devices.  
  
3. If the component is not running, select **Start** , and then select the relevant Forescout devices.  
4. Select **OK**.  
 
# Configure the Module  
After eyeExtend Connect is installed, **Connect** is displayed under **Options**.  
  
  
## Configure Meraki MX App  
To configure eyeExtend Connect for Meraki MX, you import the Meraki MX App and then add a system description.  
  
Initially, the App Configuration tab of the **Connect** pane is blank. The Meraki MX App has not been imported yet and the system description has not been configured yet.  
  
## Import an App  
You can import the Meraki MX App.  
  
To import the Meraki MX App:  
  
1. In the App Configuration tab of the **Connect** pane, select **Import**.  
2. Apps that can be imported are in .zip or .eca format. They can be in any folder.  
3. Select **Import**.  
If the app is imported successfully, a message is displayed at the bottom of the **Sending** dialog box. If the app is not imported successfully, error messages are displayed in the **Sending** dialog box.  
4. Select **Close** when the import has finished. A blank **System Description** dialog box opens. See Add a System Description.  
  
- If you select **Close** before the import has finished, it will fail.  
  
## Add a System Description  
To configure the Meraki MX App, you add a system description to define a connection, which includes login credentials.  
  
To add the system description:  
  
After the app is imported, the **System Description** dialog box opens. It is initially blank and only the **Add** and **Import** buttons are enabled.  
  
If a system description has not been configured and you select **OK** now, a warning message is displayed.  
1. Select **Add**.  
2. Enter the following information:  
  
- Meraki Dashboard API URL: Enter the server URL for Meraki Dashboard API. (e.g. api.meraki.com)
- Meraki API Key: Enter the API for the Meraki Dashboard API.
- Meraki Organisation Name: Enter the Org Name exactly as configured within Meraki.
  
3. Select **Next**. 
4. Enter a test MAC Address here to be used during the Connect App test. This MAC Address should be an endpoint connected to a Meraki MX device during the test.

5. Select **Next**. 
6. Initially, the Assign Forescout Devices panel has only one option, **Assign all devices by default** , and it is selected so that one device is added.  
 - If you want to add a second device, the Assign Forescout Devices panel has more options.  
7. Enter the following information:  
- Connecting Forescout Device: Select Enterprise Manager or an IP address of the connecting Forescout device. In an environment where more than one Forescout device is assigned to a single third-party instance, the connecting Forescout Appliance functions as a middleman between the third-party instance and the Forescout Appliance. The connecting Forescout Appliance forwards all queries and requests to and from the third-party instance.  
- Assign specific devices: This Forescout Appliance is assigned to a third-party instance, but it does not communicate with it directly. All communication between the third-party instance and its assigned Forescout Appliance is handled by the connecting Forescout Appliance defined for the third-party instance. All the IP addresses handled by an assigned Appliance must also be handled by the third-party instance to which the Appliance is assigned.  
  - Select **Available Devices** and then select an IP address or Appliance name from the Available Devices list.  
  - Select **Add**. The selected device will send its requests to the third-party instance through the connecting Appliance.  
- Assign all devices by default: This is the connecting Appliance to which Forescout Appliances are assigned by default if they are not explicitly assigned to another connecting Appliance. Select this option to make this connecting Appliance the middleman for all Forescout Appliances not assigned to another connecting device.  
  
Note the following:  
  
- An error message is displayed if you try to add a device that is already used.  
- If you have apps that discover 50,000 or more endpoints, distribute the apps in such a way so that only up to two of the apps share the same focal (connecting) appliance. An alternative is to split the endpoints across multiple user accounts on multiple servers.  
  
8. Select **Next**.  
9. Enter the Proxy Server information similar to any Forescout Extended Module:
- Proxy Server IP address
- Proxy Server Port
- Proxy Server Username (if applicable/ authentication required)
- Proxy Server Password (if applicable/ authentication required)

10. Select **Next**.  
11. Optionally, define the refresh interval for the Connect App Instance Cache, this can be defined in minutes, between 5 minutes and 48 hours. This is set to 24 hours by default. The cache will retrieve Org and Network ID's from Meraki, so reduce this time only if you have regular changes to Network ID's in your environments.
12. Select **Finish**. The configured system description is displayed in the **System Description** dialog box.  
  
When the system description is selected, all the buttons on the dialog box are enabled.  
  
You can create multiple system descriptions. To add another system description, select **Add** and repeat the procedure for Add a System Description.  
  
13. Select **OK** to save the system description to the Forescout Appliance. The system description is displayed in the App Configuration tab of the **Connect** pane. There are several default columns. See Connect Pane Details.  
  
## Edit a System Description  
You can edit an existing system description for the Meraki MX App.  
  
To edit a system description:  
  
1. Select an existing system description and select **Edit**.  
There are tabs for each pane. You can edit the settings in the Meraki Connection, Meraki Test, Assign Forescout Devices, Proxy Server, and Meraki Options tabs.  
2. Select **OK** to save the system description edits to the Forescout Appliance.  
  
## Remove a System Description  
You can remove an existing system description.  
  
To remove a system description:  
1. Select an existing system description and select **Remove**. A confirmation is displayed.  
2. Select **More** for details or select **Ok**.  
  
## Test a System Description  
You can test a system description, which tests the connection of the eyeExtend Connect App to the Meraki Dashboard API. The app must be in the Running state.  
  
Also, the app must be saved before selecting **Test**. Select **OK** in the **System Description** dialog box and then select **Apply** in the **Connect** pane to save the system description. Please wait about 5-10 seconds after clicking apply.  
  
To test a system description:  
  
1. Select an existing system description and select **Test**.  
If the connectivity of the system description has been tested successfully, a success message is displayed at the top of the dialog box. If the test failed, a failure message is displayed with a reason.  
2. Select **Close**.  
  
## Refresh App Instance Cache
If changes have been made to the Organisation or Networks within Meraki, you can manually refresh the App Instance Cache.

1. Select an existing system description and select **Refresh**.
2. Select **App instance cache** and select **Ok**, then cache will refresh and provide a success or failure output.
  
# Meraki MX Properties  
Meraki MX properties are available to be used in a policy.  
  
The following properties are available:  
  
- **Meraki MX Device Name**: The name of the Meraki MX device an endpoint is connected to.
- **Meraki MX Port**: The port on the Meraki MX device an endpoint is connect to.
- **Meraki MX Port Type**: The port type an endpoint is connected to, this could be Access or Trunk ports. Note actions can only be taken on Access ports.
- **Meraki MX VLAN**: The current VLAN the endpoint is in on the Meraki MX device.
- **Meraki MX Network ID**: The Meraki Network ID that the MX device and the endpoint belong to.

# Meraki MX Actions  
Meraki MX actions are available to be used in a policy.  
  
To access the Meraki MX actions:  
  
1. When configuring a policy, select **Add** in the Actions section of the Main Rule or Sub-Rule dialog box.  
2. Search for Meraki MX.  
3. Select an action in the **Meraki MX** folder.  
  
The following action is available:  
- **Assign to VLAN - Meraki MX**: Using the VLAN ID only (VLAN Names not supported), assign the device to a VLAN. The device must have the **Meraki MX Port** property resolved.
