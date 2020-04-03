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

''' Test connection to google cloud '''
import json
import urllib.request
import urllib.parse
import urllib
# import ssl
# import jwt
# import time
# from time import gmtime, strftime, sleep
# from datetime import datetime, timedelta
# import base64

##################
# FUNCTIONS
##################


# def get_gcp_data(url, max_page, page_token):
#     ''' HTTP get Google Project Data '''
#     # Header
#     header = {"Authorization": "Bearer " + BEARER_TOKEN}
#
#     if page_token == "":
#         REQUEST_URL = url+max_page
#     else:
#         REQUEST_URL = url+max_page+page_token
#
#     # print(REQUEST_URL)
#     request = urllib.request.Request(REQUEST_URL, headers=header)
#     resp = urllib.request.urlopen(request, context=ssl_context)
#
#     return request_response

# FUNCTIONS END #


# GET Params Configuration
AUD_URL = params["connect_googleengine_aud_url"]
CLIENT_EMAIL = params["connect_googleengine_client_email"]
SCOPE = params["connect_googleengine_claim_scope"]
PRIVATE_KEY = params["connect_googleengine_private_key"]
PROJECTS_FORBIDDEN = params["connect_googleengine_projects_forbidden"]
PAGE_SIZE = params["connect_googleengine_page_size"]

BEARER_TOKEN = params.get("connect_authorization_token")

logging.info("Starting Test")

response = {}

if BEARER_TOKEN is None or BEARER_TOKEN is "":
    response["succeeded"] = False
    response["result_msg"] = "Could not connect to Google Cloud Platform."

else:
    # Request Projects
    # projects_request = urllib.request.Request(REQUEST_URL, headers=header)

    try:
        # Projects
        # ADD-TODO, Need to add logic for multi pages being returned
        # Not sure if it will ever happen, maybe fore large customers
        # With more than 500 projects
        PROJECT_URL = "https://cloudresourcemanager.googleapis.com/v1/projects"
        # Paging parameters are different on some API's, Duplicated here per API
        PAGING_PARAMS = "?pageSize=" + PAGE_SIZE
        PROJECTS_URL = PROJECT_URL + PAGING_PARAMS

        # Header
        header = {"Authorization": "Bearer " + BEARER_TOKEN}

        # Request Projects
        projects_request = urllib.request.Request(PROJECTS_URL, headers=header)
        # Response
        projects_response = urllib.request.urlopen(projects_request, context=ssl_context)

        if projects_response.getcode() == 200:
            json_projects_response = json.loads(projects_response.read())
            logging.info("Test Passed ")
            response["succeeded"] = True
            response["result_msg"] = \
                f"Successfully connected. No. of Projects {len(json_projects_response['projects'])}"

    except urllib.error.HTTPError as error:
        logging.info(f"Error Test Failed : {error.reason}")
        logging.debug(f"HTTPError code : {error.read()}")

        response["succeeded"] = False
        response["error"] = f"Error Test Failed : {error.reason}"
