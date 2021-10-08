# Ubiquiti SDN
eyeExtend Connect App for Ubiquiti enabling discovery, application integillence and control of Ubiquiti SDN Infrastructure and Connected Clients with the Forescout platform.
 
## Versions
1.0.0
1.0.1
1.1.0
1.2.0 
1.2.1
1.2.2

## Change Log
1.2.0
<ul>
<li> Introduced new properties as well as actions </li>
</ul>
1.2.1
<ul>
<li> unreleased, removed unused proxy configuration</li>
</ul>
1.2.2
<ul>
<li>Removed 2 lines from UB_API_NONOO.py containing print function calls which is now rejected in connect apps.  This corrects a failure on installing the app on newer versions of connect plugin.</li>
<li>Incremented version to 1.2.2</li>
</ul>

## Configurations
UnifiOS and Unifi based controllers are supported
Multi site configurations on Unifi Based controllers are supported.  UnifiOS currently does not support multiple sites.

## Supported Use Cases
* Discovery and actionable restriction of endpoints connected to Ubiquiti's Unifi based network devices.  
* Discovery is purely from API calls and does not rely on SSH or SNMP to query for endpoint data.
* Guest authorization based on CounterACT Policy or authentication

### Properties Polled
* Gateway Details:
  * Gateway IP
  * Gateway Firmware Version
  * Gateway Name
  * Gateway Model
* Switch Details:
  * Switch IP Address 
  * Switch MAC Address
  * Switch Firmware Version
  * Switch Name
  * Switch Port
* AP Details:
  * Wireless AP IP Address
  * Wireless Firmware Version
  * Wireless AP Name
  * Wireless SSID
  * Wireless Radio Protocol
  * Wireless Channel
  * Wireless MAC
* Client (USG/UDM Learned) hostname
* Client Alias
* Client Info/Note
* Connectivity Type (Wired or Wireless)
* Controller IP/FQDN
* Role (Controller/Device/Client)
* Site ID
* Guest State
  * Guest Authorized State
* IP Address
* MAC Address
* Network Name

### Properties Resolved with Policies
* Device Model
* Device Name
* Device Serial Number
* Device Type
* Client DPI Stats

### Actions
* Add to Firewall Group (Cancelable)
* Authorize Guest
* Unauthorize Guest
* Block Device (Cancelable)
* Change Port Profile
	* Assign a configured profile to port
	* 802.1x state port profile override
* Disconnect Endpoint

### Policies
* Ubiquiti SDN Application Usage mapped to Compliance state

### Configuration Notes
* FQDN or IP can be used for controller address
* Unifi type is the original unifi controller.  UnifiOS type is UDM/UDM Pro style controller (Port should be changed to 443 for UnifiOS based Controllers)
* Site must be default for UnifiOS.  At this time UnifiOS does not support multiple sites.
* Discover all sites is ignored if UnifiOS type is selected.
* If Polling/Discovery is not enabled, policy resolving and actions are limited to just the default site.

### Action Notes
* Provision Port Profile
  * Applying port profiles that contain overrides will leave those overrides behind if port profile assigned by action does not have same settings overritten
  * Exception to rule above is dot1x auth state override.  Options are:
    * Inherit - Do not set any override, apply whatever port profile dictates
    * force_authorized - Port is always 802.1x authorized
    * auto - Authenticate port via 802.1x
    * forced_unauthorized - port is always 802.1x unauthorized
    * multi_host - allow multi host 802.1x authentication on single port
    * mac_ based - MAB based authorization
  * Port profile name is NOT case sensitive

* Authorize Guest
  * 0 for options does not apply any restrictions and default restrictions that are configured for the guest settings in controller are applied.
  * Authorize for time in minutes
  * limit upload speed in kbps (this ignores any bandwidth group assignments)
  * limit download speed in kbps (this ignores any bandwidth group assignments)
  * Bandwidth Quota in MB - Once total ammount of data defined is used, guest is no longer authorized.

* Disconnect Device
  * Same as clicking Reconnect in Unifi
  * Only applies to wireless endpoints (Unifi Limitation)

<h2>General note</h2>
Applying many actions at the same time can lead to the Unifi API Backend getting confused as to what the end state should be.  This is mostly noticable on UnifiOS based controllers.  If this occurs policy workarounds to avoild mass application of actions such as add/remove to/from firewall group and such should be done.  A future update will target a polling based action trigger which will control this.  Community volunteers are welcomed on implementing this.
