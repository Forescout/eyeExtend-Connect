# Forescout
eyeExtend for CiscoDNAC App README.md Version: 1.1.1

## Configuration Guide
**Version 1.1.1**

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

# About eyeExtend for Cisco DNAC
Forescout eyeExtend for Cisco DNAC is an integration of the Forescout platform with Cisco DNAC.

Forescout is recognized as a leading network-access control solution with continuous, agentless discovery of endpoint devices whether they are managed, unmanaged, or otherwise unknown. Cisco DNAC redefines the capabilities and efficiency of endpoint security. By leveraging artificial intelligence, malware can be detected and prevented in real time, before it even executes.

The integration of the Forescout platform with Cisco DNAC helps customers enforce compliance by assuring endpoints have the Cisco DNACPROTECT sensor and reduce the risk of having any unmanaged devices on their network. It also provides a means for the distribution of endpoint management software, which improves the user experience and increases operational efficiency.

The goal of eyeExtend for Cisco DNAC is to increase security protection across a wider device landscape that includes both traditional and non-traditional endpoints, including BYOD and IoT. This is achieved through continuous device discovery/visibility and rapid remediation to prevent the spread of threats and ensure endpoint compliance.

The Forescout integration with Cisco DNAC lets you:

- Fortify endpoint defenses, minimize security breaches, and reduce your attack surface
- Gain visibility of devices across your network and beyond
- Verify the presence of functional Cisco DNAC registered clients at connection time and enroll devices.

Together, the Forescout platform and Cisco DNAC can protect customers by providing both broad and deep endpoint discovery, threat detection, and remediation across a broad array of device types and networks. The Forescout platform also helps continually enforce device compliance upon network access. See Use Cases.

# Customer Support
The Connect Plugin is supported by Forescout Customer Support. See [https://forescout.force.com/support/s/](https://forescout.force.com/support/s/).

Connect Apps, including those provided by Forescout, are not supported by Forescout.

# About This Module
Forescout eyeExtend for Cisco DNAC supports information sharing and interaction with components of the Cisco DNAC VOIP platform.

To use the module, you should have a basic understanding of Cisco DNAC concepts, functionality, and terminology, and understand how Forescout platform policies and other basic features work.

# Use Cases
This section describes important use cases supported by Forescout eyeExtend for Cisco DNAC.


# How It Works
The following Cisco DNAC components are required for this integrated solution:

- **Cisco DNAC REST API:** The Forescout platform addresses the Cisco DNAC REST API exposed by the platform to retrieve switch and router information.

The following Forescout platform components support the integration:

- **Forescout eyeExtend for Cisco DNAC:** This cloud-delivered module handles communication with Cisco DNAC and provides the properties, actions, and policies described in this guide.
- **Forescout eyeExtend Cloud:** A Forescout cloud service that handles third-party integrations including the integration with Cisco DNAC, which provides the endpoint properties and actions described in this guide.
- **Forescout eyeExtend Connect Plugin:** An infrastructure for integrating third-party vendors with the Forescout platform.
- **Forescout eyeExtend Cisco DNAC App:** The Connect App developed by Forescout to implement the integration with Cisco DNAC.

In a typical deployment, several cloud connections are defined in the Forescout platform. Connections to the cloud may be planned based on anticipated traffic or geographic location. The deployment is as follows:

- A single CounterACT® device connects to each cloud access point, handling communication for a cluster of CounterACT devices. The CounterACT devices in the cluster only work with that Cisco DNAC cloud instance.
- For each connection, the rate limiting of messaging from the Forescout platform to the Cisco DNAC cloud can be configured.
- The Forescout platform does not communicate directly with the endpoints.

This deployment method scales efficiently and allows tuning of traffic loads.

# What to Do
To set up your system for integration with eyeExtend for Cisco DNAC, perform the following steps:

1. Verify that the requirements are met. See Requirements.
2. Download and install the module. See How to Install.
3. Configure the module. See Configure the Module.
4. Configure policy templates. See Configure Cisco DNAC Policy Templates.
5. Configure properties. See Configure Properties.
6. Configure actions. See Configure Actions.

# Requirements
- Forescout version 8.4.1, 8.5.1

# How to Install
Get Forescout eyeExtend Connect plugin and Cisco DNAC App from Forescout.

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

# Obtain Cisco DNAC Username and Password
You can obtain the Username and Password from the Cisco DNAC Web Portal, please refer to Cisco engineer.

They are used in the app configuration. See Add a System Description.

DNAC URL, DNAC Username, DNAC Password.


# Configure the Module
After eyeExtend Connect is installed, **Connect** is displayed under **Options**.


## Configure Cisco DNAC App
To configure eyeExtend for Cisco DNAC, you import the Cisco DNAC App and then add a system description.

Initially, the App Configuration tab of the **Connect** pane is blank. The Cisco DNAC App has not been imported yet and the system description has not been configured yet.

## Import an App
You can import the Cisco DNAC App.

To import the Cisco DNAC App:

1. In the App Configuration tab of the **Connect** pane, select **Import**.
2. Apps that can be imported are in .zip or .eca format. They can be in any folder.
3. Select **Import**.
If the app is imported successfully, a message is displayed at the bottom of the **Sending** dialog box. If the app is not imported successfully, error messages are displayed in the **Sending** dialog box.
4. Select **Close** when the import has finished. A blank **System Description** dialog box opens. See Add a System Description.

- If you select **Close** before the import has finished, it will fail.

## Add a System Description
To configure the Cisco DNAC App, you add a system description to define a connection, which includes login credentials.

To add the system description:

1. After the app is imported, the **System Description** dialog box opens. It is initially blank and only the **Add** and **Import** buttons are enabled.

If a system description has not been configured and you select **OK** now, a warning message is displayed.
2. Select **Add**.
3. Enter the following information:

- URL: Enter the Cisco DNAC URL: Server IP or FQDN
- Username : Enter the DNAC account username. (This is obtained from the Cisco DNAC admin) 
- Password :  Enter the DNAC account password. ( This is obtained from the Cisco DNAC System.
- Verify Passowrd: Re-enter the account data from above.
- Enter the Cisco DNAC version. ( This is the REST API version )
- Enter a description to describe the REST API instance.
- Validate Server Certificate: Select this option to validate the identity of the third-party server before establishing a connection, when the eyeExtend product communicates as a client over SSL/TLS. To validate the server certificate, either of the following certificate(s) must be installed:
  - Self-signed server certificate: the server certificate must be installed on the CounterACT Appliance
  - Certificate Authority (CA) signed server certificate: the CA certificate chain (root and intermediate CA certificates) must be installed on the CounterACT Appliance
Use the Certificates \&gt; Trusted Certificates pane to add the server certificate to the Trusted Certificate list. For more information about certificates, refer to the appendix, &quot;Configuring the Certificate Interface&quot; in the _Forescout Administration Guide_.
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

11: Cisco DNAC Option: Typically leave this set to 1
12 CounterACT EM API: Please refer to setting up the switch API. Once setup you will need to provide the following 
https://docs.forescout.com/bundle/switch-api-8-4-htg/page/about-the-switch-api.html
13: 
13 Username of EyeSight account that will be used to access the REST API
14 Passowrd of the EyeSight account that will be used to access the REST API
15 Confirm password of the EyeSight account that will be used to access the REST API
16 EyeSight REST API Rate in seconds. Leave this set for around 2 seconds

Switch Default Data

15 Eyesight Switch Managers. These are the IP addresses of the appliances that will manage the switches. When adding switches the managining appliances will be selected at randon and assigned to the switches.
16 Key MAC address to use: The MAC address key is used as mechanism to limit the number of triggers to read the DNAC API. I'd the DNAC API will only every be read based on 1 device property being checked based on policy recheck times. 
Typically just copy the MAC or 1 appliance and assign it to this value. Then in the Ciscodnacapp DNAC Switch Scan policy (found in policy templates ) add this mac address to one of the mac address fields in the main rule.
17 Delete switches: This option if selected will make the plugin delete all switches that are not found in DNAC, thus synchronising switches found in DNAC with those present in Eyesight. If not selected 
switches added manaully or added automatically and later removed will not be deleted.
18 Switch Parsing Data: In order to be able to assign swicthes and routers discovered in DNAC to the right profile in EyeSight we need to define a mapping table. The mapping table currently uses the data contained in the 
'Role' parameter of the DNAC data, values seen include 'Distrubution, Core and Switch. So if we get a device with either 'Distrubition' or 'Core' we are most liley going to want to assign it to a Layer III switch profile
for only reading ARP tables, if we get a 'Switch' role then we will probably assign it to a Layer II profile. The format is as followins: {name}|{Profile}{cr}



Additional configuration steps required.
The default Eeysight REST API is rate limited to 1 min. In order to ensure that the Cisco DNAC APP doe snot exceed its maximum running time we need to adjust the rate limit on the EyeSight switch REST API.
The rate limite is adjusted by taking the following steps.

Using putty terminal login to the EM and type the following commands below.

fstool sw set_property rest_api.rate_limit.enabled.valuerest_api.rate_limit.enabled.value 0
fstool sw restart

For additional information please refer to the link below.
https://docs.forescout.com/bundle/switch-api-8-4-3-htg/page/set-api-rate-limiting.html


## Edit a System Description
You can edit an existing system description for the Cisco DNAC App.

To edit a system description:

1. Select an existing system description and select **Edit**.
There are tabs for each pane. You can edit the settings in the Cisco DNAC Connection, Assign CounterACT Devices, Proxy Server, and Cisco DNAC Options tabs.
2. Select **OK** to save the system description edits to the CounterACT Appliance.

## Remove a System Description
You can remove an existing system description.

To remove a system description:
1. Select an existing system description and select **Remove**. A confirmation is displayed.
2. Select **More** for details or select **Ok**.

## Test a System Description

Once installed and configured you may test it using two methods.

1) Go to options / connect / Ciscodnacapp / Edit and select the Ciscodnacapp entry and push the test button. If successful you should see 'Test succeeded and Poll status succeeded.'
You will also see that the switch plugin has updated with any new devices that were not present in the switch plugin but were found in the DNAC system.

# Scripts
There are a few Python scripts.

- Cisco DNAC_test.py User can test the connection to the Cisco DNAC server.
- Cisco DNAC_resolve.py Used to initiate a Cisco DNAC scan and inform policy.


