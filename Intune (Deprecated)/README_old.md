# Forescout  
eyeExtend for Intune App README.md Version: 1.0.0  
  
## Configuration Guide  
**Version 1.0.0**  
  
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
© 2020 Forescout Technologies, Inc. All rights reserved. Forescout Technologies, Inc. is a Delaware corporation. A list of our trademarks and patents can be found at [https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks](https://urldefense.proofpoint.com/v2/url?u=https-3A__www.forescout.com_company_legal_intellectual-2Dproperty-2Dpatents-2Dtrademarks&amp;d=DwMFAg&amp;c=L5E2d05je37i-dadkViuXA&amp;r=Z3cI4QPLlfMimB_63ipHyFuWSHGqqAs50hjX-2X1CEw&amp;m=ypFjb5tb21hH81CxdGe-3FT8l4QXZe-hzuDh-eBT-wQ&amp;s=ATQ1mJb4KkN8L9fn2BnpRuwmDWJcze7zyqTbG1PTwkc&amp;e=). Other brands, products, or service names may be trademarks or service marks of their respective owners.  
  
# About eyeExtend for Intune
  
  
# Customer Support  
The Connect Plugin is supported by Forescout Customer Support. See [https://forescout.force.com/support/s/](https://forescout.force.com/support/s/).  
  
Connect Apps, including those provided by Forescout, are not supported by Forescout.  
  
# About This Module  
  
  
# Use Cases  
This section describes important use cases supported by Forescout eyeExtend for Intune.  
  
## Intune Device Enrollment Policy  
  Use this policy template to detect corporate hosts not enrolled with the Intune service, and prompt host users to enroll.  
Corporate hosts are defined as hosts that have authenticated via the HTTP Login action or have enrolled through Company Portal on their device.  
By default, users cannot browse the Internet until enrollment is complete.  
A restrictive action blocks corporate network access to users not enrolled.  
This action is disabled by default.
  
## Intune Offsite Device Enrollment Policy
Use this policy template to discover and classify offsite devices on Intune. The policy template adds all offsite devices to the Intune Offsite Devices group. It also classifies offsite devices based on the Operating Systems reported by Intune, and puts them into OS groups

## Intune Device Compliance
Use this policy template to detect corporate hosts not enrolled with the Intune service, and prompt host users to enroll.  
Corporate hosts are defined as hosts that have authenticated via the HTTP Login action or have enrolled through Company Portal on their device.  
By default, users cannot browse the Internet until enrollment is complete.  
A restrictive action blocks corporate network access to users not enrolled.  
This action is disabled by default.  
  
# How It Works  
The following Intune components are required for this integrated solution:  
  
- **Microsoft Graph API:** The Forescout platform addresses the API exposed by the platform to retrieve endpoint information and perform actions.  
  
The following Forescout platform components support the integration:  
  
- **Forescout eyeExtend for Intune:** This cloud-delivered module handles communication with Intune and provides the properties, actions, and policies described in this guide.  
- **Forescout eyeExtend Cloud:** A Forescout cloud service that handles third-party integrations including the integration with Intune, which provides the endpoint properties and actions described in this guide.  
- **Forescout eyeExtend Connect Plugin:** An infrastructure for integrating third-party vendors with the Forescout platform.  
- **Forescout eyeExtend Intune App:** The Connect App developed by Forescout to implement the integration with Intune.  
  
In a typical deployment, several cloud connections are defined in the Forescout platform. Connections to the cloud may be planned based on anticipated traffic or geographic location. The deployment is as follows:  
  
- A single CounterACT® device connects to each cloud access point, handling communication for a cluster of CounterACT devices. The CounterACT devices in the cluster only work with that Intune cloud instance.  
- For each connection, the rate limiting of messaging from the Forescout platform to the Intune cloud can be configured.
  
# What to Do  
To set up your system for integration with eyeExtend for Intune, perform the following steps:  
  
1. Verify that the requirements are met. See Requirements.  
2. Download and install the module. See How to Install.  
3. Configure the module. See Configure the Module.  
4. Configure policy templates. See Configure Intune Policy Templates.  
5. Configure properties. See Configure Properties.  
6. Configure actions. See Configure Actions.  
  
# Requirements  
- Forescout version 8.1.4, 8.2.1
- Forescout eyeExtend for Microsoft Intune requires the following:
	- An Azure online account for you to log in to https://portal.azure.com/.
	- For information about the vendor models (hardware/software) and versions (product/OS) that are validated for integration with this Forescout component, refer to the [Forescout Compatibility Matrix]([https://www.forescout.com/company/resources/forescout-compatibility-matrix/](https://www.forescout.com/company/resources/forescout-compatibility-matrix/)).

Note that eyeExtend for Microsoft Intune acquires the authorization token and query device information through the following URLs. You can whitelist them to allow access.
* https://login.microsoftonline.com/
* https://graph.microsoft.com/
  
# How to Install  
Get Forescout eyeExtend Connect plugin and Intune App from Forescout.  
  
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
  
# Create User and Application  
  
* On Azure Active Directory (AAD), you need to:  
  * Create a user account and assign it a role.  
  * Create an application and assign it an owner.  
      
Before the Forescout platform can authenticate against an Intune account via the service principal (the application), you need to perform the following procedures to register an application and service principal on AAD, as well as ensure that you have the required role, permissions, and owner.  
You can obtain the Directory (Tenant) ID and Application (Client) ID from the Azure portal.    
  
#### **Create a New User**
   1. Go to https://portal.azure.com/ and log in to your account.  
   2. Select **Azure Active Directory > Users**  
 3. Select **New User**  
 4. Enter the required information  
      - Name: The of the user, for example: New User  
      - User name: The user name of the user, for example: New.User@domain.onmicrosoft.com  
       - **Tip**: To find your domain, which ends in onmicrosoft.com, go to Azure Active Directory > Overview  
   5. A temporary password is generated for the user account.  
   6. Click **Show Password** and copy the temporary password.  
   7. Select **Create**  
  8. Recommendation: In another browser session, open a New incognito window, log in with the new user and temporary password, then change the password.
#### Assign Intune Administrator Role  
   1. Select **Azure Active Directory > Users**  
 2. Locate the new user you created and select it by clicking the user name  
   3. Select **Directory role**  
 4. Select **Add assignment**  
 5. Select **Intune administrator**  
 6. Select **Select**  
#### Check AAD Permissions  
   1. Select **Azure Active Directory > User settings**  
 2. Check the setting of **App registrations**  
 3. If **App registrations** is set to **Yes**, any user in the AAD tenant, including a non-admin user, can register an app.  
   4. If **App registrations** is set to **No**, only global administrators can register AD apps. Check if your account is an admin for the AAD tenant. Select **Overview** and view your user information. If your account is assigned to the User role, but the setting of **App registrations** is limited to admin users, ask your administrator to assign you to the global administrator role or to enable users to register apps.  
#### Create an AAD Application  
   1. Select **Azure Active Directory > App registrations.**  
 2. Select **New registration.**  
 3. Enter the **Name** for the application, for example, fs-intune-plugin-app.  
     - *The application name must be unique across an Azure region*  
	 - *The Redirect URI is not used in the Intune integration*  
 4. Select **Register** and review the application details in **Overview**.  
   5. Select **Authentication** and scroll to **Default client type**  
 6. For Default client type, select **Yes** to treat application as a public client.  
   7. Select **Save**  
#### Assign Graph API Permissions  
   1. Select **Azure Active Directory > App registrations.**  
 2. Select the app you created, for example, fs-intune-plugin-app.  
   3. Select **API permissions.**  
 4. Select **Microsoft Graph** and then select **Delegated permissions**.  
   5. In **Type to search**, type DeviceManagementManagedDevices.  
   6. Select the following two graph API permissions:  
       - DeviceManagementManagedDevices.PrivilegedOperations.All to perform user-impacting remote actions on Microsoft Intune devices  
       - DeviceManagementManagedDevices.Read.All to read Microsoft Intune devices  
   7. Select **Update permissions**. The API permissions are displayed.  
   8. Select **Grant admin consent for Forescout.**  
 9. Select **Yes.** The API permissions are displayed.  
#### Assign the App an Owner  
   1. Select **Azure Active Directory > App registrations.**  
 2. Select the app you created, for example, fs-intune-plugin-app, and select **Owners.**  
 3. Note that the new user is not in the list.  
   4. Select **Add owner.**  
 5. Select the new user and select **Select.**  
####  Obtain tenant ID, application ID, and application secret:  
   1. Select **Azure Active Directory > App Registrations**  
 2. Select your application, for example, fs-intune-plugin-app  
   3. The information is displayed.  
   4. Copy the **Application ID** and store it in your application code. The application ID is also referred to as the client ID.  
   5. Copy the **Directory (Tenant) ID.** Include it with your authentication request.  
  
# Configure the Module  
After eyeExtend Connect is installed, **Connect** is displayed under **Options**.  
  
  
## Configure Intune App  
To configure eyeExtend for Intune, you import the Intune App and then add a system description.  
  
Initially, the App Configuration tab of the **Connect** pane is blank. The Intune App has not been imported yet and the system description has not been configured yet.  
  
## Import an App  
You can import the Intune App.  
  
To import the Intune App:  
  
1. In the App Configuration tab of the **Connect** pane, select **Import**.  
2. Apps that can be imported are in .zip or .eca format. They can be in any folder.  
3. Select **Import**.  
If the app is imported successfully, a message is displayed at the bottom of the **Sending** dialog box. If the app is not imported successfully, error messages are displayed in the **Sending** dialog box.  
4. Select **Close** when the import has finished. A blank **System Description** dialog box opens. See Add a System Description.  
  
- If you select **Close** before the import has finished, it will fail.  
  
## Add a System Description  
To configure the Intune App, you add a system description to define a connection, which includes login credentials.  
  
To add the system description:  
  
1. After the app is imported, the **System Description** dialog box opens. It is initially blank and only the **Add** and **Import** buttons are enabled.  
  
If a system description has not been configured and you select **OK** now, a warning message is displayed.  
1. Select **Add**.  
2. Enter the following information:  
  
- Tenant ID:  Enter the account tenant ID. See Obtain Tenant ID, Application ID and Secret.  
- Application ID: Enter the account application ID. See Obtain Tenant ID, Application ID and Secret.  
- Description: Enter a description for the Intune account.  
- User: Enter the username for the Intune account.  
- Password: Enter the password for the Intune account.  
  
3. Select **Next**.  
 - Initially, the Assign CounterACT Devices panel has only one option, **Assign all devices by default** , and it is selected so that one device is added.  
If you want to add a second device, the Assign CounterACT Devices panel has more options.  
5. Enter the following information:  
- Connecting CounterACT Device: Select Enterprise Manager or an IP address of the connecting CounterACT device. In an environment where more than one CounterACT device is assigned to a single third-party instance, the connecting CounterACT Appliance functions as a middleman between the third-party instance and the CounterACT Appliance. The connecting CounterACT Appliance forwards all queries and requests to and from the third-party instance.  
- Assign specific devices: This CounterACT Appliance is assigned to a third-party instance, but it does not communicate with it directly. All communication between the third-party instance and its assigned CounterACT Appliance is handled by the connecting CounterACT Appliance defined for the third-party instance. All the IP addresses handled by an assigned Appliance must also be handled by the third-party instance to which the Appliance is assigned.  
  - Select **Available Devices** and then select an IP address or Appliance name from the Available Devices list.  
  - Select **Add**. The selected device will send its requests to the third-party instance through the connecting Appliance.  
- Assign all devices by default: This is the connecting Appliance to which CounterACT Appliances are assigned by default if they are not explicitly assigned to another connecting Appliance. Select this option to make this connecting Appliance the middleman for all CounterACT Appliances not assigned to another connecting device.  
  
Note the following:  
  
- An error message is displayed if you try to add a device that is already used.  
- If you have apps that discover 50,000 or more endpoints, distribute the apps in such a way so that only up to two of the apps share the same focal (connecting) appliance. An alternative is to split the endpoints across multiple user accounts on multiple servers.  
  
6. Select **Next**.  
7. Enter the Proxy Server information similar to any Forescout Extend Module:  
8. Select **Next**.  
9. Enter the following information:  
- Enable Host Discovery: Select this option to enable the **Discovery Frequency** field.  
- Discovery Frequency: Select a value for the frequency of host discovery, which is the interval between discoveries. The range is from 1 minute to 72 minutes. The default is 8 minutes.  
- Number of API queries per unit time: Select a value for the rate limiter. The range is from 1 to 100 requests per second. The default is 1 request per second. You can rate limit the requests sent to the third-party server. The rate limiter specifies the number of times a script is invoked during the specified time. It is triggered when the app starts.  
10. Select **Finish**. The configured system description is displayed in the **System Description** dialog box.  
  
When the system description is selected, all the buttons on the dialog box are enabled.  
  
You can create multiple system descriptions. To add another system description, select **Add** and repeat the procedure for Add a System Description.  
  
11. Select **OK** to save the system description to the CounterACT Appliance. The system description is displayed in the App Configuration tab of the **Connect** pane. There are several default columns. See Connect Pane Details.  
  
## Edit a System Description  
You can edit an existing system description for the Intune App.  
  
To edit a system description:  
  
1. Select an existing system description and select **Edit**.  
There are tabs for each pane. You can edit the settings in the Intune Connection, Assign CounterACT Devices, Proxy Server, and Intune Options tabs.  
2. Select **OK** to save the system description edits to the CounterACT Appliance.  
  
## Remove a System Description  
You can remove an existing system description.  
  
To remove a system description:  
1. Select an existing system description and select **Remove**. A confirmation is displayed.  
2. Select **More** for details or select **Ok**.  
  
## Test a System Description  
You can test a system description, which tests the connection of the Intue App to the Intune server. The app must be in the Running state.  
  
Also, the app must be saved before selecting **Test**. Select **OK** in the **System Description** dialog box and then select **Apply** in the **Connect** pane to save the system description. Please wait about 5-10 seconds after clicking apply.  
  
To test a system description:  
  
1. Select an existing system description and select **Test**.  
If the connectivity of the system description has been tested successfully, a success message is displayed at the top of the dialog box. If the test failed, a failure message is displayed with a reason.  
2. Select **Close**.  
  
# Configure Intune Policy Templates  
There are three Intune policy templates for customers to manage devices in an Intune environment, detect devices that are compliant or non-compliant, and devices that are enrolled or not.  
  
- Intune Device Enrollment  
- Intune Offsite Device Enrollment  
- Intune Device Compliance  
  
## Add Intune Policies  
To configure an Intune policy:  
  
1. In the Forescout Console, select **Policy**.  
2. Select **Add** , search for Intune, and expand the **Intune** folder.  
3. Select **Intune Device Enrollment**, **Intune Offsite Device Enrollment** or **Intune Device Compliance**.  
  
# Intune Properties  
Intune properties are available to be used in a policy.  
  
The following properties are available:  
  
- **Intune Device AAD ID**: Indicates the unique identifier (read-only) for the Azure Active Directory (AAD) device.  
- **Intune Device Compliance State**: Indicates the compliance state of the device. The possible values are:  
  - Compliant  
  - Conflicts with other rules  
  - Device is non-compliant and is blocked from corporate resources  
  - Error  
  - In grace period  
  - Managed by configuration manager  
  - Unknown.  
- **Intune Device Enrolled DateTime**: Indicates the date and time when the device was enrolled.  
- **Intune Device ID**: Indicates the unique identifier of the device.  
- **Intune Device is Jail Broken**: Indicates whether a device is jailbroken. The possible values are:  
  - False  
  - True  
  - Unknown.  
- **Intune Device is Registered in AAD**: Indicates whether the device is registered in the AAD.  
- **Intune Device is Supervised**: Indicates the supervised status of the device.  
- **Intune Last Sync DateTime**: Indicates the date and time when the device last completed a successful synchronization with Intune.  
- **Intune Device Manufacturer**: Indicates the manufacturer of the device.  
- **Intune Device Model**: Indicates the model of the device.  
- **Intune Device Name**: Indicates the name of the device.  
- **Intune Device Operating System**: Indicates the operating system of the device, such as Windows or iOS.  
- **Intune Device Operating System Version**: Indicates the operating system version of the device.  
- **Intune Device Reported Threat State**: Indicates the (read-only) threat state of a device with a Mobile Threat Defense partner in use by the account and device. The possible values are:  
  - Activated  
  - Compromised  
  - Deactivated  
  - High Severity  
  - Low Severity  
  - Medium Severity  
  - Misconfigured  
  - Secure  
  - Unknown  
  - Unresponsive.  
- **Intune Device Serial Number**: Indicates the serial number of the device.  
- **Intune Directory ID**: Indicates the directory ID of the source Intune account.  
- **Intune Managed Device Owner Type**:   
- **Intune Device Wi-Fi MAC**: Indicates the Wi-Fi MAC address of the device.  
- **Intune IMEI**: Indicates the International Mobile Equipment Identity (IMEI), which is a unique number that identifies all mobile phones and smart phones.  
- **Intune MEID**: Indicates the mobile equipment identifier (MEID), which is a unique number that identifies a mobile device.  
- **Intune Device Email Address**: Indicates one or more email addresses for the user associated with the device.  
- **Intune Device Phone Number**: Indicates the phone number of the device.  
- **Intune Device User Display Name**: Indicates the user display name of the device.  
- **Intune Device User ID**: Indicates the unique identifier of the user associated with the device.  
  
# Intune Actions  
Intune actions are available to be used in a policy.  
  
To access the Intune actions:  
  
1. When configuring a policy, select **Add** in the Actions section of the Main Rule or Sub-Rule dialog box.  
2. Search for Intune.  
3. Select an action in the **Intune** folder.  
  
The following action is available:  
- **Remote Lock**:  Locks down a managed endpoint.  
- **Wipe Device**: Factory resets a managed endpoint.  
  
# Scripts  
There are a few Python scripts.  
- **intune_poll.py** User can enable discovery on a specified period to poll endpoint properties.  
- **intune_test.py** User can test the connection to the Intune server.  
- **intune_resolve.py** User can get the Intune endpoint properties.  
- **intune_remote_lock_managed_device.py** User can issue a request to the Intune server to lock a specific managed endpoint.  
- **intune_wipe_managed_device.py** User can issue a request to the Intune server to wipe a specific managed endpoint.
- **intune_authorization.py** User can fetch an Intune REST API authorization token for a specific interval.