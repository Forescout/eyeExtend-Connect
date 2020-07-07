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
readtables = ["connect_cherwell_fs_staging_table", "connect_cherwell_configuration_item", "connect_cherwell_config_computer", "connect_cherwell_config_mobiledevice", "connect_cherwell_config_networkdevice", "connect_cherwell_config_notinventoried", "connect_cherwell_config_otherci", "connect_cherwell_config_printer", "connect_cherwell_config_server", "connect_cherwell_config_softwarelicense", "connect_cherwell_config_configsystem", "connect_cherwell_config_telephonyequipment"]

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
import_busObjID = ''
import_displayName = ''
configurationitem_busObjID = ''
configurationitem_displayName = ''
computer_busObjID = ''
computer_displayName = ''
mobile_busObjID = ''
mobile_displayName = ''
network_busObjID = ''
network_displayName = ''
notinvent_busObjID = ''
notinvent_displayName = ''
otherci_busObjID = ''
otherci_displayName = ''
printer_busObjID = ''
printer_displayName = ''
server_busObjID = ''
server_displayName = ''
software_busObjID = ''
software_displayName = ''
system_busObjID = ''
system_displayName = ''
telephony_busObjID = ''
telephony_displayName = ''
misc_busObjID = ''
misc_displayName = ''
misc_Name = ''
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
        if x == "connect_cherwell_fs_staging_table":
            import_busObjID = request_response[0]['busObId']
            import_displayName = request_response[0]['displayName']
        elif x == "connect_cherwell_configuration_item":
            configurationitem_busObjID = request_response[0]['busObId']
            configurationitem_displayName = request_response[0]['displayName']
        elif x == "connect_cherwell_config_computer":
            computer_busObjID = request_response[0]['busObId']
            computer_displayName = request_response[0]['displayName']
        elif x == "connect_cherwell_config_mobiledevice":
            mobile_busObjID = request_response[0]['busObId']
            mobile_displayName = request_response[0]['displayName']
        elif x == "connect_cherwell_config_networkdevice":
            network_busObjID = request_response[0]['busObId']
            network_displayName = request_response[0]['displayName']
        elif x == "connect_cherwell_config_notinventoried":
            notinvent_busObjID = request_response[0]['busObId']
            notinvent_displayName = request_response[0]['displayName']
        elif x == "connect_cherwell_config_otherci":
            otherci_busObjID = request_response[0]['busObId']
            otherci_displayName = request_response[0]['displayName']
        elif x == "connect_cherwell_config_printer":
            printer_busObjID = request_response[0]['busObId']
            printer_displayName = request_response[0]['displayName']
        elif x == "connect_cherwell_config_server":
            server_busObjID = request_response[0]['busObId']
            server_displayName = request_response[0]['displayName']
        elif x == "connect_cherwell_config_softwarelicense":
            software_busObjID = request_response[0]['busObId']
            software_displayName = request_response[0]['displayName']
        elif x == "connect_cherwell_config_configsystem":
            system_busObjID = request_response[0]['busObId']
            system_displayName = request_response[0]['displayName']
        elif x == "connect_cherwell_config_telephonyequipment":
            telephony_busObjID = request_response[0]['busObId']
            telephony_displayName = request_response[0]['displayName']
        else:
            misc_busObjID = request_response[0]['busObId']
            misc_displayName = request_response[0]['displayName']
            misc_Name = request_response[0]['name']
    # -----------------------------------------------------------------------------------------------

    # Process the output to feedback to the console
    response = {}
    if import_busObjID != "":
        response["succeeded"] = True
        #  response["result_msg"] = "Output: " + all_url
        response["result_msg"] = "Successfully retrieved information. \nDisplay Name: " + import_displayName + " \nBusiness Object ID: " + import_busObjID + " \nDisplay Name: " + configurationitem_displayName + " \nBusiness Object ID: " + configurationitem_busObjID + " \nDisplay Name: " + computer_displayName + " \nBusiness Object ID: " + computer_busObjID + "\nDisplay Name: " + mobile_displayName + " \nBusiness Object ID: " + mobile_busObjID + "\nDisplay Name: " + network_displayName + " \nBusiness Object ID: " + network_busObjID + "\nDisplay Name: " + notinvent_displayName + " \nBusiness Object ID: " + notinvent_busObjID + "\nDisplay Name: " + otherci_displayName + " \nBusiness Object ID: " + otherci_busObjID + "\nDisplay Name: " + printer_displayName + " \nBusiness Object ID: " + printer_busObjID + "\nDisplay Name: " + server_displayName + " \nBusiness Object ID: " + server_busObjID + "\nDisplay Name: " + software_displayName + " \nBusiness Object ID: " + software_busObjID + "\nDisplay Name: " + system_displayName + " \nBusiness Object ID: " + system_busObjID + "\nDisplay Name: " + telephony_displayName + " \nBusiness Object ID: " + telephony_busObjID + "\n-------------------------" + "\nTroubleshooting Only - Ok to be empty" + "\nName: " + misc_Name + "\nDisplay Name: " + misc_displayName + " \nBusiness Object ID: " + misc_busObjID
    else:
        response["succeeded"] = False
        response["result_msg"] = "Failed to pull information on the Forescout Tables."
except Exception as e:
    response["succeeded"] = False
    response["result_msg"] = "At least one object ID was not retrieved {}".format(str(e))
