
### About the Cisco FMC App 1.0.0
- App is written to integate only with Cisco FMC v7
- It will add the Endpoint IP to a Dynamic Object Group
- Dynamic Objects are only supported from FMC/FTD v7 onwards

### Future Releases
- App will be modified to support direct integration with FTD

### Requirements
The App supports:
- FMC v7 and its FTDs should be in v7 or higher
- Forescout CounterACT 8.2
- Forescout eyeExtend Connect 1.1


### How it works
- Forescout Cisco FMC app will integrate with Cisco FMC via a Rest API user
- Forescout will share the Endpoint IP based on Policy Action to Cisco FMC Dynamic Object
- Cisco FMC then will share the IP with FTDs near real time which refers the Dynamic Object in a Firewall policy

### User Account Details
- You need to enable 'Rest API' globally which is under REST API preferences
- You need to create a user with following minimum previledges
  - Object Manager , Modify Object Manager
  - REST VDI , Modify REST VDI
- This user account will be used to integrate with Cisco FMC

### Properties - Only for Remote Access VPN via Syslog
- Introduced Properties are 'FMC RAVPN Public IP' and 'FMC RAVPN Username'
- These properties will only be resolved if syslog is forward to the connecting Forescout applicance
- Please see below how to perform a Syslog Mapping

### Actions
- Introduced 'Add to Dynamic Object' action
- This action requires two Properties
  - Domain Name
  - Dynamic Object Name

- Dynamic Object should be refered in the relevant Firewall rule(Access policy)
- Each Dynamic Object is created for a particular Domain. The Default Domain is 'Global'
- Domain names may differ based on how you have architected the Cisco FMC solution


### Syslog Mapping
#### Forescout Configurations to enable syslog parsing
```javascript
  # On the Syslog Receiving Appliance
  ##Custom Traps Event for Cisco FTD VPN
  fstool syslog set_property config.type1.option.ftd_vpn_logs "Cisco FTD VPN Events"
  fstool syslog set_property config.type2.option.ftd_vpn_logs "Cisco FTD VPN Events"

  ## Restart Services
  fstool service restart

  ##Cisco FTD VPN Connect Event

  fstool syslog set_property template.ftd_vpn_connect.type "ftd_vpn_logs"
  fstool syslog set_property template.ftd_vpn_connect.regexp ".*722051.+User\s<([^>]+)\>.+IP\s<([^>]\d+\.\d+\.\d+\.\d+)\>.+Address\s<([^>]\d+\.\d+\.\d+\.\d+)\>.+assigned to session"
  fstool syslog set_property template.ftd_vpn_connect.properties "\$connect_ciscofmc_user,\$connect_ciscofmc_publicip,\$ip"
  fstool syslog set_property template.ftd_vpn_connect.set_true "\$online"


  ##Cisco FTD VPN Disconnect Event
  fstool syslog set_property template.ftd_vpn_disconnect.type "ftd_vpn_logs"
  fstool syslog set_property template.ftd_vpn_disconnect.regexp ".*737016.*Freeing.*address\s(\d+\.\d+\.\d+\.\d+)"
  fstool syslog set_property template.ftd_vpn_disconnect.properties "\$ip"
  fstool syslog set_property template.ftd_vpn_disconnect.set_false "\$online"

  ## Restart Syslog Plugin
  fstool syslog restart
```
#### Forward Syslog to Forescout
```javascript

    1. Go to Devices-> Platform Settings ,
    2. Create a new policy for 'Threat Defense Settings'
        - Give a suitable name
        - Add the VPN FTD Firewalls

    3. Edit the Created Policy and Select 'Syslog' and Under this setting

       a. For Logging Setup
          - Under Basic Logging Setting - > Enable Logging
          - Under VPN Logging Setting -> Enable Logging to FMC and Select Informational
          - Keep the rest of the settings default

       b. For Logging Destinations
          - Add a new Destinations
              * Logging Destination -> Syslog server
              * Event Class - > Filter on Severity - > Select Informational
              * Add the Below Event Classes
                --- Event Class - > SVC , Syslog Severity - > Informational
                --- Event Class -> VPNC , Syslog Severity - > Informational

        c. Under Syslog Settings
          - Select Facility - > Local4
          - Enable timestamp
          - Enable syslog device ID - > Hostname

        d. Under Syslog Servers
          - Enable Allow user traffic to pass when TCP syslog server is down
          - Add the Forescout Syslog Receiving appliance
              * IP and the relevant port should be selected
              * Relevant Security Zones should be selected

      4. Save and Deploy the policy

```
