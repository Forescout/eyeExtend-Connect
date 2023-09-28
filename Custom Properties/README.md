# Forescout
eyeExtend Connect Custom Properties App README.md Version: 1.0.2

## Configuration Guide
**Version 1.0.0**
- Current Time App

**Version 1.0.1**
- Combined with Short DNS Name to create Custom Properties app

**Version 1.0.2**
- Resolved an issue with Short DNS Name not updating the host properties correctly

**Version 1.0.3**
- Added Active Network Adapter property

## Contact Information  
- Have feedback or questions? Write to us at

**[connect-app-help@forescout.com](mailto:connect-app-help@forescout.com)**

## App Support

- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.

## About eyeExtend Connect Custom Properties App

# About This App

The eyeExtend Connect Custom Properties App provides multiple custom properties and actions to expand the functionality of the Forescout platform.

# What to Do  
To set up your system for using the eyeExtend Connect Custom Properties App, perform the following steps:  

1. Download and install the module. See How to Install.  
2. Configure the module. See Configure the Module.  
3. Configure policy templates.  
4. Configure properties.  
5. Configure actions.  

# How to Install  
Get Forescout eyeExtend Connect plugin and Custom Properties App from Forescout.  

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

## Configure Custom Properties App
To configure eyeExtend Connect Custom Properties App, you import the Custom Properties App.

Initially, the App Configuration tab of the **Connect** pane is blank. The Custom Properties App has not been imported yet.

## Import an App
You can import the Custom Properties App.

To import the Custom Properties App:

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

To configure the Custom Properties App, you add a system description to define a configuration.  

If a system description has not been configured and you select **OK** now, a warning message is displayed.  

Select **Add**

### Custom Properties


On this panel, select which custom properties are intended for use. This will enable the tests for those properties to ensure they can function correctly.

Select **Next**

### Time Format


If the Timestamp property and action is to be used, this panel should be configured with the format required.

For **Time Format**, select one of:
- UTC
- Epoch
- Timezone

If Timezone is selected, then additionally configure the **Timezone Offset**. This should be configured as +/- number of hours, for example, to set for CDT (Central Daylight Time), set this to -5

Select **Next**

### DNS Short Name


If DNS Short Name property is to be used, optionally configure the custom settings here.

By default, the app will resolve the DNS Short Name as all text up to the first '.' in the DNS reverse lookup result. To change this, select the **Enable Custom DNS Domain** checkbox, and add any custom domains as a comma-separated list to the **Custom DNS Domain** setting.

For example, when resolving an IP Address to *host.sub.dns.domain* the following results will be seen:

- Default: *host*
- Custom DNS Domain (dns.domain): *host.sub*
- Custom DNS Domain (domain): *host.sub.dns*

Select **Next**

### Assign CounterACT Devices


 - Initially, the Assign CounterACT Devices panel has only one option, **Assign all devices by default** , and it is selected so that one device is added.

If you want to add a second device, the Assign CounterACT Devices panel has more options.

Enter the following information:

- Connecting CounterACT Device: Select Enterprise Manager or an IP address of the connecting CounterACT device. This is the device which will carry out resolution of the custom properties, or perform the selected actions.  
- Assign specific devices: This CounterACT Appliance is assigned to the connecting CounterACT device for any property resolution or action required via this Connect App.
  - Select **Available Devices** and then select an IP address or Appliance name from the Available Devices list.  
  - Select **Add**. The selected device will send its requests to the connecting Appliance.  
- Assign all devices by default: This is the connecting Appliance to which CounterACT Appliances are assigned by default if they are not explicitly assigned to another connecting Appliance. Select this option to make this connecting Appliance the appliance to resolve properties or carry out actions for all CounterACT Appliances not assigned to another connecting device.


Note the following:  

- An error message is displayed if you try to add a device that is already used.  
- If you have apps that discover 50,000 or more endpoints, distribute the apps in such a way so that only up to two of the apps share the same focal (connecting) appliance. An alternative is to split the endpoints across multiple user accounts on multiple servers.  


Select **Next**.


## Edit a System Description  
You can edit an existing system description for the Custom Properties App.  

To edit a system description:  

Select an existing system description and select **Edit**.  

There are tabs for each pane. You can edit the settings in the Custom Properties, Time Format, DNS Short Name, and Assign CounterACT Devices tabs.  

Select **OK** to save the system description edits to the CounterACT Appliance.  

## Remove a System Description  
You can remove an existing system description.  

To remove a system description:  
Select an existing system description
Select **Remove**. A confirmation is displayed.  

**More** for details or **Ok**.  

## Test a System Description  
You can test a system description, which tests the Custom Properties App is able to resolve the desired properties. The app must be in the Running state.  

Also, the app must be saved before selecting **Test**. Select **OK** in the **System Description** dialog box and then select **Apply** in the **Connect** pane to save the system description. Please wait about 5-10 seconds after clicking apply.  

To test a system description:  

Select an existing system description
Select
**Test**.  
    If the functionaility of the system description has been tested successfully, a success message is displayed at the top of the dialog box. If the test failed, a failure message is displayed with a reason.  

**Close**.

## Properties
The Custom Properties App provides 4 new properties available for use in policies and actions.

- **Short DNS Name**: This provides the resolved Short DNS Name for a host if a DNS reverse lookup successfully retrieves an entry for the host. This can be used in policy or to send in actions, including integrations via any of the Forescout eyeExtend modules.
- **Current Time Formatted**: This provides a timestamp against a host set by an action. The formatted version of this property can be used in policies to identify timestamps *Older than* or *Before* a set time period or time.
- **Current Time**: This provides a timestamp against a host set by an action. This version of the property is provided as a string value which can be used in actions such as notifications, or as part of any integrations via any of the Forescout eyeExtend modules.
- **Active Network Adapter**: This property requires that the *Hardware Inventory > Network Adapter* property is resolved for devices first. This standard property retrieves all network adapter details discovered on a host. The custom property shortens this list to only provide the active network adapter details, as defined by a matching IP address, so that this information can easily be included in notifications or integrations.

## Actions
The Custom Properties App provides 1 new action available for use in policies or manually.

- **Set Current Time**: This action when triggered will take the current timestamp and apply that to the Current Time property against a host. This can be used to determine the exact time a host matched a policy which can assist in investigations or auditing. This action can be cancelled, removing the timestamp that is set.