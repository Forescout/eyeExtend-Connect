 
Forescout eyeExtend Connect WayPoint App README.md
 
## About the eyeExtend Connect WayPoint App
The WayPoint Connect App gathers and shares endpoint information with the Ivanti WayPoint CMDB which enables the management of assets. With a bi-directional synchronization of the data, Forescout is then able to create IT Incidents that will have the appropriate CI linked to the record to ensure end-to-end tracking.  

## Support Requirements
- Ivanti WayPoint (formerly Ivanti Service Manager)
- Forescout CounterACT 8.5
- Forescout eyeExtend Connect 2.0.6

## Features and updates with v2.0.01 WayPoint App
This version adds support for:
- Real-time endpoint update to the WayPoint CMDB through the use of a staging table
- Device Discovery - enables periodic polling to discover new clients via WayPoint CMDB entries
- Provides for the ability to submit an IT Incident with the CMDB CI associated
- Session management with automatic logout to respect concurrent session limits
- Comprehensive error handling and validation

## Versions
* 2.0.01 Release
  - DRY Principle: Eliminated duplicated code between add/update operations
  - Error Handling: Comprehensive exception handling with specific error types
  - Validation: Added input validation for params, URLs, tokens, and business object IDs
  - Session Management: Automated session logout before new authentication to respect concurrent session limits
  - Modularity: Separated concerns into device, field_mappings, http_client and validators modules
  - Maintainability: Much easier to update field mappings and add new features
  - Testing: More testable code with smaller, focused functions
  - Tenant Extraction: Automatic tenant extraction from base URL for authentication

### Required WayPoint Updates
- Addition of a Forescout field to make a link between Forescout device and CMDB device. (This needs to be manually added to Configuration Item)
- Import table for WayPoint provides for the Forescout Import Table and is needed in order to complete the integration
- One-Step(s) or workflow automation will need to be created to move the data from the Forescout Import Table to the CMDB production tables

### Rate-limited API Count
- User can set rate-limiter for the API allowed to WayPoint per unit time
- Default in the App is allowing up to 100 API calls per second
- Range is 1 to 1000 APIs

### Test button
- Test is enabled by default
- Checks for WayPoint connection and pulls Business Object ID for the CMDB tables
- Validates authentication and tenant configuration

### Policy Templates
- There are three default WayPoint Templates:
- Add asset to the CMDB which adds the device to the Forescout import table to be processed by the client's One-Step
- Update asset in the CMDB which will push the device information to the Forescout import table, including the WayPoint CMDB record ID, to then be processed by a client supplied One-Step
- Creation of an IT Incident Record with the CI display name and record id to link the incident to the CI. It may be necessary to extend capabilities in a One-Step in order to complete the linking of the two records

### Actions
- Add an Asset to the WayPoint CMDB
- Update an Asset in the WayPoint CMDB
- Create an IT Incident in the WayPoint CMDB

### Properties
The WayPoint App provides the following properties that can be resolved and tracked:
- **WayPoint Contract ID**: The contract ID for the device in WayPoint
- **WayPoint CMDB Class Obj ID**: The object ID of the CMDB class in WayPoint
- **WayPoint Record ID**: The record number of the device retrieved from WayPoint

All properties support:
- Change tracking
- Asset portal visibility
- Inventory management
- Dependencies on MAC address, hostname, and classification changes

## Configuration
The WayPoint App requires the following configuration parameters:
- **WayPoint Base URL**: The REST API URL (e.g., https://tenant.ivanticloud.com/api)
- **Service Account**: Username for authentication
- **Service Account Password**: Password for authentication
- **Service Account Role**: Role name for the service account (e.g., ServiceDeskAnalyst)

## Installation
1. Import the WayPoint App (.eca file) into Forescout eyeExtend Connect
2. Configure the connection parameters in the WayPoint Connection panel
3. Test the connection using the built-in test button
4. Configure policy templates as needed for your environment
5. Ensure WayPoint has the required Forescout import table and workflows configured
