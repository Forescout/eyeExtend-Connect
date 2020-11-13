<mark>Forescout eyeExtend Connect F5 VPN APP README.md</mark>
 

## Contact Information

Have feedback or questions? Write to us at

**<connect-app-help@forescout.com>**

## APP Support

- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.

## About the eyeExtend Connect F5 VPN APP

### Version v1.0.0 F5 VPN APP

F5 VPN APP – connects directly to BIG-IP using the REST API and retrieves properties on connected VPN user sessions.

#### BASH REST API QUERY

This is the process flow to retrieve data.

1. Request sessions

2. Build a list of the sessions

3. Chunk the sessions based on the following option

BASH Page Size = 10

Control queries using the timer
BASH Backoff Timer = 2

##### Example

100 sessions are returned from the initial query.

Therefore the 100 sessions will be chunked up into batched of 10 (Page size)
So the APP will make 10 BASH queries to the F5 Appliance, between these queries backing off 2 seconds for every query.

Query example to the REST API is

sessions_chunks = "1 2 3 4 5 6 7 8 9  10"

BASH Query Body Payload

```json
{
        'command': 'run',
        'utilCmdArgs': f'-c "tmsh -q list apm session {session_chunks}"'
}
```

Use Case 1

- Retrieve VPN sessions data and display various properties in Forescout for policy creation.

~~Use Case 2~~

- ~~DisconnectVPN sessions~~

~~The APP enhances Forescout data content for remote endpoint sessions.~~

**<mark>REMOVED DUE TO REST API RESPONSE ALWAYS BEING HTTP 200 OK.**</mark>

<mark>**DURING TESTING**</mark>

<mark>**WHEN AN INVALID SESSION ID WAS USED, THE HTTP RESPONSE 200 OK</mark>

<mark> WAS RETURNED BY THE REST API**</mark>

*f5vpn_disconnect_session.py*, is provided separately and isn't imbedded with the eca file for the App.
The properties.conf section relating to the action has been removed.

If you want to add back the action for testing, add the following to the properties.conf. As well as taking the f5vpn_disconnect_session.py and creating a zip file to update the app and include the disconnect functionality.

Line 370 **

```json
    "actions": [
        {
            "name": "connect_f5vpn_disconnect_session",
            "label": "Disconnect Session",
            "group": "connect_f5vpn",
            "description": "Disconnect Session",
            "ip_required": false,
            "threshold_percentage": 1,
            "dependencies": [
                {
                    "name": "connect_f5vpn_session_id",
                    "redo_new": fasle,
                    "redo_change": false
                }
            ]
        }
    ],
```

Line 383 (Before above insert)

```json
,
        {
            "name": "f5vpn_disconnect_session.py",
            "actions": [
                "connect_f5vpn_disconnect_session"
            ]
        }
```

## Requirements

- BIG-IP AMP Management

- Forescout CounterACT 8.1.4 onwards

- Forescout eyeExtend Connect Package 1.1 or higher

- See license.txt file for license information

  ----------------------------------------------------------------------------------------------------------------------------------------------------

## User Interface

Walking through adding an appliance wizard configuration, you will be present with 4 panels.

**F5 BIG-IP Panels**

#### Predefined fields used panels

- Certification validation
- Authorization
- Rate limiter

#### Rate limited API Count

- User can set rate-limiter for the API allowed to the F5 VPN per unit time.
- Default in the APP is allowing up to 100 API calls per second.
- Range is 1 to 1000.
- Set in the system.conf file

### Panels

#### F5 VPN Configuration

F5 VPN Connection

| Property                    | Comment                        |
|:--------------------------- |:------------------------------ |
| F5 Managment URL            | Example https://<name> or <ip> |
| Username                    | Default **none**               |
| Password                    | Default **none**               |
| Validate Server Certificate | Not Selected                   |

### F5 VPN Options

| Property                            | Comment                                                                        |
|:----------------------------------- |:------------------------------------------------------------------------------ |
| Enable Host Discovery               | **Required and should be checked**                                             |
| Discovery Frequency (Mintutes)      | Default **8**<br>How often to poll F5 Management appliance                     |
| Authorization                       | Default **15**<br>How often the APP will request a new token                   |
| BASH Page Size                      | How many session-id's to ask for per request                                   |
| BASH Backoff Timer (Seconds)        | The number of seconds to wait before requesting another BASH Page Size request |
| Number of API queries per unit time | Default **100**<br>See rate-limited-api-count                                  |

  ----------------------------------------------------------------------------------------------------------------------------------------------------

#### Focal appliance

Assign a Forescout focal appliance.

### Proxy Server

Used to define proxy settings.

### Test button

- Test is enabled by default.
- Device info need to be saved (applied) before test can be successfully run.

Example F5 VPN Test Result

```
ADD TEST RESULT TEXT HERE
```

  ----------------------------------------------------------------------------------------------------------------------------------------------------

## Manage the APP

### Import

- User can import the F5 VPN Connect APP via eyeExtend Connect module

- APP file shall look like F5VPN-App.ECP which is signed

  ## Start and Stop APP

- User can start and stop the F5 VPN App

- When the APP is stopped, all properties resolve, actions and policy are suspended.

  ### Remove APP

- User can remove the APP if no longer needed

- User need to delete the F5 VPN policy first to remove the App.

  ----------------------------------------------------------------------------------------------------------------------------------------------------

  ## Policy Templates

- Checks that the F5 has reputation check enabled for the endpoint

  - After importing the APP the policy can be find under Policy > Add > F5 VPN > F5 VPN Endpoint Reputation Check

    ----------------------------------------------------------------------------------------------------------------------------------------------------

## Properties

There are a few properties gathered from the F5 VPN for the endpoint.

**These are all obtained from the BASH query, apart from the Session ID**

| Property                       |
|:------------------------------ |
| F5 Client Sessions ID          |
| F5 Client Tunnel IP            |
| F5 Client Local IP             |
| F5 Client Local MAC Address    |
| F5 Logon Domain Name           |
| F5 Anti-Virus Name             |
| F5 Anti-Virus Signature        |
| F5 Anti-Virus Vendor           |
| F5 Anti-Virus Version          |
| F5 Firewall Name               |
| F5 Firewall Signature          |
| F5 Firewall Vendor             |
| F5 Firewall Version            |
| F5 Client Host Name            |
| F5 Client Platform             |
| F5 Logon Name                  |
| F5 Logon Username              |
| F5 Inspection Status           |
| F5 Inspection Status Timestamp |
| F5 VPN Server Name             |
| F5 VPN Server Port             |
| F5 VPN Server Protocol         |
| F5 Client Reputation           |
| F5 User Start Time             |

  ----------------------------------------------------------------------------------------------------------------------------------------------------

## Scripts

* Discovery used to poll for VPN sessions

  **f5vpn_poll.py**

* Used by the Authorization timer to keep the token upto date

  **f5vpn_authorization.py**

* Test authentication to F5 VPN Appliances
  **f5vpn_test.py**

* *This script is not enbled in the properties.conf file*. (See note above)

  f5vpn_disconnect_session.py

  ----------------------------------------------------------------------------------------------------------------------------------------------------

## Footnote
