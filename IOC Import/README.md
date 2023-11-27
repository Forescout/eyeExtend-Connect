# Forescout
eyeExtend Connect IOC import App README.md Version: 1.0.0

## Configuration Guide
**Version 1.0.0**
- Initial Version

## Contact Information  
- Have feedback or questions? Write to us at

**[connect-app-help@forescout.com](mailto:connect-app-help@forescout.com)**

## App Support

- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.

## About eyeExtend Connect IOC Import App

# About This App

The eyeExtend Connect IOC Import App provides functionality to ingest threat feeds in the form of IOCs which can populate the Forescout IOC Scanner. Feeds can be received in the form of CSV files from external sources.

# What to Do  
To set up your system for using the eyeExtend Connect IOC Import App, perform the following steps:  

1. Download and install the module. See How to Install.  
2. Configure the module. See Configure the Module.  
3. Configure policy templates.  
4. Configure properties.  
5. Configure actions.  

# How to Install  
Get Forescout eyeExtend Connect plugin and IOC Import App from Forescout.  

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

## Configure IOC Import App
To configure eyeExtend Connect IOC Import App, you import the IOC Import App.

Initially, the App Configuration tab of the **Connect** pane is blank. The IOC Import App has not been imported yet.

## Import an App
You can import the IOC Import App.

To import the IOC Import App:

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

To configure the IOC Import App, you add a system description to define a configuration.  

If a system description has not been configured and you select **OK** now, a warning message is displayed.  

Select **Add**


### IOC Import


If using the app to import IOCs from an external source in CSV format, a friendly **IOC Source Name** should be defined here.

The **URL** field should includes the *http(s)://* prefix, and the file to be used, such as */test.csv*

The default refresh interval is to update every day, or every 1440 minutes. This can be modified if required.

Select **Next**

### IOC Property Mapping


Use the headers in the CSV file to map data to the required fields within Forescout. The **Filter Column Name** and **Filter Values** can be used to select what data in a CSV is actually imported.

The **File Name Column Name** is mandatory, and one of the **MD5**, **SHA1** or **SHA256** fields must be populated as well. Other fields if left blank will either be ignored or replaced with default values on import.

Select **Next**

### IOC Severity


To define the severity of an IOC based on data within a CSV, specify a column header that gives a severity value as an *Integer* only.

The severity thresholds define the lower value to match a severity. For example, a *Critical Severity* set at *90* would mean a value in the CSV of *92* is evaluated as *Critical*, whereas a value of *89* would be evaluated lower based on the remaining thresholds. If not defined, then a default severity of *Medium* will be set for all IOCs imported.

Select **Next**

### Assign Forescout Devices


 - Initially, the Assign Forescout Devices panel has only one option, **Assign all devices by default** , and it is selected so that one device is added.

If you want to add a second device, the Assign Forescout Devices panel has more options.

Enter the following information:

- Connecting Forescout Device: Select Enterprise Manager or an IP address of the connecting Forescout device. This is the device which will retrieve IOCs from defined CSV files.  
- Assign specific devices: This Forescout Appliance is assigned to the connecting Forescout device for retrieveing any IOCs via this Connect App.
  - Select **Available Devices** and then select an IP address or Appliance name from the Available Devices list.  
  - Select **Add**. The selected device will send its requests to the connecting Appliance.  
- Assign all devices by default: This is the connecting Appliance to which Forescout Appliances are assigned by default if they are not explicitly assigned to another connecting Appliance. Select this option to make this connecting Appliance the appliance to retrieve IOCs for all Forescout Appliances not assigned to another connecting device.


Note the following:  

- An error message is displayed if you try to add a device that is already used.  
- If you have apps that discover 50,000 or more endpoints, distribute the apps in such a way so that only up to two of the apps share the same focal (connecting) appliance. An alternative is to split the endpoints across multiple user accounts on multiple servers.  


Select **Next**.

### Proxy Server


If required, optionally enter the Proxy Server information needed for network connectivity.  

Select **Finish**.  

## Edit a System Description  
You can edit an existing system description for the IOC Import App.  

To edit a system description:  

Select an existing system description and select **Edit**.  

There are tabs for each pane. You can edit the settings in the IOC Import, Time Format, DNS Short Name, and Assign Forescout Devices tabs.  

Select **OK** to save the system description edits to the Forescout Appliance.  

## Remove a System Description  
You can remove an existing system description.  

To remove a system description:  
Select an existing system description
Select **Remove**. A confirmation is displayed.  

**More** for details or **Ok**.  

## Refresh IOC Data
You can refresh *Discovery of IOC Data*, which instructs the IOC Import App to resolve IOCs from any configured sources immediately. The app must be in the Running state.  

The app must be saved before selecting **Refresh**. Select **OK** in the **System Description** dialog box and then select **Apply** in the **Connect** pane to save the system description. Please wait about 5-10 seconds after clicking apply.  

To refresh IOC data:  

Select an existing system description
Select **Refresh**, then **Discovery of IOC Data** and select **OK**.

A window will appear to display the status of the refresh.