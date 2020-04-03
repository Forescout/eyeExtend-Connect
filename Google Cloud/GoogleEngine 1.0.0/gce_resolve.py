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

''' Get GCP Engine data resolve script
    Request a engine ID
    Property requirments ID, ProjectID, Zone (Learned from previous full poll)
'''
import json
import urllib.request
import urllib.parse
import urllib
# import ssl
# import jwt
# import time
# from time import gmtime, strftime, sleep
from datetime import datetime
# import base64
# import random

##################
# FUNCTIONS
##################

def build_response_properties(endpoint, passed_project, passed_project_id):
    ''' Build the properties fields for the response '''
    # Properties that are obtained outside of the instance data
    properties[GCT_TO_CT_PROPS_MAP['project']] = passed_project
    properties[GCT_TO_CT_PROPS_MAP['projectId']] = passed_project_id
    # Zone obtained via zone loop
    properties[GCT_TO_CT_PROPS_MAP['zone']] = get_url_end(endpoint['zone'])
    # Convert RFC3339 date format to epoch
    properties[GCT_TO_CT_PROPS_MAP['creationTimestamp']] =\
        convert_rfc3339_date(endpoint['creationTimestamp'])

    # JSON Instance map Properties
    properties[GCT_TO_CT_PROPS_MAP['id']] = endpoint['id']
    properties[GCT_TO_CT_PROPS_MAP['status']] = endpoint['status']
    properties[GCT_TO_CT_PROPS_MAP['name']] = endpoint['name']
    properties[GCT_TO_CT_PROPS_MAP['cpuPlatform']] =\
        endpoint['cpuPlatform']

    # False Vaulue
    properties[GCT_TO_CT_PROPS_MAP['canIpForward']] =\
        endpoint['canIpForward']
    properties[GCT_TO_CT_PROPS_MAP['deletionProtection']] =\
        endpoint['deletionProtection']
    properties[GCT_TO_CT_PROPS_MAP['startRestricted']] =\
        endpoint['startRestricted']
    properties[GCT_TO_CT_PROPS_MAP['machineType']] =\
        get_url_end(endpoint['machineType'])

    # Composite Data
    # DISK
    disk_composite = {}

    disk_composite['type'] = endpoint['disks'][0]['type']
    disk_composite['devicename'] = endpoint['disks'][0]['deviceName']
    disk_composite['boot'] = endpoint['disks'][0]['boot']
    disk_composite['autodelete'] = endpoint['disks'][0]['autoDelete']
    disk_composite['interface'] = endpoint['disks'][0]['interface']
    disk_composite['guestsosfeaturestype'] =\
        endpoint['disks'][0]['guestOsFeatures'][0]['type']
    disk_composite['disksizegb'] = endpoint['disks'][0]['diskSizeGb']

    properties['connect_googleengine_disk'] = disk_composite

    # INTERFACE
    network_composite = {}

    # Check if key accessConfigs exists, not always present on GCP data
    if 'accessConfigs' in endpoint['networkInterfaces'][0]:
        # Some Instances Do not Have a NAT-IP, Check If Key Exists
        if 'natIP' in \
                endpoint['networkInterfaces'][0]['accessConfigs'][0]:
            # Update
            network_composite['natip'] =\
                endpoint['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    network_composite['name'] = endpoint['networkInterfaces'][0]['name']
    network_composite['network'] =\
        get_url_end(endpoint['networkInterfaces'][0]['network'])
    network_composite['subnetwork'] =\
        get_url_end(endpoint['networkInterfaces'][0]['subnetwork'])

    properties['connect_googleengine_network'] = network_composite

    return properties


# Get the end of the URL
def get_url_end(url_string):
    ''' get the end of the URL '''
    # break into parts
    url_parts = urllib.parse.urlparse(url_string)
    # get last part
    path_parts = url_parts[2].rpartition('/')
    return path_parts[2]


# RFC3339 date to epoch time
def convert_rfc3339_date(rfc3339_date):
    ''' Convert the rfc3339 dates returned from google to EPOCH '''
    # Python 3.6.3 does not support tz offset with : (Need to remove colon)
    # Return int, microsecond not supported by Forescout
    # Split across several vars to make readable

    # Remove the last colon
    date_temp = rfc3339_date[::-1].replace(":", "", 1)[::-1]

    # Convert to date object
    date_object = datetime.strptime(date_temp, "%Y-%m-%dT%H:%M:%S.%f%z")

    # return epoch (timestamp) int value, remove microsonds
    return int(datetime.timestamp(date_object))

# FUNCTIONS END #


# Mapping between GCE API response fields to Forescout properties
GCT_TO_CT_PROPS_MAP = {
    "id": "connect_googleengine_id",
    "status": "connect_googleengine_status",
    "project": "connect_googleengine_project",
    "projectId": "connect_googleengine_projectid",
    "name": "connect_googleengine_instance_name",
    "creationTimestamp": "connect_googleengine_creationtimestamp",
    "zone": "connect_googleengine_zone",
    "networkInterfaces": "connect_googleengine_interface_name",
    "natIP": "connect_googleengine_natip",
    "machineType": "connect_googleengine_machinetype",
    "canIpForward": "connect_googleengine_canipforward",
    "cpuPlatform": "connect_googleengine_cpuplatform",
    "deletionProtection": "connect_googleengine_deletionprotection",
    "startRestricted": "connect_googleengine_startrestricted",
}

BEARER_TOKEN = params.get("connect_authorization_token")

ENGINE_ID = params["connect_googleengine_id"]
ENGINE_PROJECT = params["connect_googleengine_project"]
ENGINE_PROJECTID = params["connect_googleengine_projectid"]
ENGINE_ZONE = params["connect_googleengine_zone"]

logging.info("Checking Token")

if BEARER_TOKEN is None or BEARER_TOKEN is "":
    response = {}
    endpoint_data = {}
    logging.info("No Valid Bearer Token")
    response["succeeded"] = False
    response["troubleshooting"] = endpoint_data
else:
    response = {}
    fs_endpoints = []

    ENGINE_URL = \
    "https://www.googleapis.com/compute/v1/projects/" \
    + ENGINE_PROJECTID + "/zones/" + ENGINE_ZONE \
    + "/instances/" + ENGINE_ID

    logging.info(f"Resolve {ENGINE_URL}")

    # Header
    header = {"Authorization": "Bearer " + BEARER_TOKEN}

    engine_request = urllib.request.Request(ENGINE_URL, headers=header)
    try:
        engine_response = urllib.request.urlopen(engine_request, context=ssl_context)

        if engine_response.getcode() == 200:
            # Return JSON Data
            endpoint_data = json.loads(engine_response.read())

            logging.info(f"Engine =  {ENGINE_ID}")

            # Build Properties
            # Had to pass project and zone info to avoid out of look warning
            # NOTE
            # Project Name will require and extra API call, did not add
            # To reduce API rate limits
            # Project Name uses existing vale
            properties = {}
            properties = \
                build_response_properties(
                    endpoint_data,
                    ENGINE_PROJECT,
                    ENGINE_PROJECTID
                    )

            logging.debug(f"properties =  {properties}")

            # Update Forescout with endpoint_data
            response = {}
            response["properties"] = properties
        else:
            response["error"] = "Could not resolve properties."

    except urllib.error.HTTPError as error:
        logging.debug(f"HTTPError code : {error.read()}")

        response["succeeded"] = False
        response["error"] = f"Error Could Not Start Engine. {error.reason}"
