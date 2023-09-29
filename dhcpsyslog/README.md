# Forescout
eyeExtend Connect DHCP SysLog Receiver App README.md Version: 1.0.0

## Configuration Guide
**Version 1.0.0**
- Initial App to receive dhcpd logs via Syslog


## Contact Information  
- Have feedback or questions? Write to us at

**[connect-app-help@forescout.com](mailto:connect-app-help@forescout.com)**

## App Support

- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.

## About eyeExtend Connect DHCP SysLog Receiver App

# About This App

The eyeExtend Connect DHCP SysLog Receiver App provides functionality to receive dhcpd logs via Syslog, and extract host IP and MAC Address from this for extended visibility in the Forescout platform.

A standard dhcpd log will contain DHCPDISCOVER, DHCPOFFER, DHCPREQUEST and DHCPACK log messages which can all be sent via Syslog. This app only utilises the DHCPACK message, specifically in the format:

`DHCPACK on 1.1.1.1 to aa:bb:cc:dd:ee:ff (hostname) via eth0`

# What to Do  
To set up your system for using the eyeExtend Connect DHCP SysLog Receiver App, perform the following steps:  

1. Download and install the module. See How to Install.  
2. Configure the module. See Configure the Module.  
3. Configure policy templates.  
4. Configure properties.  
5. Configure actions.  

# How to Install  
Get Forescout eyeExtend Connect plugin and DHCP SysLog Receiver App from Forescout.  

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

## Configure DHCP SysLog Receiver App
To configure eyeExtend Connect DHCP SysLog Receiver App, you import the DHCP SysLog Receiver App.

Initially, the App Configuration tab of the **Connect** pane is blank. The DHCP SysLog Receiver App has not been imported yet.

## Import an App
You can import the DHCP SysLog Receiver App.

To import the DHCP SysLog Receiver App:

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

To configure the DHCP SysLog Receiver App, you add a system description to define a configuration.  

If a system description has not been configured and you select **OK** now, a warning message is displayed.  

Select **Add**

### DHCP SysLog Receiver


On this panel, enter a name for the Syslog Source to be used. This name is only for identification purposes within the Forescout platform.

Select **Next**


### Assign Forescout Devices


 - Initially, the Assign Forescout Devices panel has only one option, **Assign all devices by default** , and it is selected so that one device is added.

If you want to add a second device, the Assign Forescout Devices panel has more options.

Enter the following information:

- Connecting Forescout Device: Select Enterprise Manager or an IP address of the connecting Forescout device. This is the device which will receive syslog messages.  
- Assign specific devices: This Forescout Appliance is assigned to the connecting Forescout device for receiving syslog via this Connect App.
  - Select **Available Devices** and then select an IP address or Appliance name from the Available Devices list.  
  - Select **Add**. The selected device will send its requests to the connecting Appliance.  
- Assign all devices by default: This is the connecting Appliance to which Forescout Appliances are assigned by default if they are not explicitly assigned to another connecting Appliance. Select this option to make this connecting Appliance the appliance to receive syslog for all Forescout Appliances not assigned to another connecting device.


Note the following:  

- An error message is displayed if you try to add a device that is already used.  
- If you have apps that discover 50,000 or more endpoints, distribute the apps in such a way so that only up to two of the apps share the same focal (connecting) appliance. An alternative is to split the endpoints across multiple user accounts on multiple servers.  


Select **Next**.

### Syslog Source


On this panel, enable the Syslog Source and specify the source name or IP that Forescout will receive syslog messages from. Only syslog messages received from this source will be processed by the app, all other syslog messages will be ignored.

Select **Finish**

## Edit a System Description  
You can edit an existing system description for the DHCP SysLog Receiver App.  

To edit a system description:  

Select an existing system description and select **Edit**.  

There are tabs for each pane. You can edit the settings in the DHCP SysLog Receiver, Assign Forescout Devices, and Syslog Source tabs.  

Select **OK** to save the system description edits to the Forescout Appliance.  

## Remove a System Description  
You can remove an existing system description.  

To remove a system description:  
Select an existing system description
Select **Remove**. A confirmation is displayed.  

**More** for details or **Ok**.  
