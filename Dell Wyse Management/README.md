## About the eyeExtend Connect Dell Wyse Management Studio App
This app queries the Dell Wyse Management Studio API to discovery Thin Clients and information about the thin client. The app allows some interaction to be performed against the thin client endpoint via the Wyse API.

## Requirements
The App has been (mostly) validated using:
- Dell Wyse Management Suite 4.3.0
- Forescout CounterACT 8.4.3
- Forescout Connect Plugin v2.0.1
- [Enable Wyse API](https://developer.dell.com/apis/3788/versions/4.3.0/docs/Getting%20Started/1Prerequisites.md)

## Configuration
#### Dell Wyse Management Suite Connection
- URL to the Wyse Server
	- Must include protocol (http or https)
	- Optional to include port (if running differently than standard http/https)
	- Do not include trailing /
	- Default: https://wyse.domain.local:443
- Username & Password
	- Username and Password to authenticate against Wyse. Must be a user in Wyse.
- Certificate Validation
	- If Forescout should reject HTTPS requests to Wyse server if server certificate is untrusted.

#### Assign Forescout Devices
It is recommended to run the integration on a focal appliance, not the Enterprise Manager.

#### Proxy Server
If the app should connect to Wyse through a Proxy.

#### Dell Wyse Management Suite Options
- Authentication token refresh interface
	- Defaults to 10 minutes
	- May cause error if not frequent enough
	- Wyse defaults to 10-20 min session validity
- Discovery
	- Enable discovery; app will not function without Discovery enabled
- Discovery Frequency
	- How often to refresh discovery. Recommneded every 60 minutes to fit in line with Forescout default inactivity timer settings
- Number of API queries per second
	- Recommended to start slow and increase as needed. Will affect how long it takes to discover all thin clients on a connection.

### Test button
- Test is enabled by default.
- Connection Information (System Descriptions) need to be saved (applied) before test can be successfully run.

## Policy Templates
Several Policy templates are included.
- Dell Wyse Management Suite Discovery
	- Add this first! Use this policy template to detect group all devices found by Dell Wyse Management Suite Connect App. All other policies leverage the group this adds devices to.
- Dell Wyse Management Suite Classification
	- Example Policy to use properties from Wyse Management Suite to re-classify devices. Expand subrules and actions as needed to match your environment.
- Dell Wyse Management Suite Discovery and Reclassification
	- Alternative to "Dell Wyse Management Suite Discovery" and "Dell Wyse Management Suite Classification", combing both policies and including some extra (native to Forescout) actions to reclassify thin clients using the native Forescout actions so that the Function, OS, and Vendor fields are more accurate.
- Dell Wyse Management Suite Serial Number
	- Highlights the device serial number for devices and adds devices to the "C2C-2.1.2 Network Device Serial Number Found Compliant" which is used in C2C Reporting for DoD.
- Extended Device Information and Online Sync
	- Policy to resolved extended device details from Dell Wyse Management Suite. WARNING: Causes an API query per host which can impact performance. NOTE: Dependent on discovering Dell Wyse Management Suite device ID from discovery service.

## Properties

    {
          "tag": "connect_dellwysemanagementsuite_id",
          "group": "connect_dellwysemanagementsuite_group",
          "label": "Dell Wyse Management Suite Device ID",
          "description": "ID from Wyse Management Suite",
          "type": "string"
        },
        {
          "tag": "connect_dellwysemanagementsuite_last_seen_in_api",
          "group": "connect_dellwysemanagementsuite_group",
          "label": "Dell Wyse Management Suite Last Updated/Seen in Discovery API Poll",
          "description": "Last Updated/Seen Time from Wyse Management Suite API in Discovery poll",
          "type": "date"
        },
        {
          "tag": "connect_dellwysemanagementsuite_device_details",
          "group": "connect_dellwysemanagementsuite_group",
          "label": "Dell Wyse Management Suite Device Details (Basic)",
          "description": "Device Details from Dell Wyse Management Suite Discovery API Poll",
          "type": "composite",
          "inventory": {
        	"enable": true,
        	"description": "Invetory of Dell Wyse Management Suite Device Details"
          },
          "subfields": [
        	{
        	  "tag": "platform_type",
        	  "label": "Platform Type",
        	  "description": "Platform Type",
        	  "type": "string",
        	  "inventory": true
        	},
        	{
        	  "tag": "system_name",
        	  "label": "System Name",
        	  "description": "System Name",
        	  "type": "string",
        	  "inventory": false
        	},
        	{
        	  "tag": "compliance",
        	  "label": "Compliance",
        	  "description": "Compliance according to Wyse Management Suite",
        	  "type": "boolean",
        	  "inventory": true
        	},
        	{
        	  "tag": "type",
        	  "label": "Type",
        	  "description": "Type",
        	  "type": "string",
        	  "inventory": true
        	},
        	{
        	  "tag": "os_version",
        	  "label": "OS Version",
        	  "description": "OS Version",
        	  "type": "string",
        	  "inventory": true
        	},
        	{
        	  "tag": "serial",
        	  "label": "Serial",
        	  "description": "Serial",
        	  "type": "string",
        	  "inventory": false
        	},
        	{
        	  "tag": "last_user",
        	  "label": "Last User",
        	  "description": "Last User",
        	  "type": "string",
        	  "inventory": false
        	},
        	{
        	  "tag": "group",
        	  "label": "Group",
        	  "description": "Group",
        	  "type": "string",
        	  "inventory": true
        	},
        	{
        	  "tag": "last_checkin_date",
        	  "label": "Last Checkin Date",
        	  "description": "Last Checkin Date (Day precision )",
        	  "type": "date",
        	  "inventory": false
        	}
          ]
        },
        {
          "tag": "connect_dellwysemanagementsuite_device_details_extended",
          "group": "connect_dellwysemanagementsuite_group",
          "label": "Dell Wyse Management Suite Device Details (Extended)",
          "description": "Extended Device Details from Dell Wyse Management Suite. WARNING: Causes an API query per host which can impact performance. NOTE: Dependant on discovering Dell Wyse Management Suite device ID from discovery service.",
          "type": "composite",
          "inventory": {
        	"enable": true,
        	"description": "Invetory of Dell Wyse Management Suite Device Details (Extended)"
          },
          "dependencies": [
        	{
        	  "name": "connect_dellwysemanagementsuite_id",
        	  "redo_new": false,
        	  "redo_change": false
        	}
          ],
          "subfields": [
        	{
        	  "tag": "power_state",
        	  "label": "Power State",
        	  "description": "The current power state of the system according to Dell Wyse Management Suite",
        	  "type": "string",
        	  "inventory": true
        	},
        	{
        	  "tag": "name",
        	  "label": "Name",
        	  "description": "Device name as displayed in device summary section in Dell Wyse Management Suite",
        	  "type": "string",
        	  "inventory": false
        	},
        	{
        	  "tag": "manufacturer",
        	  "label": "Manufacturer",
        	  "description": "The manufacturer or OEM of this system in Dell Wyse Management Suite",
        	  "type": "string",
        	  "inventory": true
        	},
        	{
        	  "tag": "id",
        	  "label": "Id",
        	  "description": "The identifier that uniquely identifies the resource within the collection of similar resources in Dell Wyse Management Suite.",
        	  "type": "string",
        	  "inventory": false
        	},
        	{
        	  "tag": "description",
        	  "label": "Description",
        	  "description": "The description of this resource. Used for commonality in the schema definitions in Dell Wyse Management Suite.",
        	  "type": "string",
        	  "inventory": false
        	},
        	{
        	  "tag": "bios_version",
        	  "label": "BIOS Version",
        	  "description": "The version of the system BIOS or primary system firmware according to Dell Wyse Managmeent Suite.",
        	  "type": "string",
        	  "inventory": true
        	}
          ]
        },
        {
          "tag": "connect_dellwysemanagementsuite_device_details_extended_status",
          "group": "connect_dellwysemanagementsuite_group",
          "label": "Dell Wyse Management Suite Device Details Status (Extended)",
          "description": "Extended Device Details Status from Dell Wyse Management Suite. WARNING: Causes an API query per host which can impact performance. NOTE: Dependant on discovering Dell Wyse Management Suite device ID from discovery service.",
          "type": "composite",
          "inventory": {
        	"enable": true,
        	"description": "Invetory of Dell Wyse Management Suite Device Details Status (Extended)"
          },
          "dependencies": [
        	{
        	  "name": "connect_dellwysemanagementsuite_id",
        	  "redo_new": false,
        	  "redo_change": false
        	}
          ],
          "subfields": [
        	{
        	  "tag": "health",
        	  "label": "Health",
        	  "description": "The health state of this resource in the absence of its dependent resources in Dell Wyse Management Suite",
        	  "type": "string",
        	  "inventory": true
        	},
        	{
        	  "tag": "health_rollup",
        	  "label": "Health Rollup",
        	  "description": "The overall health state from the view of this resource in Dell Wyse Management Suite",
        	  "type": "string",
        	  "inventory": true
        	},
        	{
        	  "tag": "state",
        	  "label": "State",
        	  "description": "The known state of the resource, such as, enabled in Dell Wyse Management Suite.",
        	  "type": "string",
        	  "inventory": true
        	}
          ]
        }
    
## Actions
- Change Group
    	- Calls the Wyse API to change the device group. This actiona is cancellable and will revert to the original group when the device no longer meets the policy/sub-rule where the action is applied.
    	- **Note**: This API is not yet validated to function and is purely made based on the API documentation.
- Shutdown
	- Calls the Wyse API to request that the thin client shutdown.
	- **Note**: This API is not yet validated to function and is purely made based on the API documentation.
- Send Message
	- Calls the Wyse API to request that the thin client show a message.
	- **Note**: This API is not yet validated to function and is purely made based on the API documentation.

## Scripts
- `wyse_authorization.py`
	- Gets X-Auth-Token from Wyse API using the username and password. Required for all other scripts and API calls. [Wyse Documentation says sessions are valid for 10-20 minutes](https://developer.dell.com/apis/3788/versions/4.3.0/docs/Getting%20Started/3authentication.md). Refresh interval for token may need to be adjusted in the settings. Default is 10 minutes.
- `wyse_discovery.py`
	- Queries Wyse API to gather registered clients. Defaults to discovery every hour. Discovery is required for function of app. Note that Discovery will filter Wyse API query with Status=='Online'.
- `wyse_test.py`
	- Performs a test to see if the Wyse API is working and returning results.
- `wyse_extended_query.py`
	- [Attempts to get extra information](https://developer.dell.com/apis/3788/versions/4.3.0/docs/Tasks/3get_device_details.md) about a thin client from the Wyse API. Requires that discovery be performed first to get the Client ID of the thin client. Not recommended for extensive use as it performs an API query per endpoint.
- `wyse_change_group.py`
	- [Untested] [Changes group](https://developer.dell.com/apis/3788/versions/4.3.0/docs/Tasks/8.0change_device_group.md) of a thin client in Wyse.
- `wyse_undo_change_group.py`
	- [Untested] Restore group of a thing client in Wyse after the change group action.
- `wyse_send_message.py`
	- [Untested] [Sends a message](https://developer.dell.com/apis/3788/versions/4.3.0/docs/Tasks/8.5sendmessagedevice.md) to the thin client itself.
- `wyse_shutdown.py`
	- [Untested] [Shuts down](https://developer.dell.com/apis/3788/versions/4.3.0/docs/Tasks/8.3shutdown.md) the thin client.


## Notes

### Client Certificate required by Wyse
The following error has been observed in deployments when performing a test of the App. This likely indicate a Client Certificate is required (but not 100% validated), but the app currently is not created to support presenting a Client Certificate. With Connect 2, presenting a client certificate is support, but simply not implemented in this app.

    {"code":"Base.1.0.GeneralError","message":"A general error has occurred. See Resolution for information on how to resolve the error.","@Message.ExtendedInfo":[{"@odata.type":"#Message.v1_0_9.Message","MessageId":"Base.1.0.InternalError","Message":"Server is not able to serve the request.","MessageArgs":["org.springframework.web.reactive.function.client.WebClientRequestException: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target; nested exception is javax.net.ssl.SSLHandshakeException: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target"],"RelatedProperties":["#/Sessions"],"Resolution":"Please contact Dell Inc. support.","Severity":"Warning"}]}

### Timeout
2,600 Thin Clients took > 2 minutes to retrieve from Wyse API in the Discovery script. You may need to adjust the timeout of Connect to account for this. 

[Documentation Page](https://docs.forescout.com/bundle/eye-connect-2-0-1-rn/page/eye-connect-2-0-1-rn.eyeExtend-Connect-Module-2.0.1_3a-Connect-Plugin-1.html)
> The Connect Plugin uses a socket connection to run Python scripts. There are two timeout settings: socket connection timeout and socket read timeout. Both can now be configured.
> 
> In prior versions, the socket connection timeout was 20 seconds, which meant that if the socket connection was not established within 20 seconds, it timed out. The socket read timeout was 2 minutes, which meant that if a Python script did not return a response within 2 minutes, it timed out.
> 
> To change the socket connection timeout value, run the following command on all the connecting appliances:
> 
> `fstool connect_module set_property connect.python.socket.connect.timeout.seconds <number of seconds>`
> 
> To change the socket read timeout value, run the following command on all the connecting appliances:
> 
> `fstool connect_module set_property connect.python.socket.read.timeout.seconds <number of seconds>`
> 
> The <number of seconds> must be a positive integer. The default for the socket connection timeout is 20 seconds, the default for the socket read timeout is 120 seconds. There is no maximum value.