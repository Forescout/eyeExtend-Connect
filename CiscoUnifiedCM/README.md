# Forescout eyeExtend Connect for Cisco UCM README

## About the Cisco UCM App 1.0.0

- App is written to integate only with Cisco UCM v11.5.1 & 12.5.1
- It queries the Unified Call Manager if the Cisco Phone is registered.
- Connects via API

## Requirements

The App have been tested on this environment:

- Cisco UCM v11.5.1 & 12.5.1
- Forescout CounterACT 8.3.0.1
-Forescout eyeExtend Connect 2.0.9
- Only one CounterACT can be assigned for each Cisco UCM instance configured on the App

## How it works

- Forescout Cisco UCM App integrates with Cisco UCM via a Rest API users
- Forescout will query with VoIP device IPv4 address on the Cisco UCM server if a Cisco phone is registered or not, helping with the classification of the Corporate VoIP devices assigning the status of “Registered”

## User Account Details

- You need to enable 'Rest API' globally which is under REST API preferences
- You need to create a user with RO permissions
- This user account will be used in the Connect APP

## Properties – CUCM\_Status

This property checks for the device’s status on the Cisco UCM platform where we can retrieve information about the status of the device. If the device is not registered in Cisco UCM, it returns <blank> response.

## Reference

RisPort70 API Reference - Call Detail Records on Demand SOAP Service API Developer Guide - Document - Cisco Developer <https://developer.cisco.com/docs/sxml/#!risport70-api-reference/risport70-api-reference>
