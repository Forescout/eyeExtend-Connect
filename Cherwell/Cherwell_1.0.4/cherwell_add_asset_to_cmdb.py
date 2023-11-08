"""
Copyright © 2020 Forescout Technologies, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import urllib.request

# Extract the token
bearer_token = params["connect_authorization_token"]

# Setup list of tables we are going iterate through
readtables = ["connect_cherwell_fs_staging_table"]

# API URL
url_call = params["connect_cherwell_base_url"]
url_path = "/api/V1/getbusinessobjectsummary/busobname/"

# URL Header Type Information
url_content_type = params["connect_cherwell_content_type"]
url_accept_type = params["connect_cherwell_accept_type"]

# -------------------------------------------------------------------------------------------------

# Setup the header information to information from Cherwell
header_info = {
    'Content-Type': url_content_type,
    'Accept': url_accept_type,
    'Authorization': 'Bearer ' + bearer_token
}

# initialize the payload variable and variables that are used to store
# the object info for the tables we are going to reference
payload_data = ''

fsimporttable_busObjID = ''
fsimporttable_Name = ''

# ----- Process table information
for x in readtables:
    # Grab the table name based on the parameter
    tablename = params[x]

    # Build the entire url
    target_url = url_call + url_path + tablename

    # Issue the REST API call and retrieve the information
    request_response = urllib.request.Request(target_url, headers=header_info,
                                              data=bytes(payload_data, encoding="utf-8"), method='GET')
    resp = urllib.request.urlopen(request_response, context=ssl_context)

    # Read the json responses
    request_response = json.loads(resp.read())

    # Process the output based on which paramter is being pulled back
    # Extract the ObjID and the Display Name
    fsimporttable_busObjID = request_response[0]['busObId']
    fsimporttable_Name = request_response[0]['name']

# Server URL update needed to grab the objects schema id
# this is required to build the payload for the submission
# of data as the busObj name and ID are required to process
url_path = "/api/V1/getbusinessobjectschema/busobid/" + fsimporttable_busObjID

# No payload to send but field is still used to send
payload_data = ''
variables = {}

# Build the entire url to grab the business object schema
target_url = url_call + url_path

# Issue the REST API call and retrieve the information
request_response = urllib.request.Request(target_url, headers=header_info, data=bytes(payload_data, encoding="utf-8"),
                                          method='GET')
resp = urllib.request.urlopen(request_response, context=ssl_context)

cmdb_payload = {}
cmdb_payload["busObId"] = fsimporttable_busObjID

# Read the json responses
request_response1 = json.loads(resp.read())

# Need to read and store the field definitions
table_fields = request_response1['fieldDefinitions']
table_field_limited = ["U_ClassificationMethod", "U_Comment", "U_Company", "U_ComplianceStatus", "U_Department",
                       "U_DeviceInterfaces", "U_DHCPDeviceClass", "U_DHCPDeviceOS", "U_DHCPDomainName",
                       "U_DHCPHostname", "U_DHCPOptionsFingerPrint", "U_DHCPServerAddress", "U_DHCPVendorClass",
                       "U_DisplayName", "U_DistinguishedName", "U_DNSName", "U_ExternalDrives", "U_Function",
                       "U_HostIsOnline", "U_HotFixInstalled", "U_IntranetWSUSServer", "U_IPAddress", "U_IPv6Address",
                       "U_IPv6LinkLocalAddress", "U_LDAPUserName", "U_LinuxHostname", "U_LinuxManagable",
                       "U_LinuxManageableSSHDirect", "U_LinuxUser", "U_LinuxVersion", "U_MACAddress",
                       "U_MicrosoftAppsInstalled", "U_MobilePhone", "U_NetBIOSDomain", "U_NetBIOSHostname",
                       "U_NetBIOSMembershipType", "U_NetworkAdapters", "U_NetworkFunction", "U_NICVendor",
                       "U_NICVendorValue", "U_NumberOfHostsOnPort", "U_NumberOfIPAddresses", "U_OpenPorts",
                       "U_OSFingerprint", "U_Phone", "U_RunningConfig", "U_RunningConfigTime",
                       "U_SecureConnectorDeploymentType", "U_SecureConnectorSysTrayDisplay", "U_SecureConnectorVersion",
                       "U_ServiceBanner", "U_SignedInStatus", "U_StreetAddress", "U_SwitchHostname", "U_SwitchIP",
                       "U_SwitchIPandPortName", "U_SwitchLocation", "U_SwitchPortAction", "U_SwitchPortAlias",
                       "U_SwitchPortConfigurations", "U_SwitchPortConnect", "U_SwtichPortName",
                       "U_SwitchPortPoEConnectedDevice", "U_SwitchPortPoEPowerConsumption", "U_SwitchPortVLAN",
                       "U_SwtichPortVLANGroup", "U_SwitchPortVLANName", "U_SwitchPortVoiceDevice",
                       "U_SwitchPortVoiceVLAN", "U_SwitchVendor", "U_SwitchVirtualInterface", "U_SwitchVoIPPortn",
                       "U_SystemDescription", "U_Title", "U_User", "U_UserGivenName", "U_VirtualMachineHardware",
                       "U_VirtualMachinePowerState", "U_WindowsAntiSpywareInstalled", "U_WindowsAntiVirusInstalled",
                       "U_WindowsAntiVirusRunning", "U_WindowsAntiVirusUpdate", "U_WindowsApplicationsInstalled",
                       "U_WindowsCloudStorageInstalled", "U_WindowsHardDriveEncryption",
                       "U_WindowsHardDriveEncryptionState", "U_WindowsInstantMessagingInstalled", "U_WindowsBehindNAT",
                       "U_WindowsLoggedOn", "U_WindowsManageableDomain", "U_WindowsManageableDomainCurrent",
                       "U_WindowsManageableLocal", "U_WindowsManageableSecureConnector", "U_WindowsPeerToPeerInstalled",
                       "U_WindowsPeerToPeerRunning", "U_WindowsPersonalFirewall", "U_WindowsUpdateAgentInstalled",
                       "U_WindowsUpdatesInstalledRebootRequired", "U_WindowsVersion", "U_WindowsVersionCPEFormat",
                       "U_WindowsVersionFineTuned", "U_WLANAPLocation", "U_WLANAPName", "U_WLANAssociationStatus",
                       "U_WLANAuthenticationMethod", "U_WLANBSSID", "U_WLANClientConnectivityStatus",
                       "U_WLANClientRole", "U_WLANClientUserAgent", "U_WLANClientUserName", "U_WLANClientVLAN",
                       "U_WLANCIPIP", "U_WLANDetectedClientType", "U_WLANManagingController", "U_WLANNetworkFunction",
                       "U_WLANSSID"]
# Map the field definitions to their individual object id's
field_name_to_field_busobjid_map = {}
for row in table_fields:
    field_name = row['name']
    field_id = row['fieldId']

    # Lets limit the payload to a minor set of fields.  To adjust this add the field
    # to the table_field_limited list in order to include it
    if field_name in table_field_limited:
        field_name_to_field_busobjid_map[field_name] = field_id

cmdb_fields = []
dirty = True

# Setup the payload to submit the data to the staging table
for field in field_name_to_field_busobjid_map:
    cmdb_field = {}
    fieldname = str(field)

    if fieldname.startswith("U_") and fieldname != "U_":
        try:
            ct_fieldname = "cherwell_" + fieldname
            logging.debug(ct_fieldname)
            parameter_field = params[ct_fieldname]
            # check to make sure there is a passed value.  If not do not include
            # in the payload.  This is used to prevent sending of empty fields

            if parameter_field != "Irresolvable" and parameter_field != "":
                cmdb_field["value"] = parameter_field
                cmdb_field["dirty"] = dirty
                cmdb_field["name"] = fieldname
                cmdb_field["fieldId"] = field_name_to_field_busobjid_map[fieldname]
                cmdb_fields.append(cmdb_field)
        except:
            errormessage = "Error for field: " + ct_fieldname
            logging.debug(errormessage)

# Put together the final parts of the payload
cmdb_payload["fields"] = cmdb_fields
cmdb_payload["persist"] = dirty

# Set up the URL for the REST API to save the object
target_url = url_call + '/api/V1/savebusinessobject'

# Convert the payload to json in order to convert the values
# to the correct format for json
payload_data = json.dumps(cmdb_payload)

logging.debug("Payload for submission")
logging.debug(payload_data)

# Issue the request for the save
request_response = urllib.request.Request(target_url, headers=header_info, data=bytes(payload_data, encoding="utf-8"),
                                          method='POST')

# Capture the response from the submission
response = {}
resp = urllib.request.urlopen(request_response, context=ssl_context)

# For actions, the response object must have a field named "succeeded" to denote if the action suceeded or not.
# The field "troubleshooting" is optional to display user defined messages in CounterACT for actions.

if resp.getcode() == 200:
    response["succeeded"] = True
    request_response = json.loads(resp.read())
    id = request_response['busObRecId']
    logging.debug("(CREATE) The record id created was {}".format(id))
    response["RecID"] = id
else:
    response["succeeded"] = False
    response["troubleshooting"] = "Failed action. Response code: {}".format(resp.getcode())

logging.debug("Add to CMDB result: ")
logging.debug(response)
