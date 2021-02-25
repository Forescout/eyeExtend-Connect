Forescout eyeExtend Connect Fortinet VPN APP README.md
 

## Contact Information

- Have feedback or questions? Write to us at SMEOrchestration@forescout.onmicrosoft.com

## APP Support

- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.

## About the eyeExtend Connect Fortinet VPN APP

### Version v1.3.0 - Fixes issue related to polling/discovery script failure with SSL-VPN Web User; Removes proxy panel from deployment wizard

### Version v1.0.0 Fortinet VPN APP

Fortinet VPN APP – connects directly to FMG/FGT using the REST API and retrieves properties on connected VPN user sessions.

Control Actions

- Drop (disconnect) VPN existing VPN sessions.
- Disable local Users Accounts From accessing the network.

Use Case 1

- Retrieve VPN sessions data and display various properties in Forescout for policy creation.

Use Case 2

- Drop VPN sessions or Disable Local User accounts, based on policy conditions.

The APP enhances Forescout data content for remote endpoint sessions.

## Requirements

- FortiManager (FMG) and FortiGate (FGT). Tested versions 6.0.2, 6.0.9, 6.2.3

- VDOM and ADOM is supported.

- Forescout CounterACT 8.2, 8.1.4

- Forescout eyeExtend Connect 1.5 or higher

- See license.txt file for license information

  ----------------------------------------------------------------------------------------------------------------------------------------------------

## User Interface

Walking through adding an appliance wizard configuration, you will be present with 6 panels.

**NOTE ForiGate/FortiManager Panels**

1. **Device panels cannot be disabled based on a selection.**
2. **Panel properties do not support a type of list**

_Example 1_
If you are configuring a FortiGate
You will still have to complete the details on the FortiManager panel.

FortiManager/FortiGate panels have dummy default values that will be ignored based on the Fortinet Device. You can select NEXT and skip over the configuration’s properties.

Fortinet Device = FortiGate, you can skip FortiManager panel configuration.
Fortinet Device = FortiManager, you can skip the FortiGate panel configurations.

_Example 2_
Typically focal appliance(s) only allow 1 Fortinet device per Forescout appliance.

To allow for multiple FortiGate appliances to be configured on a single Forescout appliance and property list type are not support at present.
The APP allows for upto 4 FortiGate Devices and Keys on the FortiGate device panel.

#### Predefined fields used panels

- Certification validation
- Authorization
- Rate limiter

#### Rate limited API Count

- User can set rate-limiter for the API allowed to the Fortinet VPN per unit time.
- Default in the APP is allowing up to 10 API calls per second.
- Range is 1 to 100.
- Set in the system.conf file

### Panels

#### FortiGate Configuration

Upto 4 FortiGate devices are allowed per Forescout focal appliances.

**Remember if you are not adding a FortiGate appliance, you can click NEXT**

**and skip this panel.**

| Property                  | Comment                         |
|:------------------------- |:------------------------------- |
| FortiGate IP [1]          | Default **none**<br>**IP Only** |
| REST API Admin [1]        | ********                        |
| Verify REST API Admin [1] | ********                        |
| FortiGate IP [2]          | Default **none**<br>**IP Only** |
| REST API Admin [2]        | ********                        |
| Verify REST API Admin [2] | ********                        |
| FortiGate IP [3]          | Default **none**<br>**IP Only** |
| REST API Admin [3]        | ********                        |
| Verify REST API Admin [3] | ********                        |
| FortiGate IP [4]          | Default **none**<br>**IP Only** |
| REST API Admin [4]        | ********                        |
| Verify REST API Admin [4] | ********                        |

### FortiManager Configuration

**Remember if you are not adding a FortiGate appliance, you can skip this panel.**

Multiple Administrator Domains (ADOM) can be added, one per line.

| Property                     | Comment                         |
| ---------------------------- | ------------------------------- |
| FortiManager IP              | Default **none**<br>**IP Only** |
| FortiManager User            | Default **none**                |
| FortiManager Password        | ********                        |
| Verify FortiManager Password | ********                        |
| FortiManager ADOM            | Default **root**                |

### Fortinet VPN Options

Fortinet options

| Property                         | Comment                                                                 |
|:-------------------------------- |:----------------------------------------------------------------------- |
| Enable Host Discovery            | **Required and should be checked**                                      |
| Discovery Frequency (Mintutes)   | Default **3**<br>How often to poll FortiManager/FortiGate               |
| Number of API queries per second | Default **10**<br>[See Rate limited API Count](#rate-limited-api-count) |

  ----------------------------------------------------------------------------------------------------------------------------------------------------

#### Focal appliance

Each Forescout appliance allows for upto 4 Fortigate appliances to be configured

*You can have a mix as an example 4 FortiGate and 1 FortiManager*

### Proxy Server

Used to define proxy settings.

### Test button

- Test is enabled by default.
- Device info need to be saved (applied) before test can be successfully run.

Example FortiGate Test Result

```
Test failed:
FortiGate 192.168.x.1 - Connection Successful : Serial-xxxxxxxxxx version=6.0.9.335
FortiGate 192.168.x.2 - Connection Failed: Check IP/API Key
```

Example FortiManager Test Result



```
Test failed:
FortiManager - Error: ADOM adom1 doesn't exist
FortiManager - FGT-Home(192.x.x.x) VDOM: root - Connection Successful
FortiManager - FGT-Home(192.x.x.x) VDOM: vdom_test - Connection Successful
FortiManager - Error: ADOM adom2 doesn't exist
```

  ----------------------------------------------------------------------------------------------------------------------------------------------------

## Manage the APP

### Import

- User can import the Fortinet VPN Connect APP via eyeExtend Connect module

- APP file shall look like Fortinet-VPNApp.ECP which is signed

  ## Start and Stop APP

- User can start and stop the Fortinet VPN App

- When the APP is stopped, all properties resolve, actions and policy are suspended.

  ### Remove APP

- User can remove the APP if no longer needed

- User need to delete the Fortinet VPN policy first to remove the App.

  ----------------------------------------------------------------------------------------------------------------------------------------------------

  ## Policy Templates

- There is a default Fortinet VPN Template

  - After importing the APP the policy can be find under Policy > Add > Fortinet VPN > Fortinet VPN disable non-compliant device

        The policy has 2 actions enabled.

            _Drop VPN_

            _Disable Local User_

    ----------------------------------------------------------------------------------------------------------------------------------------------------

    ## Actions

- Down/Terminate the IPSec / SSL tunnel. **Drop VPN**

- Disable/Enable local users account(s). **Disable Local User**

  - Not Available on FortiManager

    ----------------------------------------------------------------------------------------------------------------------------------------------------

## Properties

There are a few properties gathered from the Fortinet VPN for the endpoint.

- Fortigate IP

- Fortigate Serial Number

- Device learnt from

- Fortigate Hostname

- Fortigate VDOM

- Fortigate Version

- Fortinet VPN User

- Fortinet VPN Type

- Fortinet VPN IPSEC p1name

- Fortinet VPN IPSEC p2name

- Fortinet VPN IPSEC p2serial

- Fortinet VPN SSL index

- Fortinet VPN External IP

  ----------------------------------------------------------------------------------------------------------------------------------------------------

## Scripts

* Discovery used to poll for VPN sessions
  **fvpn_poll.py**

* Disable local user account
  **fvpn_disable_user.py**

* Enable local user account
  **fvpn_enable_user.py**

* Drop VPN
  **fvpn_vpn_down.py**

* Test authentication to Fortinet Appliances
  **fvpn_test.py**

  ----------------------------------------------------------------------------------------------------------------------------------------------------

## Footnote
