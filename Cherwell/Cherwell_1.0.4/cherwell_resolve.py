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

from datetime import datetime, timedelta

# Extract the token
bearer_token = params["connect_authorization_token"]

# Setup list of tables we are going iterate through
readtables = ["connect_cherwell_config_computer", "connect_cherwell_config_printer"]

# API URL
url_call = params["connect_cherwell_base_url"]


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

# Set a flag to track whether we found the MAC Address or not
found = False

# initialize all the variables that we are going to use to store the
# table information from Cherwell
payload_data = ''

response = {}

configurationitem_busObjID = ''
configurationitem_displayName = ''

logging.debug("Starting Cherwell Resolve Script")
# Initialize our hostname variables if they exist
nbthostname = ''
dhcphostname = ''
if 'nbthost' in params:
    nbthostname = params["nbthost"]
    logging.debug("nbthost = " + nbthostname)
if 'dhcp_hostname_v2' in params:
    dhcphostname = params["dhcp_hostname_v2"]
    logging.debug("dhcphost = " + dhcphostname)

try:
    # ----- Process table information
    for x in readtables:
        # Grab the table name based on the parameter
        tablename = params[x]

        # Create variable so we know if we failed to find anything via MACAddress. 
        # will set to 1  on failure so we can check by hostname
        CheckedMACAddress = 0


        # Build the entire url
        url_path = "/api/V1/getbusinessobjectsummary/busobname/"
        target_url = url_call + url_path + tablename
        logging.debug("Processing table info Target URL " + target_url + " Response: ")

        # Issue the REST API call and retrieve the information
        request_response = urllib.request.Request(target_url, headers=header_info, data=bytes(payload_data, encoding="utf-8"), method='GET')
        resp = urllib.request.urlopen(request_response, context=ssl_context)

        # Read the json responses
        request_response = json.loads(resp.read())

        # Process the output based on which paramter is being pulled back
        # Extract the ObjID and the Display Name
        configurationitem_busObjID = request_response[0]['busObId']
        configurationitem_displayName = request_response[0]['displayName']


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

        # Build the entire url
        target_url = url_call + url_path
        url_info['target_url'] = target_url

        # Issue the REST API call and retrieve the information
        logging.debug("Retreieve data with Target URL " + target_url + " Response: ")
        request_response = urllib.request.Request(target_url, headers=header_info, data=bytes(payload_data, encoding="utf-8"), method='GET')
        resp = urllib.request.urlopen(request_response, context=ssl_context)

        # Read the json responses
        request_response1 = json.loads(resp.read())


        table_fields = request_response1['fieldDefinitions']
        
        # iterate for both MACAddress and hostname
        # for number in range(2):
        def do_lookup(by_hostname=False, by_mac_address=False):
        
            #Decide if the function was called to search by hostname or by MAC address
            if by_hostname:
                lookup_field = params["connect_cherwell_cmdb_hostname"]
            elif by_mac_address:
                lookup_field = params["connect_cherwell_cmdb_mac_address"]
            else:
                raise Exception("Error")

            for row in table_fields:
                field_name = row['name']
                if field_name == lookup_field:
                    field_id = row['fieldId']

            logging.debug("Cherwell mac lookup " + params["mac"])
            cherwell_macaddress = params["mac"]
            
            logging.debug("nbthost " + nbthostname)
            logging.debug("dhcp_hostname_v2 " + dhcphostname)
            
            #Decide which hostname to use, either Netbios or DHCP
            if nbthostname:
                cherwell_hostname = nbthostname
                logging.debug("Using nbthost for hostname " + nbthostname)
            elif dhcphostname:
                cherwell_hostname = dhcphostname
                logging.debug("Using dhcp_hostname_v2 for hostname " + dhcphostname)
            else:
                return
            
    
    
            # Convert MAC Address to be colon delimited
            cherwell_macaddress_colons = ':'.join(cherwell_macaddress[i:i+2] for i in range(0,len(cherwell_macaddress),2))
            logging.debug("Cherwell mac lookup with colons " + cherwell_macaddress_colons)

            target_url = url_call + '/api/V1/getsearchresults'

            if by_hostname:
                payload_data = '{"busObId":"' + configurationitem_busObjID + '","filters":[{"fieldid":"' + field_id + '","operator":"eq","value":"' + cherwell_hostname + '"}],"includeAllFields":true}'
            elif by_mac_address:
                payload_data = '{"busObId":"' + configurationitem_busObjID + '","filters":[{"fieldid":"' + field_id + '","operator":"eq","value":"' + cherwell_macaddress_colons + '"}],"includeAllFields":true}'
            else:
                raise Exception("Error")        
                
        
            logging.debug("Get mac data via call to URL " + target_url + " and payload data " + payload_data)

            request_response = urllib.request.Request(target_url, headers=header_info, data=bytes(payload_data, encoding="utf-8"), method='POST')
            resp = urllib.request.urlopen(request_response, context=ssl_context)

            
            # Read the json responses
            request_response2 = json.loads(resp.read())
            
       
            # Make sure we got a record back with a businessObject in it
            logging.debug("TotalRows found = " + str(request_response2['totalRows']))
            
            
            return request_response2
            
            
        
        logging.debug("calling do_lookup")
        lookup_obj = do_lookup(by_hostname=True)
        
        
        #If we failed to lookup by hostname, let's do it by MAC address
        if lookup_obj['totalRows'] == 0:
            lookup_obj = do_lookup(by_mac_address=True)
            
        #If we didn't find anything, try another table
        if lookup_obj['totalRows'] == 0:
            continue
            
        logging.debug ("147")
        config_computer_obj = lookup_obj['businessObjects']

        # logging.debug ("Response JSON" + str(request_response1))
        logging.debug ("Value of found is " + str(found))
        
        # Is this the first record returned
        if found == True:
            logging.debug ("Raising Exception due to duplicate MAC Address found")
            raise Exception(f"Duplicate record found for MAC Address {cherwell_macaddress_colons}")
        else:
            found = True
        
        logging.debug ("Past found - parsing data")
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
                        logging.debug (f"Field Name {field_date_value}")
                    else:
                        properties[cherwell_to_ct_props_map[field_name]] = field_value
                        logging.debug (f"Field Name {field_value}")
        response["properties"] = properties
        if lookup_obj['totalRows'] != 0:
            break
except Exception as e:
    response["error"] = "Could not resolve properties {}".format(str(e))
