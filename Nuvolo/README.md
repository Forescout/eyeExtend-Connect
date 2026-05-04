# Nuvolo Connect App

## Overview
Nuvolo Connect App for the Forescout platform that enables seamless synchronization of endpoint discovery data with Nuvolo's ServiceNow-based IT Service Management platform.

## Version
1.0.0

## Features
- **OAuth2 Authentication**: Secure authentication using client credentials flow
- **Asset Data Synchronization**: Automatically post discovered endpoint data to Nuvolo's device discovery staging table
- **Comprehensive Field Mapping**: Maps 20+ Forescout properties to corresponding Nuvolo table columns
- **Proxy Support**: Full proxy configuration support with authentication

### Python Scripts
- **nuvolo_lib.py**: Shared library functions for proxy handling, OAuth2 token management, and API requests
- **nuvolo_authorization.py**: OAuth2 authorization script for token acquisition and refresh
- **nuvolo_test.py**: Configuration validation and API connectivity testing script
- **nuvolo_resolve_properties.py**: Custom property resolver for MAC address and role properties
- **nuvolo_post_asset.py**: Action script to POST endpoint data to Nuvolo staging table

## Custom Properties and Workarounds

### Property Dependency Resolution Issue

Some Forescout properties may not be passed from the managing appliance to action scripts when listed directly as dependencies. To work around this limitation, custom Nuvolo properties are used as intermediaries:

#### Custom Properties:
- **connect_nuvolo_host_mac**: Custom property that resolves the MAC address
  - **Source**: `otsm_details_host_mac_addresses`
  - **Resolver**: `nuvolo_resolve_properties.py`
  - **Format Handling**: Strips brackets and quotes from array format (e.g., `["08:92:04:c0:8b:ee"]` → `08:92:04:c0:8b:ee`)
  
- **connect_nuvolo_host_role**: Custom property that resolves the device role
  - **Source**: `otsm_details_role`
  - **Resolver**: `nuvolo_resolve_properties.py`

#### How It Works:
1. The custom properties (`connect_nuvolo_host_mac`, `connect_nuvolo_host_role`) are defined with dependencies on the base properties
2. The resolver script (`nuvolo_resolve_properties.py`) fetches values from the base properties via `hostinfo` call
3. The resolved values are exposed as custom properties
4. The action script uses these custom properties instead of the direct base properties
5. This ensures reliable property value retrieval across all Forescout appliance configurations

**Note**: If you encounter similar issues with other properties not being passed to actions, the same workaround pattern can be applied by creating additional custom properties with resolver scripts.

## Configuration Requirements

### Nuvolo Instance Settings
- **Nuvolo Instance URL**: ServiceNow instance URL (e.g., `ven05225.service-now.com`)
- **Client ID**: OAuth2 application client identifier
- **Client Secret**: OAuth2 application client secret
- **Forescout Cloud URL**: Base URL for Forescout Cloud asset links (e.g., `https://stg.cloud.forescout.com`)
- **Authorization Refresh Interval**: Token refresh interval (default: 28 minutes)

### Proxy Settings (Optional)
- Proxy server IP and port
- Proxy authentication credentials (if required)

## Field Mappings

The plugin maps the following Forescout properties to Nuvolo table columns:

| Forescout Property              | Nuvolo Column                                         |
|---------------------------------|-------------------------------------------------------|
| otsm_details_first_seen         | u_first_discovered                                    |
| otsm_details_last_seen          | u_most_recent_discovery                               |
| wifi_ap_location                | u_last_discovery_location **      |
| cde_eyefocus_asset_id           | Used to construct u_discovery_source_url *            |
| cysiv_risk_severity             | u_security_impact_overall                             |
| rem_fda_class                   | u_security_impact_patient                             |
| rem_phi                         | u_security_impact_data                                |
| rem_function                    | u_security_impact_business                            |
| cysiv_risk_score                | u_security_risk_score                                 |
| wifi_ssid                       | u_discovered_network_names                            |
| otsm_details_host_name          | u_discovered_hostname                                 |
| os_details_classification       | u_discovered_os, u_discovered_os_version, u_discovered_os_revision *** |
| otsm_details_firmware_version   | u_discovered_firmware_version                         |
| comp_application                | u_discovered_software_version                         |
| connect_nuvolo_host_mac         | u_discovered_mac *****                                |
| ip                              | u_discovered_ip                                       |
| manufacturer_classification     | u_discovered_device                                   |
| connect_nuvolo_host_role        | + u_discovered_device **** *****                      |
| otsm_details_serial_number      | u_discovered_sn                                       |
| sw_ipport                       | u_switch_ip_and_port_number                           |

**Notes**: 
- `*` The `u_discovery_source_url` field is constructed by combining the Forescout Cloud URL (configured in system.conf) with the `cde_eyefocus_asset_id` property in the format: `<forescout_cloud_url>/#/assets/<cde_eyefocus_asset_id>` (e.g., `https://stg.cloud.forescout.com/#/assets/019bb926-b441-7e19-86fb-f07318642ea9`)
- `**` The `u_last_discovery_location` field prioritizes the value from `sw_ipport` first. If `sw_ipport` is not available, the value from `wifi_ap_location` is used.
- `***` The `os_details_classification` property is parsed as JSON to extract multiple values (example format: `{"flavor":"Enterprise","parent":"Windows 11 64-bit","build":"7623.26200","arch":"64-bit","sp":null,"version":"25H2"}`):
  - `parent` and `flavor` fields combined → `u_discovered_os` (e.g., "Windows 11 64-bit - Enterprise")
  - `version` field → `u_discovered_os_version` (e.g., "25H2")
  - `build` field → `u_discovered_os_revision` (e.g., "7623.26200")
- `****` The `u_discovered_device` property is constructed with `manufacturer_classification` field with `-` and the device's role `connect_nuvolo_host_role` (e.g., "Laptop", "Server", "IoT Device"). The final value in `u_discovered_device` would be a combination of the manufacturer and role (e.g., "Dell Inc. - Laptop").
- `*****` Custom Nuvolo properties that resolve values from other properties:
  - `connect_nuvolo_host_mac` resolves from `otsm_details_host_mac_addresses`
  - `connect_nuvolo_host_role` resolves from `otsm_details_role`

## Authentication Flow

1. The authorization script (`nuvolo_authorization.py`) requests an OAuth2 token using client credentials
2. The token is automatically refreshed based on the configured interval
3. All API requests use the Bearer token authentication
4. Token endpoint: `https://<instance>.service-now.com/oauth_token.do`

## API Endpoints

### Token Acquisition
- **Method**: POST
- **Endpoint**: `https://<instance>.service-now.com/oauth_token.do`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Parameters**:
  - `client_id`: OAuth2 client ID
  - `client_secret`: OAuth2 client secret
  - `grant_type`: `client_credentials`

### Post Asset Data
- **Method**: POST
- **Endpoint**: `https://<instance>.service-now.com/api/now/table/x_nuvo_eam_forescout_clinical_device_staging`
- **Content-Type**: `application/json`
- **Headers**:
  - `Authorization`: `Bearer <token>`
  - `Accept`: `application/json`

## Actions

### Post Asset to Nuvolo
Creates a new asset record in the Nuvolo device discovery staging table with discovered endpoint data.

**Dependencies**: All field mappings are defined as dependencies, ensuring that values are populated if the properties exist on the endpoint.

**Response**: Returns success/failure status with troubleshooting information on errors.

## Installation

1. Package all files into a ZIP archive, signed .eca file
2. Import the Connect App through the Forescout Console
3. Configure the Nuvolo instance URL and OAuth2 credentials
4. Assign CounterACT devices to manage the connection
5. Configure proxy settings if required
6. Test the configuration using the built-in test function

## Testing

The test script validates:
1. Credential configuration completeness
2. OAuth2 token acquisition
3. API connectivity to the Nuvolo instance

## Error Handling

All scripts include comprehensive error handling:
- Credential validation
- OAuth2 authentication failures
- API connectivity issues
- HTTP error responses
- JSON parsing errors
- Network timeout handling

## Logging

Debug logging is included throughout for troubleshooting:
- OAuth2 token acquisition
- API requests and responses
- Error conditions and failures
- Configuration validation results

## Compliance

This plugin follows all Forescout Connect App development rules and best practices:
- Script-style (module-level) implementation
- Proper response dictionary structure
- Library function patterns for shared code
- Proxy and SSL configuration support
- Platform-standard naming conventions

## Author
Forescout eyeExtend

## License
See license.txt (if applicable)
