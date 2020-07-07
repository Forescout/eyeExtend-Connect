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

incident_busObjID = ''
incident_Name = ''

# ----- Process table information

# Grab the table name based on the parameter
tablename = "Incident"

# Build the entire url
target_url = url_call + url_path + tablename
try:
    # Issue the REST API call and retrieve the information
    request_response = urllib.request.Request(target_url, headers=header_info, data=bytes(payload_data, encoding="utf-8"), method='GET')
    resp = urllib.request.urlopen(request_response, context=ssl_context)

    # Read the json responses
    request_response = json.loads(resp.read())

    # Process the output based on which paramter is being pulled back
    # Extract the ObjID and the Display Name
    incident_busObjID = request_response[0]['busObId']
    incident_Name = request_response[0]['name']
except Exception as e:
    response["succeeded"] = False
    response["troubleshooting"] = "Failed action. Response: {}".format(str(e))


# Server URL update needed to grab the objects schema id
# this is required to build the payload for the submission
# of data as the busObj name and ID are required to process
url_path = "/api/V1/getbusinessobjectschema/busobid/" + incident_busObjID


# No payload to send but field is still used to send
payload_data = ''
variables = {}

# Build the entire url to grab the business object schema
target_url = url_call + url_path

try:
    # Issue the REST API call and retrieve the information
    request_response = urllib.request.Request(target_url, headers=header_info, data=bytes(payload_data, encoding="utf-8"), method='GET')
    resp = urllib.request.urlopen(request_response, context=ssl_context)

    # Setting up the payload to create the incident
    incident_payload = {}
    incident_payload["busObId"] = incident_busObjID

    # Read the json responses
    request_response1 = json.loads(resp.read())
    incident_obj = request_response1['fieldDefinitions']

    # Need to read and store the field definitions
    incident_fields = ["Service","Category","Subcategory","Description","Priority","CustomerRecID","Source","ShortDescription","ConfigItemDisplayName", "ConfigItemRecID"]

    # Map the field definitions to their individual object id's
    field_name_to_field_busobjid_map = {}
    counter = 0
    for row in incident_obj:
        field_name = row['name']
        field_id = row['fieldId']
        if field_name in incident_fields:
            field_name_to_field_busobjid_map[field_name] = field_id
            counter = counter + 1

    logging.debug(field_name_to_field_busobjid_map)

    incident_fields=[]
    dirty = True
except Exception as e:
    response["succeeded"] = False
    response["troubleshooting"] = "Failed action. Response: {}".format(str(e))

# Add to the payload to submit the data to the incident table
for field in field_name_to_field_busobjid_map:
    incident_field={}
    fieldname = str(field)
    try:
        ct_fieldname = "cherwell_" + fieldname
        logging.debug(ct_fieldname)
        parameter_field = params[ct_fieldname]
        incident_field["value"] = parameter_field
        incident_field["dirty"] = dirty
        incident_field["name"] = fieldname
        incident_field["fieldId"] = field_name_to_field_busobjid_map[fieldname]
        incident_fields.append(incident_field)
    except:
        errormessage = "Error for field: " + ct_fieldname
        logging.debug(errormessage)

# Put together the final parts of the payload to build a single payload
incident_payload["fields"] = incident_fields
incident_payload["persist"] = dirty

# Set up the URL for the REST API to save the object
target_url = url_call + '/api/V1/savebusinessobject'

# Convert the payload to json in order to convert the values
# to the correct format for json
payload_data = json.dumps(incident_payload)
logging.debug("Payload for submission")
logging.debug(payload_data)
try:
    # Issue the request for the save
    request_response = urllib.request.Request(target_url, headers=header_info, data=bytes(payload_data, encoding="utf-8"), method='POST')

    # Collect the response from incident creation
    response = {}
    resp = urllib.request.urlopen(request_response, context=ssl_context)

    # For actions, the response object must have a field named "succeeded" to denote if the action suceeded or not.
    # The field "troubleshooting" is optional to display user defined messages in CounterACT for actions.

    if resp.getcode() == 200:
        response["succeeded"] = True
        request_response = json.loads(resp.read())
        id = request_response['busObPublicId']
        logging.debug("(INCIDENT CREATED) The record id created was {}".format(id))
        response["Incident_ID"] = id
    else:
        response["succeeded"] = False
        response["troubleshooting"] = "Failed action. Response code: {}".format(resp.getcode())

    logging.debug("Incident Creation result: ")
    logging.debug(response)
except Exception as e:
    response["succeeded"] = False
    response["troubleshooting"] = "Failed action. Response: {}".format(str(e))
