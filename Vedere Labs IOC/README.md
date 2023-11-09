# Forescout
eyeExtend Connect Vedere Labs IOC App README.md Version: 1.0.0

## Configuration Guide
**Version 1.0.0**
- Initial Version

## Contact Information  
- Have feedback or questions? Write to us at

**[connect-app-help@forescout.com](mailto:connect-app-help@forescout.com)**

## App Support

- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.

## About eyeExtend Connect Vedere Labs IOC App

# About This App

The eyeExtend Connect Vedere Labs IOC App provides functionality to ingest IOCs, including IPv4 addresses, Domain Names, URLs, or File Hashes all provided through the Vedere Labs Threat Feed Service.

You will need an API key to make use of this feed, you can sign up for an API key at https://forescout.vederelabs.com/register

# What to Do  
To set up your system for using the eyeExtend Connect Vedere Labs IOC App, perform the following steps:  

1. Download and install the module. See How to Install.  
2. Configure the module. See Configure the Module.  
3. Configure policy templates.  
4. Configure properties.  
5. Configure actions.  

# How to Install  
Get Forescout eyeExtend Connect plugin and Vedere Labs IOC App from Forescout.  

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

## Configure Vedere Labs IOC App
To configure eyeExtend Connect Vedere Labs IOC App, you import the Vedere Labs IOC App.

Initially, the App Configuration tab of the **Connect** pane is blank. The Vedere Labs IOC App has not been imported yet.

## Import an App
You can import the Vedere Labs IOC App.

To import the Vedere Labs IOC App:

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

To configure the Vedere Labs IOC App, you add a system description to define a configuration.  

If a system description has not been configured and you select **OK** now, a warning message is displayed.  

Select **Add**


### Connection


To configure the connectivity to the Vedere Labs Threat Feed, select the feed type to be used. Only the **Standard IOCs** feed is available at this time.

**Instance Description** is a friendly name for referencing this configuration in the app, and the **Subscriber API Key** is obtained during registration.

To ensure a secure connection, optionally select to **Validate Server Certificate** on this connection.

Select **Next**

### IOC Feed


On the IOC feed tab, the specific details of which IOCs are retrieved can be configured.

**Lookback Days** defines how many days to retrieve IOCs for. As this will poll daily be default, and previous IOCs will remain in the IOC Scanner, it is recommended to leave this at *1*

Select to optionally enable **IPv4**, **DNS** (this includes Domain Name and URLs), or **File Hash** feeds. At least one of these must be selected for any IOCs to be retrieved. The eyeSight platform must be monitoring traffic to identify either IPv4 or DNS IOCs. File Hash IOCs can be identified on manageable devices within the eyeSight platform.

A confidence is provided to each IOC based on all the known data around it, and how accurate it is believed to be. The **Minimum Confidence Score** defines the lowest confidence value that will be automatically imported into the IOC Scanner. This is set at *50* by default.

All IOCs retrieved will attempt to set the severity based on any identified kill chain phases, mapped to the MITRE ATT&CK&reg; framework. Where a kill chain phase has not been identified, the **IOCs Default Severity Level** will be used on import.

Select **Next**

### Focal Appliance


 - Initially, the Assign Forescout Devices panel has only one option, **Assign all devices by default** , and it is selected so that one device is added.

If you want to add a second device, the Assign Forescout Devices panel has more options.

Enter the following information:

- Connecting Forescout Device: Select the IP address of the connecting Forescout device. This is the device which will communicate with the Vedere Labs Threat Feed.  
- Assign specific devices: This Forescout Appliance is assigned to the connecting Forescout device for retrieveing any IOCs via the Vedere Labs Threat Feed.
  - Select **Available Devices** and then select an IP address or Appliance name from the Available Devices list.  
  - Select **Add**. The selected device will send its requests to the connecting Appliance.  
- Assign all devices by default: This is the connecting Appliance to which Forescout Appliances are assigned by default if they are not explicitly assigned to another connecting Appliance. Select this option to make this connecting Appliance the appliance to retrieve IOCs for all Forescout Appliances not assigned to another connecting device.


Note the following:  

- An error message is displayed if you try to add a device that is already used.  
- If you have apps that discover 50,000 or more endpoints, distribute the apps in such a way so that only up to two of the apps share the same focal (connecting) appliance. An alternative is to split the endpoints across multiple user accounts on multiple servers.  


Select **Next**.

### Proxy Server


If required, optionally enter the Proxy Server information needed for network connectivity.  

Select **Next**.  

### Advanced


If required, the default refresh interval of **1440 Minutes** or the number of API queries **100 per second** can be modified here.

Select **Finish**

## Edit a System Description  
You can edit an existing system description for the Vedere Labs IOC App.  

To edit a system description:  

Select an existing system description and select **Edit**.  

There are tabs for each pane. You can edit the settings in the Vedere Labs IOC, Time Format, DNS Short Name, and Assign Forescout Devices tabs.  

Select **OK** to save the system description edits to the Forescout Appliance.  

## Remove a System Description  
You can remove an existing system description.  

To remove a system description:  
Select an existing system description
Select **Remove**. A confirmation is displayed.  

**More** for details or **Ok**.  

## Refresh IOC Data
You can refresh *Discovery of IOC Data*, which instructs the Vedere Labs IOC App to resolve IOCs immediately. The app must be in the Running state.  

The app must be saved before selecting **Refresh**. Select **OK** in the **System Description** dialog box and then select **Apply** in the **Connect** pane to save the system description. Please wait about 5-10 seconds after clicking apply.  

To refresh IOC data:  

Select an existing system description
Select **Refresh**, then **Discovery of IOC Data** and select **OK**.

A window will appear to display the status of the refresh.

Once complete, all IOC data retrieved will be visible in the IOC Scanner within the Forescout eyeSight platform.