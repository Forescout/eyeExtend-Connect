Forescout eyeExtend Connect NETSKOPE APP README.md


## Contact Information

- Have feedback or questions? Write to us at

        **[connect-app-help@forescout.com](mailto:connect-app-help@forescout.com)**

## APP Support

- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.

## About Netskope app

Version 1 of Forescout Connect app for Netskope. https://www.netskope.com/

## What does it do:
 
In its current state we use the Netskope API (version 1) to query client information from ‘api/v1/clients. This allows for additional discovery of properties that an be used to discover devices not on the customer network, properties for compliance management such as NPA status, client status, version and more.
 
### Sample:

"attributes": {
    "_id": "[masked]",
    "client_version": "[masked]",
    "device_id": "[masked]",
    "host_info": {
        "device_make": "[masked]",
        "device_model": "[masked]",
        "hostname": "[masked]",
        "last_hostinfo_update_timestamp": "[masked]",
        "managementID": "[masked]",
        "migrated_revision": "[masked]",
        "nsdeviceuid": "[masked]",
        "old_nsdeviceuid": "[masked]",
        "os": "[masked]",
        "os_version": "[masked]",
        "serialNumber": "[masked]"
    },
    "last_event": {
        "actor": "[masked]",
        "event": "[masked]",
        "npa_status": "[masked]",
        "service_name": "[masked]",
        "status": "[masked]",
        "status_v2": "[masked]",
        "timestamp": "[masked]"
    },
    "last_event_service_name": "[masked]",
    "users": [
        {
            "_id": "[masked]",
            "device_classification_custom_status": "[masked]",
            "device_classification_status": "[masked]",
            "last_event": {
                "actor": "[masked]",
                "event": "[masked]",
                "npa_status": "[masked]",
                "service_name": "[masked]",
                "status": "[masked]",
                "status_v2": "[masked]",
                "timestamp": "[masked]"
            },
            "user_added_time": "[masked]",
            "user_source": "[masked]",
            "user_state": "[masked]",
            "userkey": "[masked]",
            "username": "[masked]"
        }
    ]
}

 
## Properties

| Property| Comment|
| :------------------------------- | :-------------------------------- |
| URL          | *Netskope tenant URL i.e https://tenant.eu.goskope.com* |
| Token          | *Netskope API token |



## Whats next?
 
In the next release we are planning to add the functionality for syslog ingestion, as this will provide more near real time discovery of assets.
 
Prioritizing accessibility for all Netskope customers, we've opted to begin with the API integration. It's important to note that if syslog is utilized in a future release, additional on-premises infrastructure will be necessary but will also provide more real time ingestion
 
## Considerations:
 
- APIv1 is available to all Netskope customers currently, and should be used to generate a token for authentication against customer tenant. 
- In order for the API to work it is important to note that the latest version of the client needs to be used (over version 111.1.0.1994) as this supports polling IP address information

