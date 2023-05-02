'''
Copyright © 2021 Westcon Solutions Pte Ltd.

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

''' Resolve Cortex XDR Endpoint details '''
import uuid
import json
import urllib.request, urllib.error, urllib.parse
from datetime import datetime, timezone
import secrets
import string
import hashlib
# import logging so that we can log to the python server at /usr/local/forescout/plugin/connect/python_logs
import logging
from connectproxyserver import ConnectProxyServer, ProxyProtocol

logging.info("=======>>>>>Starting Cortex API resolve Script.")

# mapping between our App properties and the CT internal properties
# in this case, 'department' is returned from our remote host, and 'connect_Cortex_department' is the internal CT property name which must be unique & defined in 'properties.conf'
cortex_to_ct_props_map = {
    "endpoint_id": "connect_cortexxdr_read_endpointid",
    "endpoint_name": "connect_cortexxdr_read_endpointname",
    "endpoint_type": "connect_cortexxdr_read_endpointtype",
    "endpoint_status": "connect_cortexxdr_read_endpointstatus",
    "os_type": "connect_cortexxdr_read_ostype",
    "ip": "connect_cortexxdr_read_ip",
	"users": "connect_cortexxdr_read_user",
	"domain": "connect_cortexxdr_read_domain",
	"alias": "connect_cortexxdr_read_alias",
	"first_seen": "connect_cortexxdr_read_firstseen",
	"last_seen": "connect_cortexxdr_read_lastseen",
	"content_version": "connect_cortexxdr_read_contentversion",
	"installation_package":	"connect_cortexxdr_read_installationpackage",
	"active_directory":	"connect_cortexxdr_read_activedirectory",
	"install_date":	"connect_cortexxdr_read_installdate",
	"endpoint_version":	"connect_cortexxdr_read_endpointversion",
	"is_isolated": "connect_cortexxdr_read_isolation",
	"isolated_date": "connect_cortexxdr_read_isolationdate",
	"group_name": "connect_cortexxdr_read_groupname",
	"operational_status": "connect_cortexxdr_read_operationalstatus",
	"operational_status_description": "connect_cortexxdr_read_operationalstatusdesc",
	"scan_status": "connect_cortexxdr_read_scanstatus",
	"operating_system": "connect_cortexxdr_operating_system",
	"os_version": "connect_cortexxdr_os_version"
}

# CT will provide a params{} dictionary with the dependent properties you defined in 'properties.conf' & 'ssytem.conf' for each of your App's custom properties.

base_url = params['connect_cortexxdr_api_url']
auth_id = params['connect_cortexxdr_api_id']
auth_key = params['connect_cortexxdr_api_key']

# Generate a 64 bytes random string
nonce = "".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(64)])
# Get the current timestamp as milliseconds.
timestamp = int(datetime.now(timezone.utc).timestamp()) * 1000
# Generate the API auth key:
api_auth_key = "%s%s%s" % (auth_key, nonce, timestamp)
# Convert to bytes object
api_auth_key = api_auth_key.encode("utf-8")
# Calculate sha256 to use for Authorization:
api_key_hash = hashlib.sha256(api_auth_key).hexdigest()

header = {
           'x-xdr-timestamp': str(timestamp),
           'x-xdr-nonce': nonce,
           'x-xdr-auth-id': auth_id,
           'Authorization': api_key_hash,
           'Content-Type': 'application/json'
    }

if "ip" in params:
    ip_addr = params["ip"]
    
    data = {
    "request_data":{
         "filters":     [
                            { 
                                "field":"ip_list",
                                "operator":"in",
                                "value":[
                                            ip_addr
                                        ]
                            }
                        ]
                    }
    }

    #convert the data to post to json
    data = json.dumps(data)
    # Requests Proxy
    proxy_server = ConnectProxyServer(params)
    opener = proxy_server.get_urllib_request_https_opener(ProxyProtocol, ssl_context)

    # CT will provide a params{} dictionary with the dependent properties you defined in 'properties.conf' for each of your App's custom properties.
    logging.info("=======>>>>>Cortex: parameters supplied by CT: {}".format(params))

    # Get info on the passed ip address from server
    response = {}
    properties = {}
    logging.info("=======>>>>>Cortex: Resolving IP address: " + ip_addr)
    # Get device information
    try:
        request = urllib.request.Request(url=base_url+'/public_api/v1/endpoints/get_endpoint', data=bytes(data.encode("utf-8")), headers=header, method="POST")
        # resp = urllib.request.urlopen(request)
        resp = opener.open(request)
        request_response = json.loads(resp.read())
        #save only the required information from original dictionary as the original dictionary is a nested one
        trimmed_response = json.loads(json.dumps(request_response['reply']['endpoints'], indent = 4))
        
        #define list of bad chars
        bad_chars = ["[", "]","'"]    
            
        if trimmed_response:
            return_values = trimmed_response[0]
            for key, value in return_values.items():
                if key in cortex_to_ct_props_map:
                    if value != "" and value != None:
                        #remove bad chars from specific subfields and replace as N.A if empty
                        if key == 'ip' or key == 'users' or key == 'group_name' or key == 'operational_status_description':
                            value = str(value)
                            for i in bad_chars:
                                value = value.replace(i, '')
                            if value == "":
                                value = 'N.A'
                        #convert value to int if time
                        if key == 'last_seen' or key == 'first_seen' or key == 'install_date' or key == 'isolated_date':
                            value = int(value/1000)
                    #replace empty values as 1 second if time related or N.A for others
                    else:
                        if key == 'last_seen' or key == 'first_seen' or key == 'install_date' or key == 'isolated_date':       
                            value = 1
                        else:
                            value = 'N.A'
                    #map the values to the map key
                    properties[cortex_to_ct_props_map[key]] = value
        else:
            response["error"] = "=======>>>>>Cortex: Error " + ip_addr + " Not Found in Cortex Database."
            logging.error(response["error"])
    except:
        response["error"] = "=======>>>>>Cortex: Error resolving IP address: " + ip_addr
        logging.error(response["error"])

    # All responses from scripts must contain the JSON object 'response'.
    # Host property resolve scriptswill need to populate a 'properties' JSON object within the
    # JSON object 'response'. The 'properties' object will be a key, value mapping between the CT
    # property name and the value of the property.
    response["properties"] = properties
    logging.error("=======>>>>>cortext: response returned: {}".format(response))

else:
    response["error"] = "=======>>>>>cortex: No ip address to query."
    logging.error(response["error"])
