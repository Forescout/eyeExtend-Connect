# Forescout  
eyeExtend for MobileIron MDM App README.md Version: 1.0.0  

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

# About eyeExtend for MobileIron


# Customer Support  
The Connect Plugin is supported by Forescout Customer Support. See [https://forescout.force.com/support/s/](https://forescout.force.com/support/s/).  

Connect Apps, including those provided by Forescout, are not supported by Forescout.  

# About This Module  


# Use Cases  
This section describes important use cases supported by Forescout eyeExtend for MobileIron.  

## MobileIron Device Compliance Policy
Use this policy template to detect non-compliant devices and redirect non-compliant users to a notification message.

## MDM Classification Policy (Enrollment Step-1)
Only "Mobile devices" group members should be included in the policy you are creating, which is taken care of in this policy step.

## MobileIron Device Enrollment Policy (Enrollment Step-2)
Use this policy template to detect corporate hosts not enrolled with the MobileIron service, and prompt host users to enroll.  
Corporate hosts are defined as hosts that have authenticated via the HTTP Login action or have enrolled through Company Portal on their device.  
By default, users cannot browse the Internet until enrollment is complete.  
A restrictive action blocks corporate network access to users not enrolled.  
This action is disabled by default.


# How It Works  
The following MobileIron components are required for this integrated solution:  

- **Common Platform Services (CPS) API:** The Forescout platform connects to the CPS API’s exposed by the MobileIron platform to retrieve endpoint information and perform actions. This API scheme is supported by MobileIron Core(on-premise) and MobileIron Cloud. Refer MobileIron documentation on how to enable CPS API.

The following Forescout platform components support the integration:  

- **Forescout eyeExtend for MobileIron:** This cloud-delivered module handles communication with MobileIron and provides the properties, actions, and policies described in this guide.  
- **Forescout eyeExtend Cloud:** A Forescout cloud service that handles third-party integrations including the integration with MobileIron UEM, which provides the endpoint properties and actions described in this guide.  
- **Forescout eyeExtend Connect Plugin:** An infrastructure for integrating third-party vendors with the Forescout platform.  
- **Forescout eyeExtend MobileIron App:** The Connect App developed by Forescout to implement the integration with MobileIron.  

In a typical deployment, several cloud connections are defined in the Forescout platform. Connections to the cloud may be planned based on anticipated traffic or geographic location. The deployment is as follows:  

- A single CounterACT® device is designated as a “focal” appliance and connects to the cloud access point, handling communication for a cluster of CounterACT devices. Only a single MobileIron cloud instance can be associated with the designated CounterACT device or “focal” appliance within a single cluster.  
- For each connection, the rate limiting of messaging from the Forescout platform to the MobileIron cloud can be configured.

# What to Do  
To set up your system for integration with eyeExtend for MobileIron, perform the following steps:  

1. Verify that the requirements are met. See Requirements.  
2. Download and install the module. See How to Install.  
3. Configure the module. See Configure the Module.  
4. Configure policy templates. See Configure MobileIron Policy Templates.  
5. Configure properties. See MobileIron Properties.  
6. Configure actions. See MobileIron Actions.  

# Requirements  
- Forescout version 8.1.4, 8.2.1
- eyeExtend Connect Plugin version 1.8.0
- Forescout eyeExtend for MobileIron requires the following:
  - An API account on MobileIron Core and/or MobileIron Cloud with CPS role. The CPS API is supported on both MobileIron Core (on-premise) and MobileIron Cloud.
  - For information about the vendor models (hardware/software) and versions (product/OS) that are validated for integration with this Forescout component, refer to the [Forescout Compatibility Matrix]([https://www.forescout.com/company/resources/forescout-compatibility-matrix/](https://www.forescout.com/company/resources/forescout-compatibility-matrix/)).

# How to Install  
Get Forescout eyeExtend Connect plugin and MobileIron MDM App from Forescout.  

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


## Configure MobileIron App  
To configure eyeExtend for MobileIron, you import the MobileIron App and then add a system description.  

Initially, the App Configuration tab of the **Connect** pane is blank. The MobileIron App has not been imported yet and the system description has not been configured yet.  

## Import an App  
You can import the MobileIron App.  

To import the MobileIron App:  

1. In the App Configuration tab of the **Connect** pane, select **Import**.  
2. Apps that can be imported are in .zip or .eca format. They can be in any folder.  
3. Select **Import**.  
If the app is imported successfully, a message is displayed at the bottom of the **Sending** dialog box. If the app is not imported successfully, error messages are displayed in the **Sending** dialog box.  
4. Select **Close** when the import has finished. A blank **System Description** dialog box opens. See Add a System Description.  

- If you select **Close** before the import has finished, it will fail.  

## Add a System Description  
To configure the MobileIron App, you add a system description to define a connection, which includes login credentials.  

To add the system description:  

1. After the app is imported, the **System Description** dialog box opens. It is initially blank and only the **Add** and **Import** buttons are enabled.  

If a system description has not been configured and you select **OK** now, a warning message is displayed.  
1. Select **Add**.  
2. Enter the following information:  

- MobileIron Server URL: Enter the login URL  
- User: Enter the API username with CPS role.
- Password: Enter the password for the MobileIron API account.    

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
7. Enter the Proxy Server information similar to any Forescout Extend Module, if applicable.  
8. Select **Next**.  
9. Enter the following information:  
- Enable Host Discovery: Select this option to enable the **Discovery Frequency** field.  
- Discovery Frequency: Select a value for the frequency of host discovery, which is the interval between discoveries. The range is from 1 minute to 2880 minutes (48 hours). The default is 1440 minutes (24 hours).  
- MDM Query Threshold Interval: Specify how often (in seconds) the module should query the MobileIron UEM service. The range is from 1 to 1000 seconds; the default is every 10 seconds. You can rate limit the frequency in which requests are sent to the third-party server. The rate limiter specifies the number of times a script is invoked during the specified time. It is triggered when the app starts.   
10. Select **Finish**. The configured system description is displayed in the **System Description** dialog box.  

When the system description is selected, all the buttons on the dialog box are enabled.  

You can create multiple system descriptions. To add another system description, select **Add** and repeat the procedure for Add a System Description.  

11. Select **OK** to save the system description to the CounterACT Appliance. The system description is displayed in the App Configuration tab of the **Connect** pane. There are several default columns. See Connect Pane Details.  

## Edit a System Description  
You can edit an existing system description for the MobileIron App.  

To edit a system description:  

1. Select an existing system description and select **Edit**.  
There are tabs for each pane. You can edit the settings in the MobileIron Connection, Assign CounterACT Devices, Proxy Server, and MobileIron Options tabs.  
2. Select **OK** to save the system description edits to the CounterACT Appliance.  

## Remove a System Description  
You can remove an existing system description.  

To remove a system description:  
1. Select an existing system description and select **Remove**. A confirmation is displayed.  
2. Select **More** for details or select **Ok**.  

## Test a System Description  
You can test a system description, which tests the connection of the Intue App to the MobileIron server. The app must be in the Running state.  

Also, the app must be saved before selecting **Test**. Select **OK** in the **System Description** dialog box and then select **Apply** in the **Connect** pane to save the system description. Please wait about 5-10 seconds after clicking apply.  

To test a system description:  

1. Select an existing system description and select **Test**.  
If the connectivity of the system description has been tested successfully, a success message is displayed at the top of the dialog box. If the test failed, a failure message is displayed with a reason.  
2. Select **Close**.  

# Configure MobileIron Policy Templates  
There are three MobileIron policy templates for customers to manage devices in an MobileIron environment, detect devices that are compliant or non-compliant, and devices that are enrolled or not.  

- MDM Classification (Enrollment Step-1)
- MobileIron Device Enrollment (Enrollment Step-2)
- MobileIron Device Compliance  

## Configure MobileIron Policies  
To configure an MobileIron policy:  

1. In the Forescout Console, select **Policy**.  
2. Select **Add** , search for MobileIron, and expand the **MobileIron** folder.  
3. Select **Enrollment Step-1: MDM Classification** and **Enrollment Step-2: MobileIron Device Enrollment**, or **MobileIron Device Compliance**.  

# MobileIron Properties  
MobileIron properties are available to be used in a policy.  

The following properties are available:  

- **MobileIron Device ID**: Indicates the unique identifier for the MobileIron endpoint.  
- **MobileIron Device Compliance State**: Indicates the compliance state of the device. The possible values are:  
  - Compliant  
  - Non-Compliant.
- **MobileIron Compromised State**: Indicates the compromised state of the device.
- **MobileIron iOS Device Jailbroken**: Indicates whether an iOS device is jailbroken.
- **MobileIron Android Device Rooted**: Indicates whether an Android device has been rooted.  
- **MobileIron Blocked Device**: Indicates the supervised status of the device.  
- **MobileIron Device Last Check-In**: Indicates the timestamp of the last device check in (number of milliseconds from the epoch) with MobileIron.  
- **MobileIron Device MAC Address**: Indicated the MAC address of the device, which may be randomized.  
- **MobileIron Device Manufacturer**: Indicates the manufacturer of the device.  
- **MobileIron Device Model**: Indicates the model of the device.  
- **MobileIron Operating System**: Indicates the operating system of the device. The possible values are:
  - Android
  - iOS  
- **MobileIron Device OS Version**: Indicates the operating system version of the device.    
- **MobileIron MDM Managed Device**: Indicates whether the device is managed by MobileIron.
- **MobileIron Apps**: Indicates all the software applications running on the device.
- **MobileIron Device IMEI**: Indicates the International Mobile Equipment Identity (IMEI), which is a unique number that identifies all mobile phones and smart phones.
- **MobileIron Device IMSI**: Indicates the International Mobile Subscriber Identity (IMSI), which is a unique number associated with mobile phone users that is used for identifying GSM subscribers.  
- **MobileIron Device Ownership E/C:**: Indicates whether the device is company-owned or employee-owned. Possible values are:
  - Company  
  - Employee
  - Unknown  
- **MobileIron Device Registration Time**: Indicates the time at which the device was registered.
- **MobileIron Device Status**: Indicates the status of the managed device. Possible values are:
  - Active
  - Enrollment Pending
  - Retired
  - Wiped  
- **MobileIron Quarantined Device**: Indicates "true" if the device is violating any policy with respect to quarantine action for device.  
- **MobileIron Serial Number**: Indicates the serial number of the device.  
- **MobileIron Device Phone Number**: Indicates the phone number of the device.  
- **MobileIron Device User Name**: Indicates the user name of the user the device belongs to.  
- **MobileIron User UID**: Indicates the unique identifier of the user associated with the device.  

# MobileIron Actions  
MobileIron actions are available to be used in a policy.  

To access the MobileIron actions:  

1. When configuring a policy, select **Add** in the Actions section of the Main Rule or Sub-Rule dialog box.  
2. Search for MobileIron.  
3. Select an action in the **MobileIron** folder.  

The following action is available:  
- **Force Check-in**:  Forces check-in of a managed endpoint.  

# Scripts  
There are a few Python scripts.  
- **mobileironmdm_poll.py** User can enable discovery on a specified period to poll endpoint properties.  
- **mobileironmdm_test.py** User can test the connection to the MobileIron server.  
- **mobileironmdm_resolve.py** User can retrieve the MobileIron endpoint properties.  
- **mobileironmdm_resolve_app_inventory.py** User can retrieve all the software applications running on a specific managed endpoint.  
- **mobileironmdm_force_checkin_action.py** User can issue a request to the MobileIron server to force check-in a specific managed endpoint.
