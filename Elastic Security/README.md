## About the eyeExtend Connect Elastic Security App
This app queries the Elastic Security APIs to discover endpoints with Elastic Agent + Defend deployed to  it. The app performd discovery and will create new hosts if not already found in Forescout, otherwise it will add the details to the existing host record.

The app also allows you to leverage the Elastic Defend Isolate action to restrict a host's access if Network Controls fail. It also allows a case to be created in Elastic Security when the Isolate action is performed.

## Requirements
The App has been (mostly) validated using:
- Elastic Stack v8.14.1
- Service Account (Username & Password) in Elastic for Connect App
	- Pure API key based authentication is not yet implemented
- Forescout CounterACT 8.5.1
- Forescout Connect Plugin v2.0.1
- Elastic Defend deployed (Defend is required to be deployed in addition to the agent for the Elastic Security API to return hosts)

The app should work using other versions of Elastic and Forescout, but your mileage may vary.

## Notes
### Timeout
Currently no significant benchmark testing has been completed to determine how long the Agent Discovery script takes. You may need to adjust the timeout of Connect to account for this. Discovery is required for app function.

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

## Configuration
#### Elastic Security Connection
- Kibana URL
	- Must include protocol (`http` or `https`)
	- Optional to include port (if running differently than standard http/https)
	- Do not include trailing `/`
	- Example: `https://elastic.lab.local:5601`
- Kibana Username & Password
	- Username and Password to authenticate with. Must be a user in Elastic.
- Ignore Last Check-in Older Than (Minutes)
	- Will ignore the host in discovery if the last check in time of the agent is greater than the specified amount in minutes.
	- Prevents a host from continuously being marked online in Forescout if the host is actually offline and not communicating to Elastic
- Discovery API Records per Page
	- Allows you to tune how many records are requested on each API query to Elastic Security. Larger values may impact Elastic performance, while smaller values request more pages of API requests and will take longer. Tune as needed.
- Ignore IP Ranges
	- It was observed that the Elastic Agent will report IPs from a host from all interfaces. On hosts running Docker (or perhaps even the way Elastic Isolates hosts), bogus hosts were being created.
	- IP Address in the ranges specified will be ignored during discovery.
	- Enter a Comma separated list of IP ranges in CIDR notation to ignore when discovered in Elastic Agent API; for example Docker internal ranges which end up in Elastic.
- Certificate Validation
	- If Forescout should reject HTTPS requests to Elastic server if server certificate is untrusted.

#### Assign Forescout Devices
It is recommended to run the integration on a focal appliance, not the Enterprise Manager.

#### Proxy Server
If the app should connect to Elastic through a Proxy.

#### Elastic Security Options
- Enable Host Discovery
	- Enable discovery; app will not function without Discovery enabled
- Discovery Frequency
	- How often to refresh discovery. Recommended every 60 minutes to fit in line with Forescout default inactivity timer settings.
- Number of API queries per second
	- Recommended to start slow and increase as needed. Will affect how long it takes to discover all thin clients on a connection.

### Test button
- Test is enabled by default.
- Connection Information (System Descriptions) need to be saved (applied) before test can be successfully run.

## Policy Templates
Several Policy templates are included.
- Elastic Agent ID Check
	- For all IPv4, has an Elastic Agent ID been found?
	- Useful to validate if a host is enrolled in Elastic Security.
	- Required for most other policies; Adds devices to the group `Has Agent ID`
- Elastic Agent Check-in Time
	- For all *online* IPv4 that has an Elastic Agent ID, has the agent checked in within the last Day?
	- Useful to validate if the Elastic Agent is healthy.
- Possible Internal Networking IP from Elastic Agent Discovery
	- For all IPv4 that has an Elastic Agent ID and the host has multiple IPs reported by Elastic, this policy attempts to highlight duplicate or bogus hosts (perhaps from an internal Docker IP range on the host, other tool, or otherwise) where the IP range may need to be set as an Ignore Range in the app settings or the host deleted.
	- Adjust this policy to use values on the host to see if it has other data from another part of Forescout, or if it is just a bogus Endpoint that needs to be ignored/deleted.
- Elastic Agent Metadata Reclassification
	- For all *online* IPv4 that has an Elastic Agent ID, leverages the Elastic Agent Host Metadata information to reclassify devices in Forescout.
	- Since the Elastic Agent is present on the device and gathers detailed information, it can be an authoritative source for host information if Forescout's classification of the device is weak (for lack of management, access, or other reasons).
	- The policy breaks out some basic groups for Windows, Linux, and macOS as a template with a (disabled) Set OS Classification action applied. Adjust for your environment and other host types that have Elastic in your environment.
	- You may also wish to add additional actions such as "Set Function Classification", "Set Network Function", or "Set Vendor and Model Classification".
	- Remember when using the "Set ..." actions, the reclassification no longer applies if the host is removed from the subrule where the action is placed and the value will return to the original Forescout value.
- Elastic Defend Deployment Status
	- For all IPv4, highlights the status of the Elastic Defend deployment.
	- Which hosts are managed by Elastic but Not Forescout (meaning Forescout cannot due the extended validation checks)
	- Not Elastic Agent/Defend Compatible (adjust as needed)
	- Compliant: Installed, Running, and Communicating to Elastic; Hosts that have the `elastic-endpoint` binary running and have an Agent ID.
	- Not Compliant: Installed and Running BUT not Communicating; Hosts that have the `elastic-endpoint` binary running but don't have an Agent ID. May indicate a broken connection. You can run the uninstall script on the endpoint to remove the agent and then re-install (install when missing handled by another subrule in this policy)
	- Not Compliant: Agent Only Installed;  Hosts that only have the `elastic-agent` binary running but not `elastic-endpoint`. May indicate a broken connection or it is not enrolled in the correct policy in Elastic.
	- Not Compliant: Install Agent; Indicates elastic-agent isn't present on the host. Attempt to run a script (see Handy Scripts section below) to install Elastic on the host to remediate.
- Elastic Defend Isolated Hosts
	- For all IPv4 that has an Elastic Agent ID, highlights hosts that are Isolated (according to Elastic API discovery), or where an Isolation has been requested by Forescout.


## Handy Scripts
### Install Elastic Agent (from Elastic.co), Windows, PowerShell
The following script will download v8.14.1 Agent, extract, and install/enroll it, and delete the install files. Adjust the `<ENROLLMENT TOKEN>` and `<FLEET IP>:<FLEET PORT>` as needed. You can also adjust the `elasticZipFilename ` variable to download a different version. Also note the `--insecure` flag is also included. It is not recommended to have this flag in production.

    # Install_Elastic_Agent.ps1
    $ProgressPreference = 'SilentlyContinue'
    $elasticZipFilename = "elastic-agent-8.14.1-windows-x86_64.zip"
    $elasticFolderFilename = $elasticZipFilename.Substring(0, $elasticZipFilename.Length-4)
    Invoke-WebRequest -Uri "https://artifacts.elastic.co/downloads/beats/elastic-agent/$elasticZipFilename" -OutFile $elasticZipFilename
    Expand-Archive .\$elasticZipFilename -DestinationPath .
    .\$elasticFolderFilename\elastic-agent.exe install --url=https://<FLEET IP>:<FLEET PORT:8220> --enrollment-token=<ENROLLMENT TOKEN> --insecure --non-interactive
    Remove-Item -Path .\$elasticZipFilename -Force -Recurse
    Remove-Item -Path .\$elasticFolderFilename -Force -Recurse

To run this via the Forescout "Run Script on Windows" command, you may need to convert it to a PowerShell "one-liner" so it can run via Forescout. "Convert PS1 to BAT.ps1" is included to help with this process. Simply run the Script -- it will first ask for an input .ps1 file (the saved version of above), then will ask where to save a BAT file. This BAT file can then be uploaded into the Forescout Script Repository to run as an action.

### Uninstall Elastic Agent, Windows
The following will [uninstall Elastic](https://www.elastic.co/guide/en/fleet/current/uninstall-elastic-agent.html) from Windows provided there's not an [uninstall token set](https://www.elastic.co/guide/en/security/8.14/uninstall-agent.html). This can be run straight from the Forescout "Run Script on Windows" action.

    C:\"Program Files"\Elastic\Agent\elastic-agent.exe uninstall --force

## Properties
### Top Level Properties
| tag                                    | label                           | description                                                                           | type      | inventory | track_change | list |
| -------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------- | --------- | --------- | ------------ | ---- |
| connect_elasticsecurity_agent_id       | Elastic Agent ID                | Elastic Agent ID                                                                      | string    |           |              |      |
| connect_elasticsecurity_host_status    | Elastic Host Status             | Elastic Agent Host Status                                                             | string    | true      | true         |      |
| connect_elasticsecurity_last_checkin   | Elastic Agent Last Check-in     | Elastic Agent Last Check-in                                                           | date      |           |              |      |
| connect_elasticsecurity_ips            | Elastic Agent IPs               | Elastic Agent reported IP addresses; excluding loopback and ipv6 link local           | string    |           |              | true |
| connect_elasticsecurity_number_of_ips  | Elastic Agent Number of IPs     | Elastic Agent reported number of IP addresses; excluding loopback and ipv6 link local | integer   |           |              |      |
| connect_elasticsecurity_macs           | Elastic Agent MACs              | Elastic Agent reported MAC addresses                                                  | string    |           |              | true |
| connect_elasticsecurity_number_of_macs | Elastic Agent Number of MACs    | Elastic Agent reported number of MAC addresses                                        | integer   |           |              |      |
| connect_elasticsecurity_meta_host      | Elastic Agent Host Metadata     | Elastic Agent Host Metadata                                                           | composite | true      |              |      |
| connect_elasticsecurity_meta_endpoint  | Elastic Agent Endpoint Metadata | Elastic Agent Endpoint Metadata                                                       | composite | true      |              |      |
| connect_elasticsecurity_meta_agent     | Elastic Agent Agent Metadata    | Elastic Agent Agent Metadata                                                          | composite | true      |              |      |

### Composite Property: connect_elasticsecurity_meta_host
| tag          | label        | description  | type   | inventory |
| ------------ | ------------ | ------------ | ------ | --------- |
| hostname     | Hostname     | Hostname     | string | false     |
| os_variant   | OS Variant   | OS Variant   | string | true      |
| os_kernel    | OS Kernel    | OS Kernal    | string | true      |
| os_name      | OS Name      | OS Name      | string | true      |
| os_family    | OS Family    | OS Family    | string | true      |
| os_type      | OS Type      | OS Type      | string | true      |
| os_version   | OS Version   | OS Version   | string | true      |
| os_platform  | OS Platform  | OS Platform  | string | true      |
| os_full      | OS Full      | OS Full      | string | true      |
| architecture | Architecture | Architecture | string | true      |

### Composite Property: connect_elasticsecurity_meta_endpoint
| tag                            | label                                  | description                                    | list | overwrite | type    | inventory |
| ------------------------------ | -------------------------------------- | ---------------------------------------------- | ---- | --------- | ------- | --------- |
| capabilities                   | Capabilities                           | Capabilities                                   | true | true      | string  | true      |
| configuration_isolation        | Configuration:Isolation                | Configuration Isolation                        |      |           | boolean | true      |
| state_isolation                | State:Isolation                        | State Isolation                                |      |           | boolean | true      |
| policy_name                    | Elastic Defend Policy                  | Applied Elastic Defend Policy                  |      |           | string  | true      |
| policy_endpoint_policy_version | Elastic Defend Endpoint Policy Version | Applied Elastic Defend Endpoint Policy Version |      |           | string  | true      |
| policy_version                 | Elastic Defend Policy Version          | Applied Elastic Defend Policy Version          |      |           | string  | true      |
| policy_status                  | Elastic Defend Policy Status           | Applied Elastic Defend Policy Status           |      |           | string  | true      |
| status                         | Status                                 | Status                                         |      |           | string  | true      |


### Composite Property: connect_elasticsecurity_meta_agent
| tag     | label   | description   | type   | inventory |
| ------- | ------- | ------------- | ------ | --------- |
| build   | Build   | Agent Build   | string | true      |
| type    | Type    | Agent Type    | string | true      |
| version | Version | Agent Version | string | true      |

## Actions
- Isolate Host
    	- Calls the Elastic Security API to request the Host Isolate action be performed. It is recommended to make sure your Forescout Appliances are in Elastic Defend's "Host isolation exceptions" list so that Forescout may continue to inspect and have visibility of the endpoint during Isolation.
    	- This action will set the Forescout properties `connect_elasticsecurity_meta_endpoint.configuration_isolation` and `connect_elasticsecurity_meta_endpoint.state_isolation`) about the host to `true` if the Isolation API call is successful (in order to not have to wait for a new Discovery poll) and allow you to account for this state in Policy. 
    	- This action is cancellable and the endpoint will be released from isolation if it leaves the policy/subrule where the action is applied.
    	- Will create a case and link the Isolation action in Elastic Security if the "Create a case?" option is enabled.
    	- "Case: Sync alert status with case status?" will enable the sync alerts option on the case.
    	- Will enable logic to  automatically close the associated case with a Isolate action when the action is cancelled when "Auto close case?" is enabled.
    	- Note: Connect app restrictions require that text fields must have a value in order to save/run the action. The text "NONE" is reserved and will be treated as if it was left empty when entered in a field.

## Scripts
- `es_discovery.py`
	- Queries Elastic Security API to gather agent information.
	- Note that Discovery will filter Elastic Security API query with `hostStatuses=["healthy", "unhealthy", "updating"]`
	- **Important note**: The Elastic API returns all IP address and MAC addresses for a host, but has no correlation of which IP and MAC address belong together. The Discovery script will iterate through each IP provided by the Elastic API (ignoring any link local, IPv6, or addresses in the "Ignore IP Ranges" System Configuration) and create a host for each IP. If only 1 MAC address is returned in the API, each IP will be returned with the 0 index MAC address in the API response (if there are more than 1 MAC address provided, it will not be returned to Forescout and will rely on IP address mapping alone and hope Forescout figures it out).
- `es_test.py`
	- Performs a test to see if the Elastic Security API is working and returning results.
- `es_isolate.py`
	- [Isolates](https://www.elastic.co/guide/en/security/8.14/host-isolation-api.html) a host via Elastic Security; Optionally creates a Case if requested in the Action Parameters.
- `es_release.py`
	- Cancels the Isolate action and releases the endpoint. Will also close the case associated with the Isolate action if selected in the action options.

## Notes
- The timezone of the `Elastic Agent Last Check-in` property is not correctly parsed. Forescout appears to be reading this as the timezone  that the managing appliance is set for, however Elastic API returns as UTC and the script parses as such.