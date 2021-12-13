# Forescout eyeExtend Connect JAMF App

 
## Contact Information
Forescout Technologies, Inc.
190 West Tasman Drive
San Jose, CA 95134 USA
https://www.Forescout.com/support/
Toll-Free (US): 1.866.377.8771
Tel (Intl): 1.408.213.3191
Support: 1.708.237.6591

## About the Documentation
- Refer to the Technical Documentation page on the Forescout website for additional documentation:
https://www.Forescout.com/company/technical-documentation/
- Have feedback or questions? Write to us at documentation@forescout.com

## Legal Notice
© 2020 Forescout Technologies, Inc. All rights reserved. Forescout Technologies, Inc. is a Delaware corporation.
A list of our trademarks and patents can be found at https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks.
Other brands, products, or service names may be trademarks or service marks of their respective owners.

## About the Jamf App
The Jamf app is an integration of the Forescout platform with Jamf Pro, which is an Apple/iOS MDM management platform. This app lets you pull data from Jamf about the MacOS endpoints managed by the Forescout platform. It also lets you assign specific endpoints to policies on the Jamf platform.

This app is for those Forescout platform users that have Jamf Pro in their environment and want to integrate it with the Forescout platform.

## Requirements

* Forescout version 8.2
* Jamf Pro


## User Interface Overview
After Connect is installed, Connect is displayed under Options. 

![](README.assets/options.png)


## Connect Pane Overview
Initially, the Connect pane is blank. The Jamf app has not been imported yet and the system description has not been configured yet.
![](README.assets/initial.png)


## The buttons on the Connect pane are as follows:
Button  | Description
------------- | -------------
Import  | Import an App
Edit  | Edit an App
Remove  | Remove and App
Start  | Start an App
Stop  | Stop an App

The buttons are described in User Interface Details.

Select Import to import the app into Connect. Apps are in zip or eca format. They can be in any folder.

![](README.assets/import.png)

After an app is imported, the System Description dialog box opens. It is initially blank. See System Description Dialog Box Overview for configuration details.
![](README.assets/desc.png)

After the system description for the app is configured, it is displayed in the Connect pane. There can be multiple apps displayed in this pane.
![](README.assets/connectp.png)

**Third-party vendor integrations are displayed inside the Connect pane, not on the left under Options.

If the configuration has not been saved, select Apply to enable the Start button, which starts an app and the Stop button, which stops an app.

You can select an existing app and then select Edit to open the System Description dialog box.

## System Description Dialog Box Overview
![](README.assets/desc1.png)





## Licenses
This App bundles with a license.txt file. Please review the license.txt file.
