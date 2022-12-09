# Forescout

eyeExtend for Cylance App README.md Version: 1.0.0

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

# About eyeExtend for Cylance

Forescout eyeExtend for Cylance is an integration of the Forescout platform with CylancePROTECT®.

Forescout is recognized as a leading network-access control solution with continuous, agentless discovery of endpoint devices whether they are managed, unmanaged, or otherwise unknown. CylancePROTECT redefines the capabilities and efficiency of endpoint security. By leveraging artificial intelligence, malware can be detected and prevented in real time, before it even executes.

The integration of the Forescout platform with Cylance helps customers enforce compliance by assuring endpoints have the CylancePROTECT sensor and reduce the risk of having any unmanaged devices on their network. It also provides a means for the distribution of endpoint management software, which improves the user experience and increases operational efficiency.

The goal of eyeExtend for Cylance is to increase security protection across a wider device landscape that includes both traditional and non-traditional endpoints, including BYOD and IoT. This is achieved through continuous device discovery/visibility and rapid remediation to prevent the spread of threats and ensure endpoint compliance.

The Forescout integration with Cylance lets you:

- Fortify endpoint defenses, minimize security breaches, and reduce your attack surface
- Gain visibility and control of devices across your network and beyond
- Verify the presence of functional CylancePROTECT agents at connection time and enroll devices with missing agents
- Employ combined automated response options to quarantine or remediate infected devices

Together, the Forescout platform and Cylance can protect customers by providing both broad and deep endpoint discovery, threat detection, and remediation across a broad array of device types and networks. The Forescout platform also helps continually enforce device compliance upon network access. See Use Cases.

# Customer Support

The Connect Plugin is supported by Forescout Customer Support. See [https://forescout.force.com/support/s/](https://forescout.force.com/support/s/).

Connect Apps, including those provided by Forescout, are not supported by Forescout.

# About This Module

Forescout eyeExtend for Cylance supports information sharing and interaction with components of the Cylance cloud platform.

To use the module, you should have a basic understanding of Cylance concepts, functionality, and terminology, and understand how Forescout platform policies and other basic features work.

# Use Cases

This section describes important use cases supported by Forescout eyeExtend for Cylance.

## Cylance Agent Hygiene Policy

You can define a Forescout platform policy that ensures the CylancePROTECT agent is installed and functioning on all supported endpoints within the network. The module supports a set of host properties that detect CylancePROTECT agent status on endpoints. See Configure Cylance Agent Hygiene Policy.

## Policy-Based Response to Identified Risks

When the Forescout platform identifies that Cylance marked an endpoint as not safe (for example, due to malware or other malicious behavior), the Forescout platform performs an action to mitigate the risk. See Configure Cylance Endpoint Not Safe Policy.

# How It Works

The following Cylance components are required for this integrated solution:

- **Cylance User API:** The Forescout platform addresses the API exposed by the platform to retrieve endpoint information and perform actions.

The following Forescout platform components support the integration:

- **Forescout eyeExtend for Cylance:** This cloud-delivered module handles communication with Cylance and provides the properties, actions, and policies described in this guide.
- **Forescout eyeExtend Cloud:** A Forescout cloud service that handles third-party integrations including the integration with Cylance, which provides the endpoint properties and actions described in this guide.
- **Forescout eyeExtend Connect Plugin:** An infrastructure for integrating third-party vendors with the Forescout platform.
- **Forescout eyeExtend Cylance App:** The Connect App developed by Forescout to implement the integration with Cylance.

In a typical deployment, several cloud connections are defined in the Forescout platform. Connections to the cloud may be planned based on anticipated traffic or geographic location. The deployment is as follows:

- A single CounterACT® device connects to each cloud access point, handling communication for a cluster of CounterACT devices. The CounterACT devices in the cluster only work with that Cylance cloud instance.
- For each connection, the rate limiting of messaging from the Forescout platform to the Cylance cloud can be configured.
- The Forescout platform does not communicate directly with the CylancePROTECT agent on endpoints.

This deployment method scales efficiently and allows tuning of traffic loads.

# What to Do

To set up your system for integration with eyeExtend for Cylance, perform the following steps:

1. Verify that the requirements are met. See Requirements.
2. Download and install the module. See How to Install.
3. Configure the module. See Configure the Module.
4. Configure policy templates. See Configure Cylance Policy Templates.
5. Configure properties. See Configure Properties.
6. Configure actions. See Configure Actions.

# Requirements

- Forescout version 8.1.4, 8.2.0.1
- Install CylancePROTECT and CylanceOPTICS™ agents on the endpoints
- CylancePROTECT is mandatory. CylanceOPTICS is needed for the integration to take actions against infected endpoints.

# How to Install

Get Forescout eyeExtend Connect plugin and Cylance App from Forescout.

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

# Obtain Tenant ID, Application ID and Secret

You can obtain the tenant ID, application ID, and application secret from the Cylance Web Portal.

They are used in the app configuration. See Add a System Description.

To obtain tenant ID, application ID, and application secret:

1. Log in to the Cylance Web Portal using your administrator account.
2. On the left-hand side near the bottom, select the Settings icon, and then select the **Integrations** tab.
3. **Copy** the **Tenant ID**.
4. Select **ADD APPLICATION**.
5. Select the needed privileges for the application. **Copy** the **Application ID** and **Application Secret**.

# Configure the Module

After eyeExtend Connect is installed, **Connect** is displayed under **Options**.

## Configure Cylance App

To configure eyeExtend for Cylance, you import the Cylance App and then add a system description.

Initially, the App Configuration tab of the **Connect** pane is blank. The Cylance App has not been imported yet and the system description has not been configured yet.

## Import an App

You can import the Cylance App.

To import the Cylance App:

1. In the App Configuration tab of the **Connect** pane, select **Import**.
2. Apps that can be imported are in .zip or .eca format. They can be in any folder.
3. Select **Import**.
If the app is imported successfully, a message is displayed at the bottom of the **Sending** dialog box. If the app is not imported successfully, error messages are displayed in the **Sending** dialog box.
4. Select **Close** when the import has finished. A blank **System Description** dialog box opens. See Add a System Description.

- If you select **Close** before the import has finished, it will fail.

## Add a System Description

To configure the Cylance App, you add a system description to define a connection, which includes login credentials.

To add the system description:

1. After the app is imported, the **System Description** dialog box opens. It is initially blank and only the **Add** and **Import** buttons are enabled.

If a system description has not been configured and you select **OK** now, a warning message is displayed.
2. Select **Add**.
3. Enter the following information:

- URL: Enter the Cylance URL: [https://protectapi.cylance.com](https://protectapi.cylance.com/)
- Tenant ID:  Enter the account tenant ID. See Obtain Tenant ID, Application ID and Secret.
- Application ID: Enter the account application ID. See Obtain Tenant ID, Application ID and Secret.
- Application Secret:  Enter the account application secret. See Obtain Tenant ID, Application ID and Secret.
- Verify Application Secret: Re-enter the account application secret to verify it.
- Validate Server Certificate: Select this option to validate the identity of the third-party server before establishing a connection, when the eyeExtend product communicates as a client over SSL/TLS. To validate the server certificate, either of the following certificate(s) must be installed:
  - Self-signed server certificate: the server certificate must be installed on the CounterACT Appliance
  - Certificate Authority (CA) signed server certificate: the CA certificate chain (root and intermediate CA certificates) must be installed on the CounterACT Appliance
Use the Certificates \& Trusted Certificates pane to add the server certificate to the Trusted Certificate list. For more information about certificates, refer to the appendix, &quot;Configuring the Certificate Interface&quot; in the _Forescout Administration Guide_.

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

You can edit an existing system description for the Cylance App.

To edit a system description:

1. Select an existing system description and select **Edit**.
There are tabs for each pane. You can edit the settings in the Cylance Connection, Assign CounterACT Devices, Proxy Server, and Cylance Options tabs.
2. Select **OK** to save the system description edits to the CounterACT Appliance.

## Remove a System Description

You can remove an existing system description.

To remove a system description:

1. Select an existing system description and select **Remove**. A confirmation is displayed.
2. Select **More** for details or select **Ok**.

## Test a System Description

You can test a system description, which tests the connection to the Cylance App. The app must be in the Running state.

Also, the app must be saved before selecting **Test**. Select **OK** in the **System Description** dialog box and then select **Apply** in the **Connect** pane to save the system description.

To test a system description:

1. Select an existing system description and select **Test**.
If the connectivity of the system description has been tested successfully, a success message is displayed at the bottom of the dialog box. If the test failed, a failure message is displayed with a reason.
2. Select **Close**.

# Configure Cylance Policy Templates

There are two Cylance policy templates for customers to manage devices in a Cylance environment and detect devices that are compliant or non-compliant.

- Cylance Endpoint Not Safe Policy
- Cylance Agent Hygiene Policy

## Add Cylance Policies

To configure a Cylance policy:

1. In the Forescout Console, select **Policy**.
2. Select **Add** , search for Cylance, and expand the **Cylance** folder.
3. Select **Cylance Endpoint Not Safe** or **Cylance Agent Hygiene**.

# Cylance Properties

Cylance properties are available to be used in a policy.

The following properties are available:

- Cylance Agent Installed: Indicates the CylancePROTECT agent installed on the device.
- Cylance Agent Version: Indicates the CylancePROTECT agent version installed on the device.
- Cylance Date Offline: For an endpoint in the Offline state, indicates the date the endpoint was offline. **Cylance Date Offline** does not cause issues with policies because the field is considered only when the endpoint state is Offline.See **Cylance State**. See also Cylance State Offline/Online.
- Host Name: Indicates the host name detected by Cylance.
- Cylance ID: Indicates the Cylance identifier.
- Cylance IP Addresses: Indicates the Cylance IP addresses.
- Cylance is Safe: Indicates that Cylance is safe.
- Cylance Last Logged in User: Indicates the Cylance user last logged in.
- Cylance MAC Addresses: Indicates the Cylance MAC addresses.
- OS Version: Indicates the operating system version detected by Cylance.
- Cylance Policy: Indicates the Cylance policy.The following sub-properties are available:
  - Policy ID: The policy identifier.
  - Policy Name: The policy name.
- Cylance State: Indicates whether the endpoint is Online (powered on) or Offline (powered off).For an offline endpoint, see **Cylance Date Offline**. See also Cylance State Offline/Online.
- Cylance Agent Update Available: Indicates if an agent update is available for the device based on the update type.
- Cylance State Changed: Indicates the Track Change property for the Cylance state.

# Cylance Actions

Cylance actions are available to be used in a policy.

To access the Cylance actions:

1. When configuring a policy, select **Add** in the Actions section of the Main Rule or Sub-Rule dialog box.
2. Search for Cylance.
3. Select an action in the **Cylance** folder.

The following action is available:

- Lockdown Endpoint:  Locks down an endpoint.

# Scripts

There are a few Python scripts.

- cylance_poll.py User can enable discovery on a specified period to poll endpoint properties.
- cylance_test.py User can test the connection to the Cylance server.
- cylance_resolve.py User can get the Cylance endpoint properties.
- cylance_lockdown.py User can issue request to the Cylance server to lockdown specific endpoint.
- cylance_authorization.py User can fetch Cylance REST API authorization token on a specific period.
