Forescout

eyeExtend for AzureAD App README.md Version 1.0.0

Retrieve the eca file from <https://github.com/Forescout/eyeExtend-Connect/tree/master/AzureAD>
# **Contact Information**
- Have feedback or questions? Write to us at [**connect-app-help@forescout.com**](mailto:connect-app-help@forescout.com)
# **APP Support**
- All eyeExtend Connect Apps posted here are community contributed and community supported. These Apps are not supported by the Forescout Customer Support team.
- See Contact Information above.
# **About the AzureAD App**
## Use Cases
The AzureAD App is designed to utilize Microsoft Graph API to function similarly to an LDAP query with traditional Active Directory. The application performs API queries based on the User Principle Name to return user attributes and group attributes. 

Details on the AzureAD User Principle Name can be found here: <https://learn.microsoft.com/en-us/azure/active-directory/hybrid/plan-connect-userprincipalname>

The App returns the following properties based on these queries:

- ID
- Business Phone
- Display Name
- Given Name
- Job Title
- Mail
- Mobile Phone
- Office Location
- Preferred Language
- Surname
- User Principle Name
## How It Works
The following Intune components are required for this integrated solution:

- **Microsoft Graph API:** The Forescout platform addresses the API exposed by the platform to retrieve endpoint information and perform actions.

The following Forescout platform components support the integration:

- **Forescout eyeExtend Connect Plugin:** An infrastructure for integrating third-party vendors with the Forescout platform.
- **Forescout eyeExtend AzureAD App:** The Connect App developed by Forescout to implement the integration with Intune.

In a typical deployment, several cloud connections are defined in the Forescout platform. Connections to the cloud may be planned based on anticipated traffic or geographic location. The deployment is as follows:

- A single CounterACT® device connects to each cloud access point, handling communication for a cluster of CounterACT devices. The CounterACT devices in the cluster only work with that Intune cloud instance.
- For each connection, the rate limiting of messaging from the Forescout platform to the Intune cloud can be configured.
# **What to Do**
To set up your system for integration with eyeExtend Connect App for AzureAD, perform the following steps:

1. Verify that the requirements are met. See Requirements.
1. Download and install the module. See How to Install.
1. Configure the module. See Configure the Module.
## Requirements
- Forescout version 8.1.4, 8.2.2.x, 8.3, 8.4.x
- Forescout Connect Module
- Forescout eyeExtend Connect App for Microsoft AzureAD requires the following: 
  - An Azure online account for you to log in to <https://portal.azure.com/>.
  - For information about the vendor models (hardware/software) and versions (product/OS) that are validated for integration with this Forescout component, refer to the Forescout Compatibility Matrix.

Note the connect App for Microsoft AzureAD requires access to the following public URLs. You can whitelist them to allow access.

- <https://login.microsoftonline.com/>
- <https://graph.microsoft.com/>

The API permissions have a specific type

- GRAPH API, type equals *application*.
- ACTIONS, type equals *delegated*. **See section AzureAD Permissions**
# **How to Install**
Get Forescout eyeExtend Connect plugin and Azure AD App from Forescout.

Install the eyeExtend Connect Plugin: <https://docs.forescout.com/bundle/connect-module-1-9-rn/page/connect-module-1-9-rn.Install-the-eyeExtend-Connect-Module.html>

After installing the Connect plugin, ensure that it is running.

To verify:

- Select **Tools** > **Options** > **Modules**.
- Navigate to the component and hover over the name to view a tooltip indicating if it is running on Forescout devices in your deployment. In addition, next to the component name, you will see one of the following icons:
  - The component is stopped on all Forescout devices.
  - The component is stopped on some Forescout devices.
  - The component is running on all Forescout devices.
- If the component is not running, select **Start** , and then select the relevant Forescout devices.
- Select **OK**.
## Create User and Application in AzureAD
On Azure Active Directory (AAD), you need to: 

- Create a user account and assign it a role.
- Create an application and assign it an owner.

Before the Forescout platform can authenticate against an AzureAD account via the service principal (the application), you need to perform the following procedures to register an application and service principal on AAD, as well as ensure that you have the required role, permissions, and owner.
You can obtain the Directory (Tenant) ID and Application (Client) ID from the Azure portal.
### **Create a New User**
Go to <https://portal.azure.com/> and log in to your account. Select **Azure Active Directory > Users >** *create* **New User**

Fill out the form with the appropriate information. Assign* user account Appropriate **Role**.

`	`**Note:** A service account may be best for API connections rather than a user account.
### **Create a New Application and Configure**
Navigate to **Azure Active Directory** > **App registrations** > **New registration**

Name the new application

Change platform to **Web**

Leave the URL alone for now

![](README.assets/Aspose.Words.d76a5564-34b7-42a9-a7a8-b1d848e46985.001.png)

Select **Register**

Navigate* to **API permissions** within the APP you just registered

**User.read** Should appear as a default. This permission allows the API to sign in and read user profiles. 

Add* below graph API permissions:

- **Directory.Read.All**
- **Group.Read.All**
- **User.Read.All**

![](README.assets/Aspose.Words.d76a5564-34b7-42a9-a7a8-b1d848e46985.002.png)

Navigate to **Owners.** Add* the new user you just created by selecting **Add owners.** Select the new user and hit **Select**.

Now, you will need to obtain the **tenant ID, application ID, and client secret**

- **Note:** application ID can also be referred to as the **Client ID.** Tenant ID can also be referred to as the **Directory ID**

This information can be found In the **Overview** page of the newly registered application

Navigate to **Authentication**. Add Redirect URI [**https://example**](https://example)

Add Front-channel Logout URI [**https://example**](https://example)

- **Note:** you can add the API name for both Redirect URI and Front-channel logout URI. Both have to be the same

Checkmark* **Access tokens**

![](README.assets/Aspose.Words.d76a5564-34b7-42a9-a7a8-b1d848e46985.003.png)
## Configure Azure App in the Forescout Console
Retrieve and Install an eyeExtend Connect App: <https://docs.forescout.com/bundle/connect-1-7-h/page/c-deploy-an-app-with.html>

Navigate to **Tools > options > Connect.** Import* the **AzureAD** **application** file.

`	`This is the **eca file** you downloaded from Github. 
### **Configure Azure AD Connection**
Add Azure account **Tenant ID.**

Input **Tenant ID, Client ID, and Client Secret Value** in appropriate fields.

**Authorization Interval** can be left as default.

![](README.assets/Aspose.Words.d76a5564-34b7-42a9-a7a8-b1d848e46985.004.png)
### **Assign CounterAct Devices**
Select the appliance that should be the focal appliance for these API calls to AzureAD.
### **Configure Proxy Server**
If using a Proxy server, Enter appropriate information. Proxy Server is not needed for this. 
### **Configure AzureAD Options**
Assign **Test User.** This user will be used when running the test to verify that the configuration and connectivity is correct. The test will send a query using this user name. 

![](README.assets/Aspose.Words.d76a5564-34b7-42a9-a7a8-b1d848e46985.005.png)

Select* **Finish.**

AzureAD Connecter should now appear

![](README.assets/Aspose.Words.d76a5564-34b7-42a9-a7a8-b1d848e46985.006.png)

**Apply** changes. Select **Yes** when asked to save the connect plugin configuration

Reopen* **AzureAD** module

Select **Refresh** and checkmark* **Authorization Token**

Select* **Ok**

- **Note:** this manually retrieves the authorization token instead of waiting for the default authorization interval

![](README.assets/Aspose.Words.d76a5564-34b7-42a9-a7a8-b1d848e46985.007.png)

**Test** the API connection

![](README.assets/Aspose.Words.d76a5564-34b7-42a9-a7a8-b1d848e46985.008.png)

