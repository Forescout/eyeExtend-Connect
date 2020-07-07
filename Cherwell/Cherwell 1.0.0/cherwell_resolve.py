'''
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
'''

import jwt  # PyJWT version 1.6.1 as of the time of authoring
import uuid
import json
import urllib.request
import time
from time import gmtime, strftime, sleep
from datetime import datetime, timedelta

# Extract the token
bearer_token = params["connect_authorization_token"]

# Setup list of tables we are going iterate through
readtables = ["connect_cherwell_configuration_item"]

# API URL
url_call = params["connect_cherwell_base_url"]
url_path = "/api/V1/getbusinessobjectsummary/busobname/"

# URL Header Type Information
url_content_type = params["connect_cherwell_content_type"]
url_accept_type = params["connect_cherwell_accept_type"]

# -------------------------------------------------------------------------------------------------

# ***** START - AUTH API CONFIGURATION ***** #

# Setup the header information to retrieve a token from Cherwell
header_info = {
    'Content-Type': url_content_type,
    'Accept': url_accept_type,
    'Authorization': 'Bearer ' + bearer_token
}

# initialize all the variables that we are going to use to store the
# table information from Cherwell
payload_data = ''

configurationitem_busObjID = ''
configurationitem_displayName = ''
try:
    # ----- Process table information
    for x in readtables:
        # Grab the table name based on the parameter
        tablename = params[x]

        # Build the entire url
        target_url = url_call + url_path + tablename

        # Issue the REST API call and retrieve the information
        request_response = urllib.request.Request(target_url, headers=header_info, data=bytes(payload_data, encoding="utf-8"), method='GET')
        resp = urllib.request.urlopen(request_response, context=ssl_context)

        # Read the json responses
        request_response = json.loads(resp.read())

        # Process the output based on which paramter is being pulled back
        # Extract the ObjID and the Display Name
        configurationitem_busObjID = request_response[0]['busObId']
        configurationitem_displayName = request_response[0]['displayName']


    #
    url_info = {}
    # Server URL
    url_path = "/api/V1/getbusinessobjectschema/busobid/" + configurationitem_busObjID
    url_info["ci_busobjid"] = configurationitem_busObjID
    url_info["ci_displayname"] = configurationitem_displayName

    # ***** START - AUTH API CONFIGURATION ***** #


    # No payload to send but field is still used to send
    payload_data = ''
    variables = {}
    properties = {}
    response = {}

    # Build the entire url
    target_url = url_call + url_path
    url_info['target_url'] = target_url


    # Issue the REST API call and retrieve the information
    request_response = urllib.request.Request(target_url, headers=header_info, data=bytes(payload_data, encoding="utf-8"), method='GET')
    resp = urllib.request.urlopen(request_response, context=ssl_context)

    # Read the json responses
    request_response1 = json.loads(resp.read())

    table_fields = request_response1['fieldDefinitions']
    lookup_field = params["connect_cherwell_cmdb_fs_mac_address"]



    for row in table_fields:
        field_name = row['name']
        if field_name == lookup_field:
            field_id = row['fieldId']

    # -----------------------------------------------------------------------------------------------
    #cherwell_macaddress = "00505680cc82"
    cherwell_macaddress = params["mac"]

    target_url = url_call + '/api/V1/getsearchresults'
    payload_data = '{"busObId":"' + configurationitem_busObjID + '","filters":[{"fieldid":"' + field_id + '","operator":"eq","value":"' + cherwell_macaddress + '"}],"includeAllFields":true}'

    request_response = urllib.request.Request(target_url, headers=header_info, data=bytes(payload_data, encoding="utf-8"), method='POST')
    resp = urllib.request.urlopen(request_response, context=ssl_context)

    # Read the json responses

    request_response1 = json.loads(resp.read())
    config_computer_obj = request_response1['businessObjects']

    cherwell_fields = ["ConfigurationItemTypeName", "ConfigurationItemTypeID", "RecID", "SerialNumber", "ConfigurationItemTypeName", "CreatedDateTime", "PurchaseDate", "AssetStatus", "AssetTag", "PrimaryUse", "Model", "OperatingSystemVersion", "OperatingSystem", "OperatingSystemFamily", "OperatingSystemGroup", "OperatingSystemServicePack", "Vendor", "Manufacturer", "AssetOwner", "OwnedByEmail", "AssetType", "LocationRoom", "LocationBuilding", "LocationFloor", "PrimaryUserVIP", "PrimaryUserName", "PrimaryUserEmail", "Barcode", "FriendlyName", "BIOSVersion", "CreatedBy", "LastModifiedDateTime", "LastModBy", "ContractID", "MACAddress", "IPAddress", "HostName"]


    cherwell_to_ct_props_map = {
         "ConfigurationItemTypeID": "connect_cherwell_cmdbclassbusobjid", "RecID": "connect_cherwell_recordid", "SerialNumber": "connect_cherwell_serialnumber", "ConfigurationItemTypeName": "connect_cherwell_configurationitemtypename", "CreatedDateTime": "connect_cherwell_createddatetime", "PurchaseDate": "connect_cherwell_purchasedate", "AssetStatus": "connect_cherwell_assetstatus", "AssetTag": "connect_cherwell_assettag", "PrimaryUse": "connect_cherwell_primaryuse", "Model": "connect_cherwell_model", "OperatingSystemVersion": "connect_cherwell_operatingsystemversion", "OperatingSystem": "connect_cherwell_operatingsystem", "OperatingSystemFamily": "connect_cherwell_operatingsystemfamily", "OperatingSystemGroup": "connect_cherwell_operatingsystemgroup", "OperatingSystemServicePack": "connect_cherwell_operatingsystemservicepack", "Vendor": "connect_cherwell_vendor", "Manufacturer": "connect_cherwell_manufacturer", "AssetOwner": "connect_cherwell_assetowner", "OwnedByEmail": "connect_cherwell_ownedbyemail", "AssetType": "connect_cherwell_assettype", "LocationRoom": "connect_cherwell_locationroom", "LocationBuilding": "connect_cherwell_locationbuilding", "LocationFloor": "connect_cherwell_locationfloor", "PrimaryUserVIP": "connect_cherwell_primaryuservip", "PrimaryUserName": "connect_cherwell_primaryusername", "PrimaryUserEmail": "connect_cherwell_primaryuseremail", "Barcode": "connect_cherwell_barcode", "FriendlyName": "connect_cherwell_friendlyname", "BIOSVersion": "connect_cherwell_bios", "CreatedBy": "connect_cherwell_createdby", "LastModifiedDateTime": "connect_cherwell_lastmodifieddate", "LastModBy": "connect_cherwell_lastmodby", "ContractID": "connect_cherwell_contractid", "MACAddress": "connect_cherwell_macaddress", "IPAddress": "connect_cherwell_ipaddress", "HostName": "connect_cherwell_hostname"}

    cherwell_date_fields = ["CreatedDateTime","LastModifiedDateTime","PurchaseDate"]

    for row in config_computer_obj:
        computer_records = row['fields']
        for field in computer_records:
            field_name = field["name"]
            field_value = field["value"]
            if field_name in cherwell_fields:
                if field_name in cherwell_date_fields:
                    field_date_value = int(datetime.strptime(field_value, "%m/%d/%Y %I:%M:%S %p").strftime('%s'))
                    properties[cherwell_to_ct_props_map[field_name]] = field_date_value
                else:
                    properties[cherwell_to_ct_props_map[field_name]] = field_value
    response["properties"] = properties
except Exception as e:
    response["error"] = "Could not resolve properties {}".format(str(e))
