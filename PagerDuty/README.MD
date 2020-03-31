# PagerDuty 1.0.0
eyeExtend Connect App for PagerDuty enables incidents to be created as an action from Forescout.

## Configuration
App configuration requires the following paramters:
* __PagerDuty URL__ : PagerDuty instance URL to identify the configuraiton instance of the App. 
  * Required: Yes
* __PagerDuty Admin User__ : PagerDuty Admin user email address that has the privledges to create incidents. Note that new cases
created by the App will list this user as the author.
  * Required: Yes
* __PagerDuty Service ID__ : Incidents have to be associated with a particular PagerDuty service. Input the Service ID
  * Required: Yes
* __PagerDuty Instance API Key__: The API key created with the PagerDuty instnace
  * Required: Yes

## Supported Use Cases

### Actions
* __Create PagerDuty Incident__
The App creates a new action under the 'Notification' group to create PagerDuty incidents. With the following paramters
  * _Incident Urgency_: Low or High
  * _Incident Title_: Incident Title string
  * _Incident Details_: Incident content as a multi-line string
