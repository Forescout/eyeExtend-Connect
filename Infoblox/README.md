# Forescout
eyeExtend Connect Infoblox App README.md Version: 1.0.1

## Configuration Guide
**Version 1.0.1**
- Updated error handling to provide more detail for network failure errors
- Modified Test Query to avoid 400 error when response is too large

**Version 1.0.0**
- Initial App to retrieve DHCP Fingerprint and Device Class from Infoblox

## About eyeExtend Connect Infoblox App

# About This App

The eyeExtend Connect Infoblox App provides functionality to retrieve the matched DHCP Fingerprint, Device Class and DHCP Option Sequence in Infoblox and report this in the Forescout platform to assist with device classification.

Currently, if there is a conflict for a device within Infoblox, this App will not retrieve any data to avoid pulling incorrect data into Forescout host profiles.

This app has been tested with Infoblox Web API version 2.12.3

# What to Do  
To set up your system for using the eyeExtend Connect Infoblox App, perform the following steps:  

1. Download and install the module. See How to Install.  
2. Configure the module. See Configure the Module.  
3. Configure policy templates.  
4. Configure properties.  
5. Configure actions.  

# How to Install  
Get Forescout eyeExtend Connect plugin and Infoblox App from Forescout.  

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

## Configure Infoblox App
To configure eyeExtend Connect Infoblox App, you import the Infoblox App.

Initially, the App Configuration tab of the **Connect** pane is blank. The Infoblox App has not been imported yet.

## Import an App
You can import the Infoblox App.

To import the Infoblox App:

In the App Configuration tab of the **Connect** pane, select **Import**.
Apps that can be imported are in .zip or .eca format. They can be in any folder.
	Select **Import**.  
If the app is imported successfully, a message is displayed at the bottom of the **Sending** dialog box. If the app is not imported successfully, error messages are displayed in the **Sending** dialog box.  

Select
**Close** when the import has finished.
A blank **System Description** dialog box opens. 

- If you select **Close** before the import has finished, it will fail.  

## Panels


After the app is imported, the **System Description** dialog box opens. It is initially blank and only the **Add** and **Import** buttons are enabled.  

To configure the Infoblox App, you add a system description to define a configuration.  

If a system description has not been configured and you select **OK** now, a warning message is displayed.  

Select **Add**

### Infoblox Connection


On this panel, enter the Infoblox Grid Master IP or FQDN that will be used for the API connection, along with the port if changed from the default TCP/443.

Enter the username and password that has been configured for the API calls, ensure that the relevant permissions as detailed below are set correctly.

Select **Next**


### Assign Forescout Devices


 - Initially, the Assign Forescout Devices panel has only one option, **Assign all devices by default** , and it is selected so that one device is added.

If you want to add a second device, the Assign Forescout Devices panel has more options.

Enter the following information:

- Connecting Forescout Device: Select Enterprise Manager or an IP address of the connecting Forescout device. This is the device which will connect to Infoblox.  
- Assign specific devices: This Forescout Appliance is assigned to the connecting Forescout device for requesting property resolution via this Connect App.
  - Select **Available Devices** and then select an IP address or Appliance name from the Available Devices list.  
  - Select **Add**. The selected device will send its requests to the connecting Appliance.  
- Assign all devices by default: This is the connecting Appliance to which Forescout Appliances are assigned by default if they are not explicitly assigned to another connecting Appliance. Select this option to make this connecting Appliance the appliance to carry out all API calls for all Forescout Appliances not assigned to another connecting device.


Note the following:  

- An error message is displayed if you try to add a device that is already used.  
- If you have apps that discover 50,000 or more endpoints, distribute the apps in such a way so that only up to two of the apps share the same focal (connecting) appliance. An alternative is to split the endpoints across multiple user accounts on multiple servers.  


Select **Next**.

### Proxy Server


If a Proxy Server is required, enter the Proxy Server information here.

Select **Next**.

## Edit a System Description  
You can edit an existing system description for the Infoblox App.  

To edit a system description:  

Select an existing system description and select **Edit**.  

There are tabs for each pane. You can edit the settings in the Infoblox Connection, Assign Forescout Devices, and Proxy Server tabs.  

Select **OK** to save the system description edits to the Forescout Appliance.  

## Remove a System Description  
You can remove an existing system description.  

To remove a system description:  
Select an existing system description
Select **Remove**. A confirmation is displayed.  

**More** for details or **Ok**.  

# Required Permissions

It is recommended to create a separate Group or Role specifically for the Forescout API user to effectively manage permissions.

| Permission Type | Permission Name | Setting |
|-----------------|-----------------|---------|
| DHCP Permissions | All Network Views | Read-Only |
| DHCP Permissions | All IPv4 Networks | Read-Only |
| DHCP Permissions | All Hosts | Read-Only |
| DHCP Permissions | All IPv4 Host Addresses | Read-Only |
| DHCP Permissions | All IPv4 Ranges | Read-Only |
| DHCP Permissions | All IPv4 DHCP Fixed Addresses/Reservations | Read-Only |
| DHCP Permissions | All IPv4 DHCP Shared Networks | Read-Only |
| DHCP Permissions | All Roaming Hosts | Read-Only |
| DHCP Permissions | All IPv6 Networks | Read-Only |
| DHCP Permissions | All IPv6 Ranges | Read-Only |
| DHCP Permissions | All IPv6 DHCP Fixed Addresses | Read-Only |
| DHCP Permissions | All IPv6 Host Addresses | Read-Only |
| DHCP Permissions | All DHCP Fingerprints | Read-Only |