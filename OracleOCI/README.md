# OCI Connect App

Forescout Connect App for integrating with Oracle Cloud Infrastructure (OCI).

## Overview

This Connect App discovers all OCI compute instances across all compartments and subscribed regions in a tenancy. Each instance becomes a Forescout endpoint identified by its VNIC MAC address and private IP, enriched with OCI metadata including shape, lifecycle state, OS image, network details, and storage.

## Requirements

- Forescout platform with Connect module installed
- Oracle Cloud Infrastructure account with API access
- An OCI API signing key configured for a user with the required permissions:
  - **Minimum:** `inspect instance-family` and `inspect virtual-network-family` in the target compartments
  - **Recommended:** The `Reader` role at the tenancy level for full cross-compartment discovery
  - **For volume details:** `inspect volume-family` permission
- Network connectivity from the Forescout appliance to OCI API endpoints (HTTPS on port 443):
  - `iaas.<region>.oraclecloud.com`
  - `identity.<region>.oraclecloud.com`

## OCI API Key Setup

1. In the OCI Console, go to **Identity > Users** and select the user for API access.
2. Under **API Keys**, click **Add API Key**.
3. Choose **Generate API Key Pair** or **Paste Public Key** if you already have one.
4. Download the private key (PEM file) and note the **Fingerprint**.
5. Note the following values from your OCI Console:
   - **Tenancy OCID**: Found under **Administration > Tenancy Details**
   - **User OCID**: Found under **Identity > Users > User Details**
   - **Region** (optional): Your region identifier (e.g. `us-ashburn-1`)

## Installation

1. Import the `.eca` file via the Forescout Connect module.
2. Configure the connection in the **OCI Connection** panel:
   - **Region (optional)**: OCI region identifier (e.g. `us-ashburn-1`). Leave blank to auto-discover all subscribed regions.
   - **Tenancy OCID**: Your tenancy OCID
   - **User OCID**: Your user OCID
   - **API Key Fingerprint**: The fingerprint from your API key
   - **Private Key (PEM)**: Paste the full contents of your PEM private key file
3. Assign a focal appliance in the **Assign CounterACT Devices** panel.
4. Configure discovery frequency and rate limiting in the **OCI Options** panel.
5. Click **Test** to verify connectivity, then **Apply**.

## Region Auto-Discovery

The Region field is optional. When left blank, the app calls the OCI Identity API (`ListRegionSubscriptions`) to discover all subscribed regions in your tenancy and scans them all automatically. When a region is specified, only that region is scanned. This follows the same pattern as the AWS Connect App.

## How It Works

### Discovery (Poll)

The poll script runs on the configured discovery interval and:

1. Determines target regions (from config or auto-discovery).
2. Lists all compartments recursively across the tenancy (compartments are tenancy-wide).
3. For each region and compartment, lists all compute instances (skipping TERMINATED).
4. For each instance, fetches the primary VNIC to extract MAC address and private IP.
5. Resolves the source image to get the operating system name and version.
6. Fetches boot volume and block volume attachments for size and name information.
7. Resolves subnet and VCN display names from OCIDs.
8. Returns endpoints with MAC and IP mapped to Forescout core properties.
9. Sets `online = true` for RUNNING instances, `false` for all other states.

Subnet/VCN names and image OS lookups are cached to avoid redundant API calls when multiple instances share the same network or image.

### Property Resolution (Resolve)

The resolve script handles per-host property lookups:

1. Receives the host's MAC and/or IP address from Forescout.
2. Searches across all target regions and compartments for a matching instance.
3. When matched, returns all instance properties including volumes, network, and image details.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| Instance Name | string | Compute instance display name |
| Instance OCID | string | Unique instance identifier |
| Shape | string | Instance shape (e.g. VM.Standard.E2.1.Micro) |
| Lifecycle State | string | RUNNING, STOPPED, PROVISIONING, etc. |
| Compartment Name | string | Compartment containing the instance |
| Availability Domain | string | Availability domain hosting the instance |
| Fault Domain | string | Fault domain hosting the instance |
| OCPUs | integer | Number of OCPUs allocated |
| Memory (GB) | integer | Memory allocated in gigabytes |
| Image OS | string | Operating system name and version (e.g. "Canonical Ubuntu 24.04") |
| Creation Time | date | Instance creation timestamp |
| Freeform Tags | string | Freeform tags as JSON string |
| Private IP | string | Primary private IP address from VNIC |
| Public IP | string | Public IP address if assigned |
| Private DNS Hostname | string | DNS hostname assigned to the VNIC |
| VNIC Name | string | Display name of the primary VNIC |
| Subnet | string | VCN subnet display name |
| VCN | string | Virtual Cloud Network display name |
| Boot Volume Size (GB) | integer | Boot volume size in gigabytes |
| Block Volumes | composite | List of attached block volumes (name and size) |

## Files

| File | Purpose |
|------|---------|
| system.conf | Connection UI panels and settings |
| property.conf | Property definitions, groups, and script mappings |
| oci_lib.py | Shared library (OCI API signing, HTTP, region discovery, API wrappers) |
| oci_test.py | Connectivity test with region auto-discovery support |
| oci_poll.py | Discovery script - enumerates instances across regions and compartments |
| oci_resolve.py | Per-host instance property resolution across regions |

## Troubleshooting

- **Test fails with HTTP 401**: Verify that the Tenancy OCID, User OCID, Fingerprint, and Private Key are all correct. Ensure the API key is active and the private key matches the public key uploaded to OCI.

- **Test fails with connection error**: The Forescout appliance cannot reach the OCI API. Check that the appliance has outbound HTTPS access to `iaas.<region>.oraclecloud.com` and `identity.<region>.oraclecloud.com`, and proxy settings are configured if needed.

- **Test succeeds but no endpoints discovered**: The API user may lack permissions to list instances or VNICs. Grant the `Reader` role at the tenancy level, or at minimum `inspect instance-family` and `inspect virtual-network-family` in the target compartments.

- **No block volume information**: The API user needs `inspect volume-family` permission to read volume details. Without this, boot volume size and block volumes will show as 0/empty.

- **Instance missing from discovery**: TERMINATED instances are excluded. Instances without a VNIC (no MAC or IP) are also skipped since Forescout requires at least one network identifier.

- **Image OS shows empty**: The image may have been deleted from OCI, or the API user lacks permission to read image details. The app falls back to the image display name, then empty string.

- **Public IP shows empty**: The instance's VNIC does not have a public IP assigned. Assign an ephemeral or reserved public IP in the OCI Console.

- **Freeform Tags shows empty**: Freeform tags are only populated if tags have been applied to the instance in OCI. Defined tags are not included in this property.
