## About the app

The application enables integration between Forescout platform and Appgate SDP via REST API.

### Capabilities
- Detect Appgate client devices connection/disconnection events.
- Passive learning of Device ID, Username and Identity Provider of the connected endpoint.
- Collecting additional host properties about the endpoint from Appgate Controller.
- Polling the Appgate Controller for the list of connected devices and their properties.
- Adding and removing the user to/from Blacklist (all connected devices of the user are blacklisted)

### Tested on:
- Appgate Controller 6.4.5
- Forescout CounterACT 9.1.2
- eyeExtend Connect Module 2.0.2

### Configuration

#### Appgate SDP Controller Side
- API user with "View all Session Info", "Revoke all Token Records", "All privileges all Blacklists" permissions
- Forescout appliance IP configured as an rsyslog destination on the Appgate Controller

#### Forescout Connect App Side
| Option                                   | Comment                                      |
|:-----------------------------------------|:-------------------------------------------  |
| Controller FQDN                          | Appgate Controller to connect to             |
| API User                                 | username for authentication                  |
| Identity Provider                        | IdP of the API User                          |
| API version                              | API version used by your Appgate deployment  |
| Client UUID                              | UUID to distinguish the app                  |
| Validate Server Certificate              | Check to verify trust for API connections    |
| Use syslog source                        | If app will parse syslog messages            |
| Syslog Source Name or IP                 | Controller that will send syslog to the app  |
| Enable Host Discovery                    | If app will periodically poll the Controller |

### Available Properties and Actions

| Property                                 | Comment                                      |
|:-----------------------------------------|:-------------------------------------------  |
| Appgate SDP User                         | Base property. Required to discover other properties. Can be learned from syslog on device connect, or polling |
| Appgate Client Device ID                 | Base property. Required to discover other properties. Can be learned from syslog on device connect, or polling |
| Appgate Client Identity Provider         | Base property. Required to discover other properties. Can be learned from syslog on device connect, or polling |
| Appgate Client Hostname                  | Device Hostname                              |
| Appgate Client Connected Sites           | List of sites the client is connected to     |
| Appgate Client Country Code              | Originating country                          |
| Appgate Client is Domain                 | If the device is domain-joined               |
| Appgate Client is Firewall enabled       | Is local FW enabled on the device            |
| Appgate Client is user admin             | If the local device user has OS admin rights |

| Action                                   | Comment                                      |
|:-----------------------------------------|:-------------------------------------------  |
| Blacklist User                           | Requires username and IdP.                    |

> [!CAUTION]
> Blacklist User action will blacklist ALL devices for the selected user, not just the one being blocked

### Policy templates

- Appgate SDP Discovery<br>
  Learn additional properties of devices connected to Appgate SDP.<br>
  For this policy to succeed, Forescout must already know Device ID, User and its IdP from Syslog. <br>
  The flow is the following:<br>
  <ul><li>Once an endpoint is connected to Appgate, the Controller then sends a syslog message containing Device Tunnel IP, Device ID, Username and IdP to Forescout</li>
  <li>Connect App parses the message and learns those properties immediately upon connection.</li>
  <li>This policy then uses these properties to trigger Connect App to query Controller for additional device properties.</ul>
  These properties can be also learned during Appgate Controller polling, but this policy expedites this process and gives a possibility to reduce network and API load.
