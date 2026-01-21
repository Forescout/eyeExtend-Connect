## About the eyeExtend Connect Elastic App

The eyeExtend Connect Elastic App is an integration tool designed to seamlessly connect Forescout data with Elastic, enhancing your organization's data management and security capabilities. This app allows you to efficiently push endpoint data from Forescout into Elastic, enabling comprehensive visibility and analysis within your Elastic environment.

## Requirements
The App has been primarily validated using:
- Elastic Stack v9.2.3
- Forescout CounterACT 8.5.2

While it may work with other versions of Elastic and Forescout, these are the versions it has been tested on.

## Configuration
#### Elastic Connection
- Elastic URL
	- Must include protocol (`http` or `https`)
	- Including a port is optional unless it deviates from standard HTTP/HTTPS
	- Do not include trailing `/`
	- Example: `https://elastic.lab.local:5601`
- Elastic Username & Password
	- Username and Password to authenticate with. Must be a user in Elastic.
- Certificate Validation
	- If Forescout should reject HTTPS requests to Elastic server if server certificate is untrusted.
### Elastic Target
- Elastic Datastream
	- Elastic datastream where you want to push data.

#### Assign Forescout Devices
It is recommended to run the integration on a focal appliance, not the Enterprise Manager.

#### Proxy Server
If the app should connect to Elastic through a Proxy.

### Test button
- Test is enabled by default.
- Connection Information (System Descriptions) needs to be saved (applied) before test can be successfully run.

## Policy Templates
- Elastic Push
    - Follow the instructions in doc to configure the policy template. [Policy Template](https://docs.forescout.com/bundle/connect-2-0-0-h/page/t-configure-policy-templates-in.html)
	- The policy template uses two conditions:
		- `host is online`
		- `host is offline`
	- Only one of them needs to be true which means the policy will always fetch the endpoints from forescout.
	- User can modify the conditions by adding and removing conditions during configuration of the policy.
	- The policy uses Elastic Push Data action to push the data to Elastic.
	- Modify the log format of action for retriving various properties tags from forescout.
	- By default, the condition is checked every 8 hours, and any changes are pushed to Elastic.
	  
## Actions
- Elastic Push Data
    - Pushes the Forescout endpoint data to Elastic.
	- Has two parameters:
		- `Elastic Push Policy` (required): Specifies the policy name to differentiate between policy-driven and manual actions.
		- `Log Format` (required): Defines the log format to use, such as {dot1x_NAS_addr6}|{dot1x_acct_sid}. Property tags should be separated by `|`.
	- Manual action will run once but using the schedule option it can be configured to run every few hours based on time specified.

## Scripts
- `elastic_push.py`
	- Pushes the Forescout endpoint data to Elastic.
- `elastic_test.py`
	- Performs a test to see if the Elastic API is working and returning results.
