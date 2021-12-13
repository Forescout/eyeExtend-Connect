# Forescout
eyeExtend Connect for KaseyaVSA App README.md Version: 3.0.1

## Configuration Guide
**Version 3.0.0**
- Added OAuth 2.0 authentication mechanism

**Version 3.0.1**
- Resolved issue with proxy usage

**Version 3.0.2**
- Updated Server Certificate Validation functionality

## Contact Information  
- Have feedback or questions? Write to us at

**[connect-app-help@forescout.com](mailto:connect-app-help@forescout.com)**

## App Support

- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.

## About eyeExtend Connect App for KaseyaVSA

# About This App

Version 3 of the KaseyaVSA App has now added the ability to work with either Basic or OAuth 2.0 authentication mechanisms.

Basic Authentication allows for obtaining an access token with Username and Password only.

OAuth 2.0 Authentication allows for obtaining an access token using Client ID, Client Secret, Redirect URI and an Authorization Code. This also obtains a refresh token to update the access token on a regular interval.

# What to Do  
To set up your system for integration with eyeExtend Connect for KaseyaVSA, using OAuth 2.0 authentication, perform the following steps:  

1. Register Forescout as an OAuth Client within the KaseyaVSA Management Server.  
2. Obtain an Authorization Code through a browser. Refer to Kaseya [Using OAuth 2.0 to Access VSA APIs](https://help.kaseya.com/webhelp/EN/RESTAPI/9050000/UsingOAuth2.0toAccessVSAAPIs.pdf)
3. Download and install the module. See How to Install.  
4. Configure the module. See Configure the Module.  
5. Configure policy templates. See Configure KaseyaVSA Policy Templates.  
6. Configure properties. See Configure Properties.  
7. Configure actions. See Configure Actions.  

# How to Install  
Get Forescout eyeExtend Connect plugin and KaseyaVSA App from Forescout.  

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

## Configure KaseyaVSA App
To configure eyeExtend Connect for KaseyaVSA, you import the KaseyaVSA App.

Initially, the App Configuration tab of the **Connect** pane is blank. The KaseyaVSA App has not been imported yet.

## Import an App
You can import the KaseyaVSA App.

To import the KaseyaVSA App:

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

To configure the KaseyaVSA App, you add a system description to define a connection, which includes login credentials.  

If a system description has not been configured and you select **OK** now, a warning message is displayed.  

Select **Add**

### Kaseya VSA Server Connection


Enter the following information:  

- VSA Server IP Address: Enter the KaseyaVSA server IP address.
- VSA Server Port: Enter the KaseyaVSA server port. The default is TCP/443 
- Connection Type: Specify the connection method which will be used for authentication.


Select **Next**

### Kaseya VSA Basic Authentication


When using **Basic Authentication**, enter the required credentials.


- Username
- Password


Select **Next**.

### Kaseya VSA OAuth 2.0


When using **OAuth 2.0**, some manual action is required for authentication.

When configuring the App for the first time, or when the App is unavailable longer than the refresh time, an Authorization Code must be manually obtained and provided. Following this, the refresh token will be used to renew authenticated access.

The required parameters must be entered ***exactly*** as entered when registering the OAuth Client in KaseyaVSA. The Authorization Code obtained must be entered and the plugin configuration applied within 5 minutes of obtaining the code.

- Client ID
- Client Secret
- Authorization Code
- Redirect URL


Select **Next**

### Focal Appliance


 - Initially, the Assign CounterACT Devices panel has only one option, **Assign all devices by default** , and it is selected so that one device is added.

If you want to add a second device, the Assign CounterACT Devices panel has more options.

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

### Kaseya VSA Options

- Enable Host Discovery: Select this option to enable the **Discovery Frequency** field.

- Discovery Frequency: Select a value for the frequency of host discovery, which is the interval between discoveries. The default is 60 minutes.

- Authorization Interval: Set the interval to refresh the token, for OAuth the Kaseya token expires every 30 mins by default. The default interval is to refresh every 28 minutes.

- Number of API queries per second: Select a value for the rate limiter. The range is from 1 to 1000 requests per second. The default is 100 request per second. You can rate limit the requests sent to the third-party server. The rate limiter specifies the number of times a script is invoked during the specified time. It is triggered when the app starts.


## Edit a System Description  
You can edit an existing system description for the KaseyaVSA App.  

To edit a system description:  

Select an existing system description and select **Edit**.  

There are tabs for each pane. You can edit the settings in the Kaseya VSA Server Connection, Kaseya VSA Basic Authentication, Kaseya VSA OAuth 2.0, Assign CounterACT Devices, Proxy Server, and Kaseya VSA Options tabs.  

Select **OK** to save the system description edits to the CounterACT Appliance.  

## Remove a System Description  
You can remove an existing system description.  

To remove a system description:  
Select an existing system description
Select **Remove**. A confirmation is displayed.  

**More** for details or **Ok**.  

## Test a System Description  
You can test a system description, which tests the connection of the KaseyaVSA App to the KaseyaVSA server. The app must be in the Running state.  

Also, the app must be saved before selecting **Test**. Select **OK** in the **System Description** dialog box and then select **Apply** in the **Connect** pane to save the system description. Please wait about 5-10 seconds after clicking apply.  

To test a system description:  

Select an existing system description
Select
**Test**.  
    If the connectivity of the system description has been tested successfully, a success message is displayed at the top of the dialog box. If the test failed, a failure message is displayed with a reason.  

**Close**.