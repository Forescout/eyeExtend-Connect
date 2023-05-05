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

import base64
import logging

import requests
from requests.exceptions import HTTPError

MI_PROTOCOL = "https"
MI_SERVER_USERNAME = params["connect_mobileironmdm_user"]
MI_SERVER_PASSWORD = params["connect_mobileironmdm_password"]
MI_SERVER_ADDRESS = params["connect_mobileironmdm_server_url"]

# construct 'application inventory resolve' response to CounterACT
response = {}

mi_to_ct_subfields_composite_map = {
    "identifier": "connect_mobileironmdm_app_id",
    "name": "connect_mobileironmdm_app_name",
    "managed": "connect_mobileironmdm_app_managed",
    "version": "connect_mobileironmdm_app_version"
}

if params.get("connect_mobileironmdm_device_uid"):
    device_mdm_id = params.get("connect_mobileironmdm_device_uid")

    app_url = MI_PROTOCOL + "://" + MI_SERVER_ADDRESS + "/msa/v1/cps/device/application"

    logging.debug("MI App Resolve URL " + app_url)

    auth_string = "{}:{}".format(MI_SERVER_USERNAME, MI_SERVER_PASSWORD)
    base64string = base64.b64encode(auth_string.encode('utf-8'))
    header_auth_string = "".join(chr(x) for x in base64string)
    # logging.debug("Auth Basic " + header_auth_string)

    payload = "{ \"identifiers\": [\"" + device_mdm_id + "\"] }"
    logging.debug("Data-raw: " + payload)
    data = payload.encode("utf-8")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + header_auth_string
    }

    try:
        logging.debug("Starting app inventory resolve...")

        prop_response = requests.request("POST", app_url, headers=headers, data=payload, verify=ssl_verify)
        logging.debug("MI App Resolve response: " + str(prop_response.text.encode("utf-8")))

        # handle empty response
        if len(prop_response.text) == 0:
            logging.debug("No apps for device_mdm_id: " + device_mdm_id)
            response["succeeded"] = False
            response["error"] = "MBI Host does not have any Apps installed. MDM Device ID= {}".format(device_mdm_id)
        else:
            apps = prop_response.json()[0]["applications"]

            # list of software applications sent to Forescout
            client_apps_list = []

            properties = {}

            app_count = len(apps)
            for i in range(app_count):
                app = apps[i]
                application = {}
                for prop_key, prop_val in app.items():
                    if prop_key in mi_to_ct_subfields_composite_map.keys():
                        subfield_name = mi_to_ct_subfields_composite_map[prop_key]
                        application[subfield_name] = prop_val
                client_apps_list.append(application)

            properties["connect_mobileironmdm_client_apps"] = client_apps_list
            response["properties"] = properties
            logging.debug(response)

        logging.debug("App inventory resolve completed")

    except HTTPError as e:
        response["succeeded"] = False
        response["error"] = "Could not connect to MobileIron. HTTP Response code: {}".format(e.code)
    except Exception as e:
        response["succeeded"] = False
        response["error"] = "Could not connect to MobileIron. {}".format(str(e))
else:
    response["succeeded"] = False
    response["error"] = "Device MDM identifier field is empty."
