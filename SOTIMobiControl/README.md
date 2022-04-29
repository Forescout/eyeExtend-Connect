# Forescout
eyeExtend Connect for SOTI MobiControl App README.md Version: 1.0.0

## Configuration Guide
**Version 1.0.0**
- Initial app providing basic visibility of devices and compliance status from SOTI MobiControl


## Contact Information  
- Have feedback or questions? Write to us at

**[connect-app-help@forescout.com](mailto:connect-app-help@forescout.com)**

## App Support

- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.

## About eyeExtend Connect App for SOTI MobiControl

# About This App

The SOTI MobiControl app provides visibility of devices, a wide selection of their associated properties, and their compliance status as reported by SOTI MobiControl

# What to Do  
To set up your system for integration with eyeExtend Connect for SOTI MobiControl, perform the following steps:  

1. Request an API account from SOTI
2. Configure a Username and Password for access
3. Download and install the module. See How to Install.  
4. Configure the module. See Configure the Module.  
5. Configure policy templates.  
6. Configure properties.  

# How to Install  
Get Forescout eyeExtend Connect plugin and SOTI MobiControl App from Forescout.  

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

## Configure SOTI MobiControl App
To configure eyeExtend Connect for SOTI MobiControl, you import the SOTI MobiControl App.

Initially, the App Configuration tab of the **Connect** pane is blank. The SOTI MobiControl App has not been imported yet.

## Import an App
You can import the SOTI MobiControl App.

To import the SOTI MobiControl App:

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

To configure the SOTI MobiControl App, you add a system description to define a connection, which includes login credentials.  

If a system description has not been configured and you select **OK** now, a warning message is displayed.  

Select **Add**

### SOTI MobiControl Connection


Enter the following information:  

- Server Address: Enter the SOTI MobiControl server IP address, FQDN or Hostname.
- Server Port: Enter the SOTI MobiControl server port. The default is TCP/443 
- Client ID: Enter the API Client ID provided by SOTI
- Client Secret: Enter and verify the API Client Secret provided by SOTI
- Username: Enter the username for accessing SOTI MobiControl
- Password: Enter and verify the password for accessing SOTI MobiControl

Select **Next**


### Focal Appliance


 - Initially, the Assign Forescout Focal Appliance panel has only one option, **Assign all devices by default** , and it is selected so that one device is added.

If you want to add a second device, the Assign Forescout Focal Appliance panel has more options.

Enter the following information:

- Connecting CounterACT Device: Select Enterprise Manager or an IP address of the connecting CounterACT device. In an environment where more than one CounterACT device is assigned to a single third-party instance, the connecting CounterACT Appliance functions as a middleman between the third-party instance and the CounterACT Appliance. The connecting CounterACT Appliance forwards all queries and requests to and from the third-party instance.  
- Assign specific devices: This CounterACT Appliance is assigned to a third-party instance, but it does not communicate with it directly. All communication between the third-party instance and its assigned CounterACT Appliance is handled by the connecting CounterACT Appliance defined for the third-party instance. All the IP addresses handled by an assigned Appliance must also be handled by the third-party instance to which the Appliance is assigned.  
  - Select **Available Devices** and then select an IP address or Appliance name from the Available Devices list.  
  - Select **Add**. The selected device will send its requests to the third-party instance through the connecting Appliance.  
- Assign all devices by default: This is the connecting Appliance to which CounterACT Appliances are assigned by default if they are not explicitly assigned to another connecting Appliance. Select this option to make this connecting Appliance the middleman for all CounterACT Appliances not assigned to another connecting device.  


Note the following:  

- An error message is displayed if you try to add a device that is already used.  
- If you have apps that discover 50,000 or more endpoints, distribute the apps in such a way so that only up to two of the apps share the same focal (connecting) appliance. An alternative is to split the endpoints across multiple user accounts on multiple servers.  


Select **Next**.

### Proxy Server


Enter the Proxy Server information similar to any Forescout Extend Module:  

Select **Next**.  

### MobiControl Options

- Enable Host Discovery: Select this option to enable the **Discovery Frequency** field.

- Discovery Frequency: Select a value for the frequency of host discovery, which is the interval between discoveries. The default is 60 minutes.

- Add Hosts without IP: Select this to allow the SOTI MobiControl Connect App to discover and add devices with only a Mac Address, and no IP Address, into Forescout. The default is to only add devices with an in-scope IP address.

- Number of API queries per second: Select a value for the rate limiter. The default is 100 request per second. You can rate limit the requests sent to the third-party server. The rate limiter specifies the number of times a script is invoked during the specified time. It is triggered when the app starts.

- Authorization Interval: Set the interval to refresh the token. The default interval is to refresh every 58 minutes, as the SOTI MobiControl default token timeout is 60 minutes.

## Edit a System Description  
You can edit an existing system description for the SOTI MobiControl App.  

To edit a system description:  

Select an existing system description and select **Edit**.  

There are tabs for each pane. You can edit the settings in the SOTI MobiControl Connection, Assign Forescout Focal Appliance, Proxy Server, and MobiControl Options tabs.  

Select **OK** to save the system description edits to the CounterACT Appliance.  

## Remove a System Description  
You can remove an existing system description.  

To remove a system description:  
Select an existing system description
Select **Remove**. A confirmation is displayed.  

**More** for details or **Ok**.  

## Test a System Description  
You can test a system description, which tests the connection of the SOTI MobiControl App to the SOTI MobiControl server. The app must be in the Running state.  

Also, the app must be saved before selecting **Test**. Select **OK** in the **System Description** dialog box and then select **Apply** in the **Connect** pane to save the system description. Please wait about 5-10 seconds after clicking apply.  

To test a system description:  

Select an existing system description
Select
**Test**.  
    If the connectivity of the system description has been tested successfully, a success message is displayed at the top of the dialog box. If the test failed, a failure message is displayed with a reason.  

**Close**.