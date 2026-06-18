"""
copywrite RM
"""

import json
import urllib.request
from datetime import datetime, timedelta

# Extract the token
bearer_token = params["connect_authorization_token"]

# Setup list of tables we are going iterate through
readtables = ["connect_waypoint_configuration_item"]

# API URL
url_call = params["connect_waypoint_base_url"]
url_path = "/api/V1/getbusinessobjectsummary/busobname/"

# URL Header Type Information
url_content_type = params["connect_waypoint_content_type"]
url_accept_type = params["connect_waypoint_accept_type"]

# -------------------------------------------------------------------------------------------------

# ***** START - AUTH API CONFIGURATION ***** #

# Setup the header information to retrieve a token from WayPoint
header_info = {
    'Content-Type': url_content_type,
    'Accept': url_accept_type,
    'Authorization': bearer_token
}

# initialize all the variables that we are going to use to store the
# table information from WayPoint
payload_data = ''
variables = {}
properties = {}
response = {}

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
        request_response = urllib.request.Request(target_url, headers=header_info,
                                                  data=bytes(payload_data, encoding="utf-8"), method='GET')
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

    # No payload to send but field is still used to send
    payload_data = ''

    # Build the entire url
    target_url = url_call + url_path
    url_info['target_url'] = target_url

    # Issue the REST API call and retrieve the information
    request_response = urllib.request.Request(target_url, headers=header_info,
                                              data=bytes(payload_data, encoding="utf-8"), method='GET')
    resp = urllib.request.urlopen(request_response, context=ssl_context)

    # Read the json responses
    request_response1 = json.loads(resp.read())

    table_fields = request_response1['fieldDefinitions']
    lookup_field = params["connect_waypoint_cmdb_fs_mac_address"]
    polling_field = params["connect_waypoint_cmdb_mac_address"]

    for row in table_fields:
        field_name = row['name']
        if field_name == lookup_field:
            field_id = row['fieldId']
        if field_name == polling_field:
            field_macaddress = row['fieldId']

    # -----------------------------------------------------------------------------------------------

    target_url = url_call + '/api/V1/getsearchresults'
    payload_data = '{"busObId":"' + configurationitem_busObjID + '","filters":[{"fieldid":"' + field_macaddress + '","operator":"gt","value":"0"}],"includeAllFields":true}'

    request_response = urllib.request.Request(target_url, headers=header_info,
                                              data=bytes(payload_data, encoding="utf-8"), method='POST')
    resp = urllib.request.urlopen(request_response, context=ssl_context)

    # Read the json responses
    request_response1 = json.loads(resp.read())
    config_computer_obj = request_response1['businessObjects']

    WayPoint_fields = ["ConfigurationItemTypeName", "ConfigurationItemTypeID", "RecID", "SerialNumber",
                       "ConfigurationItemTypeName", "CreatedDateTime", "PurchaseDate", "AssetStatus", "AssetTag",
                       "PrimaryUse", "Model", "OperatingSystemVersion", "OperatingSystem", "OperatingSystemFamily",
                       "OperatingSystemGroup", "OperatingSystemServicePack", "Vendor", "Manufacturer", "AssetOwner",
                       "OwnedByEmail", "AssetType", "LocationRoom", "LocationBuilding", "LocationFloor",
                       "PrimaryUserVIP", "PrimaryUserName", "PrimaryUserEmail", "Barcode", "FriendlyName",
                       "BIOSVersion", "CreatedBy", "LastModifiedDateTime", "LastModBy", "ContractID", "MACAddress",
                       "IPAddress", "HostName"]

    WayPoint_to_ct_props_map = {
        "ConfigurationItemTypeID": "connect_waypoint_cmdbclassbusobjid", "RecID": "connect_waypoint_recordid",
        "SerialNumber": "connect_waypoint_serialnumber",
        "ConfigurationItemTypeName": "connect_waypoint_configurationitemtypename",
        "PurchaseDate": "connect_waypoint_purchasedate", "CreatedDateTime": "connect_waypoint_createddatetime",
        "AssetStatus": "connect_waypoint_assetstatus", "AssetTag": "connect_waypoint_assettag",
        "PrimaryUse": "connect_waypoint_primaryuse", "Model": "connect_waypoint_model",
        "OperatingSystemVersion": "connect_waypoint_operatingsystemversion",
        "OperatingSystem": "connect_waypoint_operatingsystem",
        "OperatingSystemFamily": "connect_waypoint_operatingsystemfamily",
        "OperatingSystemGroup": "connect_waypoint_operatingsystemgroup",
        "OperatingSystemServicePack": "connect_waypoint_operatingsystemservicepack",
        "Vendor": "connect_waypoint_vendor", "Manufacturer": "connect_waypoint_manufacturer",
        "AssetOwner": "connect_waypoint_assetowner", "OwnedByEmail": "connect_waypoint_ownedbyemail",
        "AssetType": "connect_waypoint_assettype", "LocationRoom": "connect_waypoint_locationroom",
        "LocationBuilding": "connect_waypoint_locationbuilding", "LocationFloor": "connect_waypoint_locationfloor",
        "PrimaryUserVIP": "connect_waypoint_primaryuservip", "PrimaryUserName": "connect_waypoint_primaryusername",
        "PrimaryUserEmail": "connect_waypoint_primaryuseremail", "Barcode": "connect_waypoint_barcode",
        "FriendlyName": "connect_waypoint_friendlyname", "BIOSVersion": "connect_waypoint_bios",
        "CreatedBy": "connect_waypoint_createdby", "LastModifiedDateTime": "connect_waypoint_lastmodifieddate",
        "LastModBy": "connect_waypoint_lastmodby", "ContractID": "connect_waypoint_contractid",
        "MACAddress": "connect_waypoint_macaddress", "IPAddress": "connect_waaypoint_ipaddress",
        "HostName": "connect_waypoint_hostname"}

    WayPoint_date_fields = ["CreatedDateTime", "LastModifiedDateTime", "PurchaseDate"]

    # counter = 0
    # cmdb_row = {}
    # row_records = {}
    endpoints = []
    for row in config_computer_obj:
        endpoint = {}
        properties = {}
        computer_records = row['fields']
        for field in computer_records:
            field_name = field["name"]
            field_value = field["value"]
            if field_name in WayPoint_fields:
                if field_name == "MACAddress":
                    field_value = field_value.replace(":", "")
                    endpoint["mac"] = field_value.lower()
                else:
                    if field_name in WayPoint_date_fields:
                        properties[WayPoint_to_ct_props_map[field_name]] = datetime.strptime(field_value,
                                                                                             "%m/%d/%Y %I:%M:%S %p").strftime(
                            '%s')
                    else:
                        properties[WayPoint_to_ct_props_map[field_name]] = field_value
        endpoint["properties"] = properties
        endpoints.append(endpoint)
    response["endpoints"] = endpoints
except Exception as e:
    response["error"] = "Could not resolve properties {}".format(str(e))
