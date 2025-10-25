# Forescout
eyeExtend for Unigy App README.md Version: 1.0.0

## Configuration Guide
**Version 1.0.3**

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

# About eyeExtend for Unigy
Forescout eyeExtend for Unigy is an integration of the Forescout platform with Unigy.

Forescout is recognized as a leading network-access control solution with continuous, agentless discovery of endpoint devices whether they are managed, unmanaged, or otherwise unknown. Unigy redefines the capabilities and efficiency of endpoint security. By leveraging artificial intelligence, malware can be detected and prevented in real time, before it even executes.

The integration of the Forescout platform with Unigy helps customers enforce compliance by assuring endpoints have the UnigyPROTECT sensor and reduce the risk of having any unmanaged devices on their network. It also provides a means for the distribution of endpoint management software, which improves the user experience and increases operational efficiency.

The goal of eyeExtend for Unigy is to increase security protection across a wider device landscape that includes both traditional and non-traditional endpoints, including BYOD and IoT. This is achieved through continuous device discovery/visibility and rapid remediation to prevent the spread of threats and ensure endpoint compliance.

The Forescout integration with Unigy lets you:

- Fortify endpoint defenses, minimize security breaches, and reduce your attack surface
- Gain visibility of devices across your network and beyond
- Verify the presence of functional Unigy registered clients at connection time and enroll devices.

Together, the Forescout platform and Unigy can protect customers by providing both broad and deep endpoint discovery, threat detection, and remediation across a broad array of device types and networks. The Forescout platform also helps continually enforce device compliance upon network access. See Use Cases.

# Customer Support
The Connect Plugin is supported by Forescout Customer Support. See [https://forescout.force.com/support/s/](https://forescout.force.com/support/s/).

Connect Apps, including those provided by Forescout, are not supported by Forescout.

# About This Module
Forescout eyeExtend for Unigy supports information sharing and interaction with components of the Unigy VOIP platform.

To use the module, you should have a basic understanding of Unigy concepts, functionality, and terminology, and understand how Forescout platform policies and other basic features work.

# Use Cases
This section describes important use cases supported by Forescout eyeExtend for Unigy.


# How It Works
The following Unigy components are required for this integrated solution:

- **Unigy REST API:** The Forescout platform addresses the Unigy REST API exposed by the platform to retrieve endpoint information and retrive data.

The following Forescout platform components support the integration:

- **Forescout eyeExtend for Unigy:** This cloud-delivered module handles communication with Unigy and provides the properties, actions, and policies described in this guide.
- **Forescout eyeExtend Cloud:** A Forescout cloud service that handles third-party integrations including the integration with Unigy, which provides the endpoint properties and actions described in this guide.
- **Forescout eyeExtend Connect Plugin:** An infrastructure for integrating third-party vendors with the Forescout platform.
- **Forescout eyeExtend Unigy App:** The Connect App developed by Forescout to implement the integration with Unigy.

In a typical deployment, several cloud connections are defined in the Forescout platform. Connections to the cloud may be planned based on anticipated traffic or geographic location. The deployment is as follows:

- A single CounterACT® device connects to each cloud access point, handling communication for a cluster of CounterACT devices. The CounterACT devices in the cluster only work with that Unigy cloud instance.
- For each connection, the rate limiting of messaging from the Forescout platform to the Unigy cloud can be configured.
- The Forescout platform does not communicate directly with the endpoints.

This deployment method scales efficiently and allows tuning of traffic loads.

# What to Do
To set up your system for integration with eyeExtend for Unigy, perform the following steps:

1. Verify that the requirements are met. See Requirements.
2. Download and install the module. See How to Install.
3. Configure the module. See Configure the Module.
4. Configure policy templates. See Configure Unigy Policy Templates.
5. Configure properties. See Configure Properties.
6. Configure actions. See Configure Actions.

# Requirements
- Forescout version 8.4.1, 8.5.1

# How to Install
Get Forescout eyeExtend Connect plugin and Unigy App from Forescout.

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

# Obtain the following information and format it in JSON format as shown below. 1 or more Unigy instances can be addressed by the plugin by formating the data as seen below.

{"Servers": [{
        "location" : "Unigy 1",
        "hostname": "https://192.168.22.20",
        "version": "v1",
        "password": "ZGF2aWRAeXViaXF1ZS5jb206I0dlMHJnZTAwNzkj",
        "active": "True",
        "certificate": "False"
        },{
        "location" : "Unigy 2",
        "hostname": "https://192.168.22.31",
        "version": "v2",
        "password": "ZGF2aWRAeXViaXF1ZS5jb206I0dlMHJnZTAwNzkj",
        "active": "True",
        "certificate" : "False"
}]}




# Configure the Module
After eyeExtend Connect is installed, **Connect** is displayed under **Options**.


## Configure Unigy App
To configure eyeExtend for Unigy, you import the Unigy App and then add a system description.

Initially, the App Configuration tab of the **Connect** pane is blank. The Unigy App has not been imported yet and the system description has not been configured yet.

## Import an App
You can import the Unigy App.

To import the Unigy App:

1. In the App Configuration tab of the **Connect** pane, select **Import**.
2. Apps that can be imported are in .zip or .eca format. They can be in any folder.
3. Select **Import**.
If the app is imported successfully, a message is displayed at the bottom of the **Sending** dialog box. If the app is not imported successfully, error messages are displayed in the **Sending** dialog box.
4. Select **Close** when the import has finished. A blank **System Description** dialog box opens. See Add a System Description.

- If you select **Close** before the import has finished, it will fail.

## Add a System Description
To configure the Unigy App, you add a system description to define a connection, which includes login credentials.

To add the system description:

1. After the app is imported, the **System Description** dialog box opens. It is initially blank and only the **Add** and **Import** buttons are enabled.

If a system description has not been configured and you select **OK** now, a warning message is displayed.
2. Select **Add**.
3. Enter the following information.

    Instance Name (Not Used) is just a reference name for use in the plugin and is not used.
	
	REST Servers Setup (JSON string) Add a JSON formatted block (as shown above) which will be used by the application to check and collect data for a Unigy registered device.


4. Select **Next**.
Initially, the Assign CounterACT Devices panel has only one option, **Assign all devices by default** , and it is selected so that one device is added.
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
- Number of API queries per unit time: Select a value for the rate limiter. The range is from 1 to 1000 requests per second. The default is 100 requests per second.You can rate limit the requests sent to the third-party server. The rate limiter specifies the number of times a script is invoked during the specified time. It is triggered when the app starts.
10. Select **Finish**. The configured system description is displayed in the **System Description** dialog box.

When the system description is selected, all the buttons on the dialog box are enabled.

You can create multiple system descriptions. To add another system description, select **Add** and repeat the procedure for Add a System Description.

11. Select **OK** to save the system description to the CounterACT Appliance. The system description is displayed in the App Configuration tab of the **Connect** pane. There are several default columns. See Connect Pane Details.

## Edit a System Description
You can edit an existing system description for the Unigy App.

To edit a system description:

1. Select an existing system description and select **Edit**.
There are tabs for each pane. You can edit the settings in the Unigy Connection, Assign CounterACT Devices, Proxy Server, and Unigy Options tabs.
2. Select **OK** to save the system description edits to the CounterACT Appliance.

## Remove a System Description
You can remove an existing system description.

To remove a system description:
1. Select an existing system description and select **Remove**. A confirmation is displayed.
2. Select **More** for details or select **Ok**.

## Test a System Description
You can test a system description, which tests the connection to the Unigy App. The app must be in the Running state.

Also, the app must be saved before selecting **Test**. Select **OK** in the **System Description** dialog box and then select **Apply** in the **Connect** pane to save the system description.

To test a system description:

1. Select an existing system description and select **Test**.
If the connectivity of the system description has been tested successfully, a success message is displayed at the bottom of the dialog box. If the test failed, a failure message is displayed with a reason.
2. Select **Close**.

# Configure Unigy Policy Templates
There ia one Unigy policy template for customer to manage devices in a Unigy environment and detect devices that are compliant or non-compliant.

- Unigy Device Roles

## Add Unigy Policies
To configure a Unigy policy:

1. In the Forescout Console, select **Policy**.
2. Select **Add** , search for Unigy, and expand the **Unigy** folder.
3. Select **Unigy Device Roles.

# Unigy Properties
Unigy properties are available to be used in a policy.

The following properties are available:

- Unigy Status: Indicates the Track Change property for the Unigy status.

# Unigy Actions

Unigy current none.

To access the Unigy actions:


# Scripts
There are a few Python scripts.

- Unigy_test.py User can test the connection to the Unigy server.
- Unigy_resolve.py User can get the Unigy endpoint properties.
