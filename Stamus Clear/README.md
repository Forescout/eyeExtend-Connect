# Forescout eyeExtend Connect Stamus Networks APP README.md

## Contact Information

Stamus Networks - https://support.stamus-networks.com/
Support Team - support@stamus-networks.com

## Requirements

- Clear NDR at release 40.0.1 or later
- Network access from Clear NDR to Forescout eyeExtend Connect

## About the eyeExtend Connect Stamus Networks APP

This integration between Stamus Networks and Forescout enables Forescout to be notified when a Declaration of Compromises (DoC) or a policy violation (DopV) is seen on a device. This allows for policies to be created within Forescout, extending the response action from Stamus Networks to the NAC level.

## Setup

1. In Forescout, import Stamus Networks Connect APP.
2. Create a user/password in eyeExtend for the connection from Clear NDR Manager to Forescout eyeExtend Connect.
3. Setup a webhook in Clear NDR Manager that uses Forescout authentication and set the user/password value to the one created in previous step. (see https://docs.stamus-networks.com/40.0.1/administration/webhooks.html)

## How it works

Clear NDR Manager is calling a REST API endpoint on Forescout eyeExtend Connect to indicate that a DoC or a DoPV has been seen
on a host. This populate various information about the threat that can then be used to trigger an action at the NAC level.
When necessary remediation has been done, the reset action can be called to reset the fields created by the initial REST API
call done by Clear NDR.

## How to test

DoC or DoPV will be displayed in the detailed information about the host. Actions following the discovery of a threat
can be triggered using the provided policy template.
