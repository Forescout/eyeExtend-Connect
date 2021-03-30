# Action API
This sample eyeExtend Connect App provides an example deployment for triggering an action via Connect Web API framework. Details can be found here [Connect Documentation](https://github.com/Forescout/eyeExtend-Connect/blob/master/eyeExtend%20Connect%20App%20Building%20Guide.pdf)

Minimum version of CounterACT 8.2.2
Minimum version of eyeExtend Connect Module 1.9.0
## App Deployment
 1. Install/Upgrade 8.2.2
 2. Install/Upgrade Connect Module 1.9.0
 3. Use the Connect Plugin to deploy the ActionAPI App. [ActionAPI.zip](https://github.com/Forescout/eyeExtend-Connect/blob/master/Connect-training-demo/ActionAPI/ActionAPI_v1.zip)

 - [ ] Enable unsigned App deployment mode to deploy this example app. See pg 92 of Connect documentation for details

		fstool allow_unsigned_connect_app_install true
 - [ ]  Provision the credential for the App (To be used for Token retrieval)
 - [ ] Provision the instance and the deployment appliance.
 - [ ] Apply the config
 4. After the App is successfully deployed deploy the Policy using the policy template provided with the app.
 - [ ] Policy Add will include list of Templates, select the 'Initiate assign to VLAN action' under the Connect Action API group
 - [ ]  Select the segment or IP ranges that apply to your use-case. If this function is required to cover all endpoint select All IPs as well as Unknown IPs to support MAC address only EPs
 - [ ] The default action is defined to trigger Assign VLAN action using the provided VLAN ID.
 - [ ] Complete the policy by applying the config

## APIs
You can access the API documentation for swagger interface of your CounterACT deployment using the following URL:

https://EM_HOST/connect/swagger-ui/index.html

where EM_IP is your  Enterprise Manager

### Token
curl example bellow to retrieve the token
Parameters:

 - username and password from step 3 above

curl -X POST "https://{em_host}/connect/v1/authentication/token" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"username\":\"test\", \"password\":\"test\", \"app_name\":\"actionapi\", \"expiration\":\"1500\"}"

Example Output:
{
  "status": "OK",
  "code": 200,
  "message": null,
  "data": {
    **"token": "XYZ",**
    "app_name": "actionapi",
    "expire_time": 1617209709619
  }
}
Leverage the token as a Bearer token for all subsequent queries
### Take Action API
curl example to post API call to trigger Assign to VLAN action using following paramters

 - Bearer Token
 - mac and/or ip of host
 - 'connect_actionapi_vlan_assign' - true to enable action; false to disable action
 - 'connect_actionapi_vlan_assign_id' - VLAN Name /ID to be assigned

#### Assign
curl -X POST "https://{em_host}/connect/v1/hosts" -H "accept: application/json" -H "Authorization: Bearer XYZ" -H "Content-Type: application/json" -d "{ \"mac\":\"e006e66ad0a6\", \"properties\":{ \"connect_actionapi_vlan_assign\":true, \"connect_actionapi_vlan_assign_id\":\"test\" }}"

#### Unassign

curl -X POST "https://{em_host}/connect/v1/hosts" -H "accept: application/json" -H "Authorization: Bearer XYZ" -H "Content-Type: application/json" -d "{ \"mac\":\"e006e66ad0a6\", \"properties\":{ \"connect_actionapi_vlan_assign\":false }}"
