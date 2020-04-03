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

''' get GCP Engine data polling script '''
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


def get_gcp_data(url, max_page, page_token):
    ''' HTTP get GCP Engine data '''
    # Header
    header = {"Authorization": "Bearer " + BEARER_TOKEN}

    if page_token == "":
        request_url = url+max_page
    else:
        request_url = url+max_page+page_token

    request = urllib.request.Request(request_url, headers=header)
    resp = urllib.request.urlopen(request, context=ssl_context)
    json_response = json.loads(resp.read())

    return json_response


def build_response_properties(passed_endpoint, passed_project, passed_project_id, passed_zone):
    ''' Build the properties fields for the response '''
    # Properties that are obtained outside of the instance data
    # Project obtained via project loop
    properties[GCT_TO_CT_PROPS_MAP['project']] = passed_project
    properties[GCT_TO_CT_PROPS_MAP['projectId']] = passed_project_id
    # Zone obtained via zone loop
    properties[GCT_TO_CT_PROPS_MAP['zone']] = passed_zone
    # Convert RFC3339 date format to epoch
    properties[GCT_TO_CT_PROPS_MAP['creationTimestamp']] =\
        convert_rfc3339_date(passed_endpoint['creationTimestamp'])

    # JSON Instance map Properties
    properties[GCT_TO_CT_PROPS_MAP['id']] = passed_endpoint['id']
    properties[GCT_TO_CT_PROPS_MAP['status']] = passed_endpoint['status']
    properties[GCT_TO_CT_PROPS_MAP['name']] = passed_endpoint['name']
    properties[GCT_TO_CT_PROPS_MAP['cpuPlatform']] =\
        passed_endpoint['cpuPlatform']

    # False Vaulue
    properties[GCT_TO_CT_PROPS_MAP['canIpForward']] =\
        passed_endpoint['canIpForward']
    properties[GCT_TO_CT_PROPS_MAP['deletionProtection']] =\
        passed_endpoint['deletionProtection']
    properties[GCT_TO_CT_PROPS_MAP['startRestricted']] =\
        passed_endpoint['startRestricted']
    properties[GCT_TO_CT_PROPS_MAP['machineType']] =\
        get_url_end(passed_endpoint['machineType'])

    # DISK
    disk_composite = {}

    disk_composite['type'] = passed_endpoint['disks'][0]['type']
    disk_composite['devicename'] = passed_endpoint['disks'][0]['deviceName']
    disk_composite['boot'] = passed_endpoint['disks'][0]['boot']
    disk_composite['autodelete'] = passed_endpoint['disks'][0]['autoDelete']
    disk_composite['interface'] = passed_endpoint['disks'][0]['interface']
    disk_composite['guestsosfeaturestype'] =\
        passed_endpoint['disks'][0]['guestOsFeatures'][0]['type']
    disk_composite['disksizegb'] = passed_endpoint['disks'][0]['diskSizeGb']

    properties['connect_googleengine_disk'] = disk_composite

    # INTERFACE
    network_composite = {}

    # Composite Data
    # Check if key accessConfigs exists, not always present on GCP data
    if 'accessConfigs' in passed_endpoint['networkInterfaces'][0]:
        # Some Instances Do not Have a NAT-IP, Check If Key Exists
        if 'natIP' in \
                passed_endpoint['networkInterfaces'][0]['accessConfigs'][0]:
            # Update
            network_composite['natip'] =\
                passed_endpoint['networkInterfaces'][0]['accessConfigs'][0]['natIP']

    network_composite['name'] = passed_endpoint['networkInterfaces'][0]['name']
    network_composite['network'] =\
        get_url_end(passed_endpoint['networkInterfaces'][0]['network'])
    network_composite['subnetwork'] =\
        get_url_end(passed_endpoint['networkInterfaces'][0]['subnetwork'])

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

PROJECTS_FORBIDDEN = params["connect_googleengine_projects_forbidden"]
PAGE_SIZE = params["connect_googleengine_page_size"]
BEARER_TOKEN = params.get("connect_authorization_token")

logging.info("Checking Token")

if BEARER_TOKEN is None or BEARER_TOKEN is "":
    response = {}
    endpoint_data = {}
    logging.debug("No Valid Bearer Token")
    response["succeeded"] = False
    response["troubleshooting"] = endpoint_data
else:
    # Projects
    # ADD-TODO, New logic to decrease poll time
    #  I will add to the next release.
    PROJECTS_URL = "https://cloudresourcemanager.googleapis.com/v1/projects"
    # Paging parameters are different on some API's, Duplicated here per API
    PAGING_PARAMS = "?pageSize=" + PAGE_SIZE
    PROJ_URL = PROJECTS_URL + PAGING_PARAMS

    # Request Projects
    projects_response = get_gcp_data(PROJECTS_URL, PAGING_PARAMS, "")

    # ADD-TODO, Need to add logic for multi pages being returned
    # Not sure if it will ever happen, maybe fore large customers
    # With more than 500 projects

    response = {}
    fs_endpoints = []

    logging.info("Starting Loop Projects/Zones/Instances")

    #####################
    # LOOP Start
    # Project
    #   Zones-per-Project
    #       Instances
    #####################
    for project in projects_response['projects']:
        # Active Only Projects and not Forbidden Projects. example Remote
        if project['lifecycleState'] == "ACTIVE" and \
                project['name'] not in PROJECTS_FORBIDDEN:

            logging.info(f"Project =  {project['name']}")

            # GET Zones for project
            ZONES_URL = "https://compute.googleapis.com/compute/v1/projects/"\
                + project['projectId'] + "/zones"

            # Paging parameters are different on some API's
            PAGING_PARAMS = "?maxResults=" + PAGE_SIZE
            ZONE_URL = ZONES_URL + PAGING_PARAMS

            # Get Zones per project
            zones_response = get_gcp_data(ZONES_URL, PAGING_PARAMS, "")

            logging.info(f"No. Zones =  {len(zones_response['items'])}")

            for zone in zones_response['items']:
                # Build Project / Zone URL
                INSTANCE_URL = \
                    "https://www.googleapis.com/compute/v1/projects/" \
                    + project['projectId'] + "/zones/" + zone['name'] \
                    + "/instances"

                # Add Page Parameters for Instances
                INST_URL = INSTANCE_URL + PAGING_PARAMS

                # GET Instances, Make the initial request
                # Check nextPageToken to see if we need to make more requests
                instance_response = get_gcp_data(INSTANCE_URL, PAGING_PARAMS, "")

                # Check if we received data back for project/zone
                if instance_response.get('items'):
                    # Loop over first page of items
                    # Process response
                    for endpoint_data in instance_response['items']:
                        #
                        fs_endpoint = {}
                        # Get IP Address
                        fs_endpoint["ip"] =\
                            endpoint_data['networkInterfaces'][0]['networkIP']

                        logging.info(f"Instance =  {fs_endpoint['ip']}")

                        # Build Properties
                        # Had to pass project and zone info.
                        # to avoid out of loop warning
                        properties = {}
                        properties = \
                            build_response_properties(
                                endpoint_data,
                                project['name'],
                                project['projectId'],
                                zone['name']
                                )

                        # Add Properties to endpoint data
                        fs_endpoint["properties"] = properties
                        # Append endpoint to endpoints
                        fs_endpoints.append(fs_endpoint)

                # Check if we have multilple pages
                if instance_response.get('nextPageToken'):
                    # Loop over Pages
                    while instance_response.get('nextPageToken'):
                        # GET More Pages
                        # Build nextPageToken Param
                        TOKEN_PARAM = "&pageToken=" + \
                            instance_response['nextPageToken']
                        # Request Next Page
                        instance_response = get_gcp_data(
                            INSTANCE_URL, PAGING_PARAMS, TOKEN_PARAM)
                        # Process response
                        for endpoint_data in instance_response['items']:
                            #
                            fs_endpoint = {}
                            # Get IP Address
                            fs_endpoint["ip"] =\
                                endpoint_data['networkInterfaces'][0]['networkIP']

                            logging.info(f"Instance =  {fs_endpoint['ip']}")

                            # Build Properties
                            properties = {}
                            properties = \
                                build_response_properties(
                                    endpoint_data,
                                    project['name'],
                                    project['projectId'],
                                    zone['name']
                                    )

                            # Add Properties to endpoint data
                            fs_endpoint["properties"] = properties
                            # Append endpoint to endpoints
                            fs_endpoints.append(fs_endpoint)

                        # Update nextPageToken
                        if instance_response.get('nextPageToken'):
                            TOKEN_PARAM = "&pageToken=" + \
                                instance_response['nextPageToken']
                        else:
                            # No More Pages
                            TOKEN_PARAM = ""

    logging.debug(f"endpoints =  {fs_endpoints}")

    # Update Forescout with endponts
    response = {}
    response["endpoints"] = fs_endpoints
