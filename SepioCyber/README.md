# Sepio Connector for Forescout

## Overview

The **Sepio Connector for Forescout** enhances Forescout’s network visibility and control by integrating **Sepio's hardware asset risk intelligence** directly into the Forescout platform. This integration enables security teams to enforce Zero Trust policies by validating the authenticity and trustworthiness of all connected devices—down to the physical layer.

With Sepio’s unique **AssetDNA™** technology, Forescout users gain unparalleled visibility into connected assets, including rogue, spoofed, or unauthorized hardware. This integration helps mitigate hardware-based threats, reduce attack surfaces, and strengthen compliance across IT, OT, and IoT environments.

## Version 1.0.6 Release Notes

- Updated API call endpoint to Sepio
- Fixed Sepio API token expiration issue
- Optimized the process for retrieving Sepio assets to reduce load

## Version 1.0.7 Release Notes

- Log enhancement
- Add configurable parameter to change number of assets per single API call to Sepio

## Version 1.0.8 Release Notes & Compatibility (November 2025)

- Supported Platforms: Forescout Platform v8.3 and later
- Environments: Linux and Windows appliance deployments

## Version 1.0.9 Release Notes & Compatibility (January 2026)

- Added new custom attribute - "Sepio Asset ID".
- Supported Platforms: Forescout Platform v8.3 and later
- Environments: Linux and Windows appliance deployments

## Key Features

- Enhanced Asset Visibility  
  Leverage Sepio’s physical-layer intelligence to detect all hardware assets—including unmanaged, shadow, and rogue devices.

- Zero Trust Hardware Access  
  Continuously validate device integrity to enforce access policies based on real device identity, not just logical credentials.

- Rogue Device Detection & Mitigation  
  Instantly detect and respond to hardware-based attacks such as network implants (e.g., passive taps) and spoofed peripherals.

- Policy-Driven Automation  
  Enrich Forescout’s policy engine with Sepio’s asset context for automated responses to risk conditions and non-compliant assets.

## Use Cases

- Prevent Hardware-Based MITM Attacks: Detect devices like rogue switches or passive taps introduced into the network.
- Control Unmanaged Peripherals: Identify and restrict unauthorized USB or PCI-connected hardware on endpoints.
- Improve Compliance and Auditing: Maintain accurate asset inventory with physical-layer verification for regulatory alignment.

## Compatibility

- Sepio Platform Version: 17.2506.510
- Forescout Version: 8  
- Integration Type: Data enrichment via API  
- Deployment: On-prem or cloud-managed Sepio environments

## Installation & Configuration

1. Prerequisites
   - A working deployment of Sepio with accessible API endpoint.
   - Forescout Console with admin access.
   - Forescout eyeExtend module enabled.

2. Steps
   - Import the Sepio Connector via the Forescout Console.
   - Configure Sepio API credentials and endpoint settings.
   - Map Sepio asset attributes (e.g., AssetDNA, risk level, vendor authenticity) to Forescout asset properties.
   - Define Forescout policies using Sepio-enriched attributes.

3. Documentation
   - For detailed setup and configuration guidance, refer to the [Integration Guide](https://docs.sepiocyber.com/integrations/configuring-and-editing-integration-settings/configuring-integrations/forescout-connector-app-configuration/).

## Support

For support and questions regarding this integration, please contact:  
Email: support@sepiocyber.com  
Website: https://www.sepiocyber.com

## About Sepio

**Sepio** delivers the industry’s first Zero Trust Hardware Access Control platform, providing visibility, control, and enforcement over every connected device—down to the physical layer. Sepio helps organizations achieve true Zero Trust by eliminating hardware-based blind spots and risks.
