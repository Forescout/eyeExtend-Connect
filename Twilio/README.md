# Twilio – Forescout eyeExtend Connect App

## Overview

This Connect App integrates **Twilio** with Forescout, enabling policy-driven SMS notifications via the Twilio Messages API. Use it to send text alerts triggered by Forescout policy conditions — for example, notifying administrators when a non-compliant device joins the network.

## Capabilities

| Capability | Description |
|---|---|
| **Send SMS** | Send a text message to any phone number via Twilio. Configurable destination number and message body per policy action. |

## Prerequisites

### Twilio Account

1. Sign up at [twilio.com](https://www.twilio.com) (a free trial account works for testing).
2. From the Twilio Console, note your **Account SID** and **Auth Token**.
3. Obtain a Twilio phone number capable of sending SMS.

### Network Requirements

- Forescout appliance must have HTTPS access to `api.twilio.com` (port 443).
- If using a proxy, configure it in the Connect App connection settings.

## Configuration

| Field | Description |
|---|---|
| **Account SID** | Your Twilio Account SID (found in the Twilio Console dashboard) |
| **Auth Token** | Your Twilio Auth Token (found in the Twilio Console dashboard) |
| **From Phone Number** | Twilio phone number to send SMS from, in E.164 format (e.g. `+15551234567`) |

## Action Parameters

### Send SMS

| Parameter | Description |
|---|---|
| **To Phone Number** | Destination phone number in E.164 format (e.g. `+15551234567`) |
| **Message Body** | Text message content to send |

## Scripts

| Script | Purpose |
|---|---|
| `twilio_lib.py` | Shared library (Twilio API helpers, proxy support) |
| `twilio_test.py` | Connection test (validates Account SID, Auth Token, and account status) |
| `twilio_send_sms.py` | Send SMS action |

## Troubleshooting

- **401 Unauthorized**: Account SID or Auth Token is incorrect. Verify credentials in the Twilio Console.
- **Account not active**: The Twilio account may be suspended or closed. Check account status in the Twilio Console.
- **Connection error**: Ensure the Forescout appliance can reach `api.twilio.com` over HTTPS. Check proxy settings if applicable.
- **Invalid phone number**: Ensure both From and To numbers are in E.164 format (e.g. `+15551234567`).

## Version History

| Version | Changes |
|---|---|
| 1.0.0 | Initial release – Send SMS action |
| 1.0.3 | Current version |
