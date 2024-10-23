# Forescout eyeExtend Connect Darktrace APP README.md

## Contact Information

Darktrace - https://customerportal.darktrace.com/\
Integrations Team - integrationsupport@darktrace.com

## Requirements

- Darktrace RESPOND/Network license
- Darktrace log forwarding (in JSON format)

## About the eyeExtend Connect Darktrace APP

This integration between Darktrace and Forescout enables Forescout to collect details when a device is actioned by Darktrace RESPOND. This allows for policies to be created within Forescout, extending the response action from Darktrace to the NAC level.

## Setup

1. Configure **Syslog** module for JSON format forwarding under **Workflow Integrations** in Darktrace.
2. Set **Application Name** with desired name.
3. Enable **Send RESPOND Alerts**.
4. In Forescout, import Darktrace Connect APP.
5. Configure module, ensuring Syslog Source is toggled on and Syslog Source is set to the Darktrace IP/hostname.
6. The system is now ready to use the added custom properties in policies as per typical Forescout recommendations and flow.

## How it works

Darktrace forwards RESPOND logs via syslog towards a Forescout focal appliance, allowing Forescout to interpret the device IP, action, and inhibitor fields behind a Darktrace RESPOND event.\
To determine the device on which the action is to be applied, the module extracts the device IP address from the Darktrace event log.\
Forescout will also interpret the value of the field 'action' in syslogs forwarded from Darktrace to determine if a block has to be put in place. The action field corresponds to the Darktrace RESPOND states: `CLEAR`, `CONFIRM`, `CREATE`, `EXPIRE`, `EXTEND`, `REACTIVATE_CLEARED`, `REACTIVATE_EXPIRED`, `CREATE_NEEDSCONFIRMATION`. These indicate if the action is e.g. new and to be executed, existing and being extended, or existing but to be deleted, etc. The state `CREATE_NEEDSCONFIRMATION` is purposely ignored by this integration and will have no impact on any active or inactive action.\
Currently, only the inhibitor for "Quarantine" is supported and interpreted in the provided Darktrace policy.

## How to test

Darktrace RESPOND blocks will be displayed in the `Policies` tab under the `Darktrace Quarantine` folder. The `Block` tab shows any currently active RESPOND actions, while the `Unblock` tab shows any cleared or expired actions. The switch block action status can be seen in the description at the bottom, as well as on under the Actions column, represented by a Forescout assigned icon. Actions applied to the Forescout platform will not have dedicated status updates within the Darktrace RESPOND Actions page.