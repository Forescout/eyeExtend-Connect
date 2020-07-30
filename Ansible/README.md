Forescout eyeExtend Connect for Ansible README.md
 
## Contact Information
Forescout Technologies, Inc.
190 West Tasman Drive
San Jose, CA 95134 USA
https://www.Forescout.com/support/
Toll-Free (US): 1.866.377.8771
Tel (Intl): 1.408.213.3191
Support: 1.708.237.6591

## About the Documentation
- Refer to the Technical Documentation page on the Forescout website for additional documentation:
https://www.Forescout.com/company/technical-documentation/
- Have feedback or questions? Write to us at documentation@forescout.com

## Legal Notice
© 2020 Forescout Technologies, Inc. All rights reserved. Forescout Technologies, Inc. is a Delaware corporation.
A list of our trademarks and patents can be found at https://www.Forescout.com/company/legal/intellectual-property-patents-trademarks.
	Other brands, products, or service names may be trademarks or service marks of their respective owners.

## About the eyeExtend Connect Ansible App
The App brings the power of Ansible to the Forescout eyeSight Platform.  

Ansible playbooks can be created using [available modules](https://docs.ansible.com/ansible/latest/modules/modules_by_category.html) and then configured as [job templates](https://docs.ansible.com/ansible-tower/latest/html/userguide/job_templates.html) on Ansible Tower.  This exposes the playbook functionality via the Tower REST API which is called by the Connect App.

Extra Variables (`extra_vars`) can be passed to the Tower REST API from the App to override those specified in the Tower job template.

Access to run the Tower jobs (ansible playbooks) is controlled by the credentialing of the Tower username/password on the App.


## Requirements

This App was tested with:

* Ansible 2.7.1
* Ansible Tower 3.2.5


## Actions
There is currently a single action to launch the Ansible Tower job.  The user must specify the `Tower Template ID`, and the `extra_vars` expressed as **keyword=value** pairs, one per line.  

For example:

```
vmvcname={vmware_vm_name}
vmcvlan=1000
```
** Note that eyeSight TAGS may be used when specificying the `extra_vars`. In the above example, `vmware_vm_name` will resolve to the vmware name of the endpoint that the action is being taken against.



## Licenses
This App bundles with a license.txt file. Please review the license.txt file.
