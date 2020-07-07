 
Forescout eyeExtend Connect Cherwell App README.md
 
## About the eyeExtend Connect Cherwell App
The Cherwell Connect App gathers and shares endpoint information with the Cherwell CMDB which enables the management of assets. With a bi-direction syncronization of the data Forescout is then able to create IT Incidents that will have the appropriate CI linked to the record to ensure end-to-end tracking.  

## Support Requirements
- Cherwell
- Forescout CounterACT 8.2
- Forescout eyeExtend Connect 1.1

## Features and updates with v1.0.0 Cherwell App
This version adds supports for
- Real-time endpoint update to the Cherwell CMDB through the use of a staging table
- Device Discovery - enables periodic polling to discover new clients via Cherwell CMDB entries
- Provides for the ability to submit an IT Incident with the CMDB CI associated

### Required Cherwell Updates
- Addition of a Forescout field to make a link between Forescout device and CMDB device. (This needs to be manually added to Configuration Item)
- mApp for Cherwell provides for the Forescout Import Table and is needed in order to complete the integration
- One-Step(s) will need to be created to move the data from the Forescout Import Table to the CMDB production tables

### Rate-limited API Count
- User can set rate-limiter for the API allowed to the Cherwell per unit time.
- Default in the App is allowing up to 100 API calls per second.
- Range is 1 to 1000 APIs.

### Test button
- Test is enabled by default.
- Checks for Cherwell connection and pulls Business Object ID for the CMDB tables.

### Policy Templates
- There are three default Cherwell Template
- Add asset to the CMDB which adds the device to the Forescout import table to be processed by the clients One-Step
- Update asset in the CMDB which will push the device information to the Froescout import table, includeing the Cherwell CMDB record ID, to then be processed byt a client supplied One-Step
- Creation of an IT Incident Record with the CI display name and record id to link the incident to the CI.  It may be necessary to extend capabilities in a One-Step in order to complete the linking of the two records.

### Actions
- Add an Asset to the Cherwell CMDB
- Update an Asset in the Cherwell CMDB
- Create an IT Incident in the Cherwell CMDB
