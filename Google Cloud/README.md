Forescout eyeExtend Connect Google Compute Engine APP README.md
 
## Contact Information
- Have feedback or questions? Write to us at SMEOrchestration@forescout.onmicrosoft.com

## APP Support
- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.

## About the eyeExtend Connect Google Compute Engine APP
### Version v1.0.0 Google Compute Engine APP
The APP gathers Compute Engine information, allowing you to build Forescout policies relating to the Compute Engine(s)
- REST API will discover all Google Compute Engine(s) that the "Service Account" has permissions to read.
    - Enable Host Discovery' flag is enabled **Recommended**
- Action    **Start/Stop** Compute Engine instance(s)
    - Actions **Start/Stop** will need write permisions to start and stop instances.

**Note    The Google API does not expose the MAC Address**

## Requirements

- Access to Google Cloud Compute (Free Trial Accounts are available)
    https://cloud.google.com/free/
- Forescout CounterACT 8.2, 8.1.4
- Forescout eyeExtend Connect 1.5 or higher
- See license.txt file for license information
## User Interface
You can refer to the Forescout eyeExtend Connect Module: Connect Application Building Guide, in particular the
sections on ”Define system.conf File” and “User Interface Details”.

#### Predefined fields used panels
- Certification validation
- Authorization
- Rate limiter

##### Rate-limited API Count
- User can set rate-limiter for the API allowed to the Google Compute Engine per unit time.
- Default in the APP is allowing up to 100 API calls per second.
- Range is 1 to 1000 APIs.

### Panels
#### Google Cloud Platform Engine
Google Cloud Authentication credentials.

|Property | Comment |
|:---|:---|
|Service Account Client Email| *some-user@some-place.iam.gserviceaccount.com*|
|Private Key for the Service Account Client Email |-----BEGIN PRIVATE KEY-----<br>MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDby7FEgurr093<br>...<br>3mnujIgLPEr8GJX7Ln32bEnEnKv4cQYZsH8C3nxP5KjBCCtYJY344xcH9MtMJtDp<br>A4QsA/tYJP8iL0GXb8mcr8A=<br>-----END PRIVATE KEY-----<br>**At present this is unencrypted longString does not allow to be hidden**<br>**New Lines Required**|
|Aud URI|Default **https://oauth2.googleapis.com/token**<br>Google region to login|
|Forbidden Projects|Default **Remote** <br>(Space sepearte list of Projects) [^1]|
|OAuth2 Scope|Default **https://www.googleapis.com/auth/cloud-platform https://www.googleapis.com/auth/cloud-platform.read-only** [^2]|

[^1]: A space seperate list of projects. 
When the API resturns a list of projects as an example "Remote" is a system defined one. You can not add compute instances to "Remote".
This field is used to skip instance queries to these project(s)
[^2]: Needed to build the OAuth2 scope to obtain the bearer token.
Permissions can be set in IAM.
Did not want to hard code into the APP

### Google Compute Engine Options
|Property | Comment|
|:---|:---|
|Enable Host Discovery|**Required and should be checked**|
|Discovery Frequency (Mintutes)|Default **60**<br>How often to poll Google Compute Cloud|
|Authorization (Minutes)|Default **55**<br>How often to update the bearer token|
|Page Size|Default **500**<br>This is the number of Compute Engine instance returned per query<br>Example: 1000 instances, the APP will make 2 queries to obtain data for the 1000 instances

#### Focal appliance
Each "Service Account Client Email" shall run on one dedicated focal appliance.

### Proxy Server
Used to define proxy settings.

### Test button
- Test is enabled by default.
- Device info need to be saved (applied) before test can be successfully run.

Example Test Result
```
Test succeeded:
Successfully connected. No. of Projects 3
```
## Manage the APP
### Import
- User can import the Google Compute Engine Connect APPvia eyeExtend Connect module
- APP file shall look like Google Compute EngineApp.ECP which is signed
## Start and Stop APP
- User can start and stop the Google Compute Engine App
- When the APP is stopped, all properties resolve, actions and policy are suspended.
### Remove APP
- User can remove the APP if no longer needed
- User need to delete the Google Compute Engine policy first to remove the App.
## Policy Templates
- There is a default Google Compute Engine Template
- After importing the App. the policy can be find under Policy > Add > Google Compute Engine > Google Compute Engine by Regions
## Actions
- Stop Google Engine
- Start Google Engine
## Properties
There are a few properties gathered from the Google Compute Engine for the endpoint.
- Google Engine ID
- Google Engine Status
- Google Engine Project Name
- Google Engine Project ID
- Google Engine Name
- Google Engine Create Time
- Google Engine Zone
- Google Engine Type
- Google Engine Can Forward IP
- Google Engine CPU Platform
- Google Engine Restricted to Start
- Google Engine Deletion Protection
- Google Engine Disk Info
     - Disk Type
    - Device Name
    - Boot Disk
    - Auto Delete Disk
    - Disk Interface
    - Guest OS Features Type
    - Disk Size GB
- Google Engine Network Info
    - Interface Name
    - Connevted Network
    - Connected Subnetwork
    - External IP

## Scripts
* Authorzation used to get/updated the bearer token
**gce_authorization.py**
* Discovery used to poll for Compute Engine instance
**gce_poll.py**
* Resolve properties requires the discovery to be enabled<br>_Compute Engine ID property is required_
**gce_resolve.py**
* Start the Compute Engine instance
**gce_start.py**
* Stop the Compute Engine instance
**gce_stop.py**
* Test authentication to Google Cloud
**gce_test.py**

## Notes
