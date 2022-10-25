# Forescout  
eyeExtend for VMware Workspace ONE App README.md Version: 1.0.0  

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

# About eyeExtend for Workspace ONE


# Customer Support  
The Connect Plugin is supported by Forescout Customer Support. See [https://forescout.force.com/support/s/](https://forescout.force.com/support/s/).  

Connect Apps, including those provided by Forescout, are not supported by Forescout.  

# About This Module  


# Use Cases  
This section describes important use cases supported by Forescout eyeExtend for Workspace ONE.  

## Workspace ONE Device Compliance Policy
Use this policy template to detect non-compliant corporate devices, and redirect non-complaint users to a notification message that indicates:
-Why the device is not-compliant
-Network access limitations
-Steps for remediation
By default, users cannot browse the Internet until they become compliant. A restrictive action that blocks corporate network access to non-compliant users is available. This action is disabled by default.

## Workspace ONE Device Enrollment Policy
Use this policy template to detect corporate hosts not enrolled with the Workspace ONE service, and prompt host users to enroll. Corporate hosts are defined as hosts that have authenticated via the HTTP Login action or have enabled the MDM Profile on their device. By default, users cannot browse the Internet until enrollment is complete. A restrictive action that blocks corporate network access to users not enrolled is available. This action is disabled by default.


# How It Works  
The following Workspace ONE components are required for this integrated solution:

The following Forescout platform components support the integration:  

- **Forescout eyeExtend for Workspace ONE:** This cloud-delivered module handles communication with Workspace ONE and provides the properties, actions, and policies described in this guide.  
- **Forescout eyeExtend Cloud:** A Forescout cloud service that handles third-party integrations including the integration with Workspace ONE, which provides the endpoint properties and actions described in this guide.  
- **Forescout eyeExtend Connect Plugin:** An infrastructure for integrating third-party vendors with the Forescout platform.  
- **Forescout eyeExtend Workspace ONE App:** The Connect App developed by Forescout to implement the integration with Workspace ONE.  

In a typical deployment, several cloud connections are defined in the Forescout platform. Connections to the cloud may be planned based on anticipated traffic or geographic location. The deployment is as follows:  

- A single CounterACT® device connects to each cloud access point, handling communication for a cluster of CounterACT devices. The CounterACT devices in the cluster only work with that Workspace ONE cloud instance.  
- For each connection, the rate limiting of messaging from the Forescout platform to the Workspace ONE cloud can be configured.

# What to Do  
To set up your system for integration with eyeExtend for Workspace ONE, perform the following steps:  

1. Verify that the requirements are met. See Requirements.  
2. Download and install the module. See How to Install.  
3. Configure the module. See Configure the Module.  
4. Configure policy templates. See Configure Workspace ONE Policy Templates.  
5. Configure properties. See Configure Properties.  
6. Configure actions. See Configure Actions.  

# Requirements  
- Forescout version 8.1.4, 8.2.2
- eyeExtend Connect Plugin version 1.8.0
- Forescout eyeExtend for Workspace ONE requires the following:
  - An online account on Workspace ONE UEM.
  - For information about the vendor models (hardware/software) and versions (product/OS) that are validated for integration with this Forescout component, refer to the [Forescout Compatibility Matrix]([https://www.forescout.com/company/resources/forescout-compatibility-matrix/](https://www.forescout.com/company/resources/forescout-compatibility-matrix/)).

# How to Install  
Get Forescout eyeExtend Connect plugin and Workspace ONE App from Forescout.  

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


## Configure Workspace ONE App  
To configure eyeExtend for Workspace ONE, you import the Workspace ONE App and then add a system description.  

Initially, the App Configuration tab of the **Connect** pane is blank. The Workspace ONE App has not been imported yet and the system description has not been configured yet.  

## Import an App  
You can import the Workspace ONE App.  

To import the Workspace ONE App:  

1. In the App Configuration tab of the **Connect** pane, select **Import**.  
2. Apps that can be imported are in .zip or .eca format. They can be in any folder.  
3. Select **Import**.  
If the app is imported successfully, a message is displayed at the bottom of the **Sending** dialog box. If the app is not imported successfully, error messages are displayed in the **Sending** dialog box.  
4. Select **Close** when the import has finished. A blank **System Description** dialog box opens. See Add a System Description.  

- If you select **Close** before the import has finished, it will fail.  

## Add a System Description  
To configure the Workspace ONE App, you add a system description to define a connection, which includes login credentials.  

To add the system description:  

After the app is imported, the **System Description** dialog box opens. It is initially blank and only the **Add** and **Import** buttons are enabled.  

If a system description has not been configured and you select **OK** now, a warning message is displayed.  
1. Select **Add**.  
2. Enter the following information:  

- Workspace ONE Server URL: Enter the URL for the Workspace ONE instance, excluding the protocol. E.g. 12345.awmdm.com.  
- User: Enter the username for the Workspace ONE UEM account.  
- Password: Enter the password for the Workspace ONE UEM account.  
- Workspace ONE API Key: Enter the API for the Workspace ONE UEM account.

3. Select **Next**.  
4. Initially, the Assign CounterACT Devices panel has only one option, **Assign all devices by default** , and it is selected so that one device is added.  
 - If you want to add a second device, the Assign CounterACT Devices panel has more options.  
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
7. Enter the Proxy Server information similar to any Forescout Extended Module:
- Proxy Server IP address
- Proxy Server Port
- Proxy Server Username (if applicable/ authentication required)
- Proxy Server Password (if applicable/ authentication required)

8. Select **Next**.  
9. Enter the following information:  
- Enable Host Discovery: Select this option to enable the **Discovery Frequency** field.  
- Discovery Frequency: Select a value for the frequency of host discovery, which is the interval between discoveries. The range is from 1 minute to 2880 minutes (48 hours). The default is 1440 minutes (every 24 hours).  
- MDM Query Threshold Interval: Specify how often (in seconds) the module should query the Workspace ONE service. The range is from 1 to 1000 seconds; the default is every 10 seconds. You can rate limit the frequency in which requests are sent to the third-party server. The rate limiter specifies the number of times a script is invoked during the specified time. It is triggered when the app starts.  
10. Select **Finish**. The configured system description is displayed in the **System Description** dialog box.  

When the system description is selected, all the buttons on the dialog box are enabled.  

You can create multiple system descriptions. To add another system description, select **Add** and repeat the procedure for Add a System Description.  

11. Select **OK** to save the system description to the CounterACT Appliance. The system description is displayed in the App Configuration tab of the **Connect** pane. There are several default columns. See Connect Pane Details.  

## Edit a System Description  
You can edit an existing system description for the Workspace ONE App.  

To edit a system description:  

1. Select an existing system description and select **Edit**.  
There are tabs for each pane. You can edit the settings in the Workspace ONE Connection, Assign CounterACT Devices, Proxy Server, and Workspace ONE Options tabs.  
2. Select **OK** to save the system description edits to the CounterACT Appliance.  

## Remove a System Description  
You can remove an existing system description.  

To remove a system description:  
1. Select an existing system description and select **Remove**. A confirmation is displayed.  
2. Select **More** for details or select **Ok**.  

## Test a System Description  
You can test a system description, which tests the connection of the Intue App to the Workspace ONE server. The app must be in the Running state.  

Also, the app must be saved before selecting **Test**. Select **OK** in the **System Description** dialog box and then select **Apply** in the **Connect** pane to save the system description. Please wait about 5-10 seconds after clicking apply.  

To test a system description:  

1. Select an existing system description and select **Test**.  
If the connectivity of the system description has been tested successfully, a success message is displayed at the top of the dialog box. If the test failed, a failure message is displayed with a reason.  
2. Select **Close**.  

# Configure Workspace ONE Policy Templates  
There are three Workspace ONE policy templates for customers to manage devices in an Workspace ONE environment, detect devices that are compliant or non-compliant, and devices that are enrolled or not.  

- MDM Classification (Enrollment Step-1)
- Workspace ONE Device Enrollment (Enrollment Step-2)
- Workspace ONE Device Compliance  

## Add Workspace ONE Policies  
To configure an Workspace ONE policy:  

1. In the Forescout Console, select **Policy**.  
2. Select **Add** , search for Workspace ONE, and expand the **Workspace ONE** folder.  
3. Select **Enrollment Step-1: MDM Classification** and **Enrollment Step-2: Workspace ONE Device Enrollment**, or **Workspace ONE Device Compliance**.  

# Workspace ONE Properties  
Workspace ONE properties are available to be used in a policy.  

The following properties are available:  

- **Workspace ONE Device ID**: Indicates the unique identifier for the Workspace ONE endpoint.  
- **Workspace ONE Compliance Status**: Indicates the compliance state of the device. The possible values are:  
  - Compliant  
  - Not Compliant.
- **Workspace ONE Compromised Status**: Indicates the compromised state of the device.
- **Workspace ONE Last Seen**: Indicates the timestamp of the last device check in (number of seconds from the epoch) with Workspace ONE.
- **Workspace ONE Model**: Indicates the model and make of the device.  
- **Workspace ONE Platform**: Indicates the platform/operating system of the device.
- **Workspace ONE OS Version**: Indicates the version of the operating system of the device.
- **Workspace ONE Device IMEI Number**: Indicates the International Mobile Equipment Identity (IMEI), which is a unique number that identifies all mobile phones and smart phones.
- **Workspace ONE Ownership:**: Indicates whether the device is company-owned ("C") or employee-owned ("E").
- **Workspace ONE Phone Number**: Indicates the phone number of the device.  
- **Workspace ONE Device Enrolled User**: Indicates the name of the user to which the device belongs.  
- **Workspace ONE User Contact Number**: Indicates the contact number of the user associated with the device.
- **Workspace ONE User Security Type**: Indicates the security type of the user associated with the device.
- **Workspace ONE Compliance Status Timestamp**: Indicates the timestamp of the most recent device compliance status (number of seconds from the epoch).
- **Workspace ONE Enrollment Status Timestamp**: Indicates the timestamp of the most recent device enrollment state (number of seconds from the epoch).
- **Workspace ONE Enrollment Status**: Indicates the status of enrollment of the device. Possible values are:
  - Enrolled  
  - Not Enrolled.
- **Workspace ONE UDID**: Indicates Workspace ONE User Unique Identifier.
- **Workspace ONE Serial Number**: Indicates the serial number associated with the endpoint.
- **Workspace ONE Cloud Connectivity**: Indicates whether the device has connectivity for cloud backup enabled.
- **Workspace ONE Applications**: Indicates all the software applications running on the device.
- **Workspace ONE Certificates**: Indicates all the certificates installed on the device.
- **Workspace ONE Profiles**: Indicates all the profiles present on the device.
- **Workspace ONE Device Block Level Encryption Status**: Indicates whether the endpoint has block level encryption.
- **Workspace ONE Device Data Protection**: Indicates if the device has data protection present/enabled.
- **Workspace ONE Device File Level Encryption Status**: Indicates if the device has file level encryption present/enabled.
- **Workspace ONE Device Passcode Compliance Status**: Indicates the compliance state of the passcode on the Workspace ONE device.
- **Workspace ONE Device Passcode Present Status**: Indicates if there is passcode present on the endpoint.
- **Workspace ONE Device Compromised Status Timestamp**: Indicates the timestamp of the most recent device compromised state (number of seconds from the epoch).


# Workspace ONE Actions  
Workspace ONE actions are available to be used in a policy.  

To access the Workspace ONE actions:  

1. When configuring a policy, select **Add** in the Actions section of the Main Rule or Sub-Rule dialog box.  
2. Search for Workspace ONE.  
3. Select an action in the **Workspace ONE** folder.  

The following action is available:  
- **Device Check-in**:  Requests check-in of a managed endpoint.  
- **Lock Device**: Lock a managed endpoint.
- **Wipe Device**: Wipe a managed endpoint.
- **Send SMS**: Send an SMS to a contact number.
- **Send Email**: Send an Email to an email address.
- **Send Push Notification**: Send a push notification to an endpoint.


# Scripts  
There are several Python scripts.  
- **workspaceone_poll.py** User can enable discovery on a specified period to poll endpoint properties.
- **workspaceone_test.py** User can test the connection to the Workspace ONE server.  
- **workspaceone_resolve.py** User can retrieve Workspace ONE genreal properties of an endpoint.  
- **workspaceone_app_resolve.py** User can retrieve all the software applications running on a specific managed endpoint.
- **workspaceone_security_resolve.py**: User can retrieve the Workspace ONE security properties of an endpoint.
- **workspaceone_user_resolve.py**: User can retrieve the Workspace ONE endpoint user-related properties.
- **workspaceone_profiles_resolve.py**: User can retrieve the Workspace ONE endpoint profile details.
- **workspaceone_cert_resolve.py**: User can retrieve the Workspace ONE endpoint certificates.
- **workspaceone_request_checkin_action.py** User can issue a request to the Workspace ONE server to a specific managed endpoint to check-in.
- **workspaceone_wipe_device.py**: User can issue a request to the Workspace ONE server to wipe a specific endpoint.
- **workspaceone_lock_device.py**: User can issue a request to the Workspace ONE server to lock a specific endpoint.
- **workspaceone_send_push_notification.py**: User can issue a request to the Workspace ONE server to send a push notification to a specific managed endpoint.
- **workspaceone_send_email.py**: User can issue a request to the Workspace ONE server to send an email with a specific subject to a specific email address.
- **workspaceone_send_sms.py**: User can issue a request to the Workspace ONE server to send an SMS to a specific phone number.
- **workspaceone_proxy_support.py**: Library file that allows user to enable and configure a proxy server between Forescout and the Workspace ONE server.
- **workspaceone_gen_proxy_dict.py**: Library file that also facilitates proxy support for the user.
