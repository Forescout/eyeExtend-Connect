# Crytica Security Connect App for Forescout

## Overview

Version 1.0.13 is the first official release of the Crytica Security Connect
App. It receives Crytica Security scan alerts in Forescout and stores them on
the matching endpoint. Use the received alert, scan, and operating-system data
in the Asset Inventory, policies, and reports.

This is an inbound integration. Crytica Security sends data to the Forescout
Connect API; Forescout does not poll or otherwise connect to Crytica
Security.

## Before You Begin

- Confirm that the Forescout **Connect** module and app's **Web Service Enabled**.
- Ensure Crytica Security can reach the Connect API endpoint (https://<ip>/connect/v1/hosts)
  over the network.
- Obtain the Connect API credentials for the Crytica Security integration. 
  These credentials are managed in Forescout Connect "Web Service Authentication".
- Ensure Crytica Security sends the IP address that Forescout uses for the
  endpoint. A message with an unknown or malformed IP cannot be applied to an
  endpoint.

## Install and Configure

1. In the Forescout Console, import `ForeScout-eca-crytica-1.0.13.eca` from the
  Connect module.
2. Open the **Crytica Security** app configuration.
3. Enter a **Crytica Security Source Label**. This is a display label that
  identifies the Crytica Security source in the Connect configuration table.
4. Under **Assign CounterACT Devices**, assign the CounterACT device that will
  receive alert messages. If no specific device is assigned, Forescout uses
  the default source assignment.
5. Select **Test**. A successful result means the app is configured and ready
  to receive messages; it does not test network connectivity to Crytica
  Security.
6. Configure Crytica Security to send alert messages to the Forescout Connect
  web-service endpoint with its Connect web-service credentials.

## Send Alert Data

Crytica Security sends a JSON POST in the standard Connect web-API inbound
format. This example sends one alert update for a known endpoint:

```json
{
  "ip": "10.110.1.157",
  "properties": {
    "connect_cryticasecurity_AlertTypeName": "Element Modified",
    "connect_cryticasecurity_AlertMessage": "Element content modified at /usr/bin/sshd",
    "connect_cryticasecurity_AlertEventTimestamp": 1725148800000,
    "connect_cryticasecurity_ElementName": "/usr/bin/sshd",
    "connect_cryticasecurity_DeviceName": "web-server-prod-01"
  }
}
```

- The top-level `ip` identifies the Forescout endpoint the alert belongs to.
- `properties` contains individual, scalar Crytica Security property values.
  Only properties present in a message are updated; earlier values for omitted
  properties remain on the endpoint.
- String properties require JSON strings. Integer and date properties require
  JSON integers. Do not send a property value as an object or list.
- Forescout `date` properties use epoch **milliseconds**. Sending epoch seconds
  is accepted but displays as a date in 1970.
- Unknown Crytica Security-prefixed properties are ignored. Use only the
  declared property names below when configuring alerts.

## Verify Incoming Data

After Crytica Security sends a message, open the endpoint identified by the
message IP in Forescout. The **Crytica Security** property group shows the
received values. Check at least the alert message, alert type, and scan date to
confirm that the integration is working.

If no values appear, first verify that the message IP matches an existing
Forescout endpoint and that the assigned CounterACT device receives the
request. Review the Connect Python log at
`/usr/local/forescout/plugin/connect_module/python_logs/python_server.log` for
message-processing errors.

## Use the Policy Templates

The **Crytica Security** policy-template group includes the following templates:

| Template | Classifications |
|----------|-----------------|
| **Endpoints by Alert Types** | Element Added, Element Deleted, Element Modified, and No Alerts. |
| **Endpoints by Last Security Scan** | Scan within 7 days, scan 7 to 30 days old, scan older than 30 days, and No Scan Data. |
| **Endpoints by OS Types** | Windows, Linux, macOS, and other reported OS types. |

Import the template that fits the desired workflow, then review and customize
the resulting policy before using it for enforcement or automated response.

## Property Reference

| Property | Type | Description |
|----------|------|-------------|
| `connect_cryticasecurity_AlertTypeName` | string | Human-readable alert type name. |
| `connect_cryticasecurity_AlertTypeDescription` | string | Alert type description. |
| `connect_cryticasecurity_AlertCategoryName` | string | Human-readable alert category. |
| `connect_cryticasecurity_AlertCategoryDescription` | string | Alert category description. |
| `connect_cryticasecurity_AlertSubcategoryName` | string | Human-readable alert subcategory. |
| `connect_cryticasecurity_AlertSubcategoryDescription` | string | Alert subcategory description. |
| `connect_cryticasecurity_AlertEventTimestamp` | date (epoch milliseconds) | Time the alert event occurred. |
| `connect_cryticasecurity_AlertMessage` | string | Free-text alert description. |
| `connect_cryticasecurity_ScanDate` | date (epoch milliseconds) | Time the scan ran. |
| `connect_cryticasecurity_ScannedElements` | integer | Number of elements scanned. |
| `connect_cryticasecurity_TotalElements` | integer | Total elements known to the scanner. |
| `connect_cryticasecurity_ScanScope` | string | Scope of the scan. |
| `connect_cryticasecurity_ScanAlertsCounter` | integer | Number of alerts raised by the scan. |
| `connect_cryticasecurity_ElementName` | string | Name or path of the affected element. |
| `connect_cryticasecurity_ElementCreateDate` | date (epoch milliseconds) | Time the element was first observed or created. |
| `connect_cryticasecurity_DeviceUid` | string | Crytica Security device UUID. |
| `connect_cryticasecurity_DeviceName` | string | Crytica Security device name. |
| `connect_cryticasecurity_DeviceOsTypeName` | string | Device OS type name. |
| `connect_cryticasecurity_DeviceOsFlavor` | string | Device OS flavor or distribution. |
| `connect_cryticasecurity_DeviceOsDescription` | string | Free-text OS description. |
| `connect_cryticasecurity_DeviceProcessorTypeName` | string | Device processor architecture. |

## Troubleshooting

| Symptom | Check |
|---------|-------|
| No Crytica Security values on an endpoint | Confirm that the message `ip` exactly matches a known Forescout endpoint, the Connect web service is enabled, and the source is assigned to a CounterACT device. |
| A property value is missing | Confirm that its JSON key exactly matches the property tag, for example `connect_cryticasecurity_AlertMessage`, and that it is sent as a scalar value of the expected type. |
| A date displays in 1970 | Convert the timestamp to epoch milliseconds by multiplying epoch seconds by 1000. |
| The Test action succeeds but alerts do not arrive | The Test action checks only app readiness. Verify Crytica Security network access, endpoint URL, and Connect web-service credentials separately. |

All Crytica Security properties are web-enabled scalar endpoint properties.
Several are also available in the Asset Inventory, and date properties can be
used in date-based policy conditions.
