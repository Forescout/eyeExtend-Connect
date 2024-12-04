# Forescout eyeExtend Connect Manifest APP README.md

## Contact Information

Manifest - https://manifestcyber.com
Integrations Team - support@manifestcyber.com

## Requirements

- A valid license to the Manifest platform and live, accessible Manifest tenant.
- Applicable SBOMs uploaded into your Manifest tenant

## About the eyeExtend Connect Manifest App

This integration between Manifest and Forescout enables Forescout to connect to the Manifest API and retrive SBOM and vulnerability data for devices in the Forescout network. This README outlines the installation and usage of the app for developers wishing to extend or modify its functionality.

## Setup
1. In Forescout, import the Manifest Connect App.
2. Configure the Manifest Connect App with your API token and API URL. Where applicable, assign any CounterAct devices and Proxy Settings, then click Next. Scroll over and click the checkbox in the Manifest Agreements section, then click 'Finish'.
3. Create the necessary mappings between the device's `mfst_vendor`, `mfst_model`, and `mfst_firmware` properties and the collected firmware data (see Usage Prereqs below).
4. Manifest data will now be available in the Forescout console for use in policies and rules. 
## Usage Prereqs:
The Manifest integration app looks for 3 properties on the device. These are:
  - `mfst_vendor`: The vendor of the device firmware.
  - `mfst_model`: The model of the device (or its firmware, as applicable).
  - `mfst_firmware`: The firmware version of the device.


## Usage
- The app will automatically fetch SBOM and vulnerability data for devices in the Forescout network. This data will be available in the Forescout console for use in policies and rules.
- Create a mapping between any collected firmware (for example, from Cloud Data Exchange) and the device's `mfst_vendor`, `mfst_model`, and `mfst_firmware` properties. This will allow the app to fetch the correct SBOM and vulnerability data for the device.
- The integration expects that the appropriate SBOMs are available in the Manifest tenant. If the SBOMs are not available, the app will not be able to fetch the SBOM and vulnerability data for the device.


## Available Manifest Properties
The integration app will attempt to attach the following properties in Forescout for each device (when available):
- `Manifest Asset ID`: The ID of the asset in Manifest.
- `Manifest SBOM ID`: The ID of the SBOM in Manifest.
- `Manifest SBOM Upload Date`: The date the SBOM was uploaded and the asset was created in Manifest.
- `Manifest SBOM Download URL`: A URL to download the SBOM from Manifest.
- `Manifest SBOM Relationship`: Indicates whether the SBOM is a first- or third-party (external) entity.
- `Manifest Coordinates`: Derived coordinates (based on CPE and PURLs) for the asset in Manifest.
- `Manifest Risk Score`: A numerical value representing the risk score of the asset in the Manifest platform. 3 is high risk, 2 is medium risk, and 1 is low risk.
- `Total Vulnerabilities Count`: Total number of vulnerabilities found by Manifest in the SBOM for this asset.
- `Critical Vulnerabilities Count`: Critical number of vulnerabilities found by Manifest in the SBOM for this asset.
- `High Vulnerabilities Count`: High number of vulnerabilities found by Manifest in the SBOM for this asset.
- `Medium Vulnerabilities Count`: Medium number of vulnerabilities found by Manifest in the SBOM for this asset.
- `Low Vulnerabilities Count`: Low number of vulnerabilities found by Manifest in the SBOM for this asset.
- `KEV Vulnerabilities Count`: Number of KEV (Known Exploitable Vulnerabilities) found by Manifest in the SBOM for this asset.

The above properties can be used in policies and rules in Forescout.