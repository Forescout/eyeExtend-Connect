# POLL: Discover endpoints from Versa Director
# Connect Plugin V1.6

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

from base64 import b64encode
import concurrent.futures
import datetime
import logging
import time

begin_time = datetime.datetime.now()

results = []
endpoints = []

versa_func.debug('Starting Versa Director Poll Script')

URL = params.get('connect_versa_director') + ":" + params.get("connect_versa_director_port")
versa_username = params.get('connect_versa_username')
versa_password = params.get('connect_versa_password')
TOKEN = b64encode(bytes(versa_username + ':' + versa_password, "utf-8")).decode("ascii")
response = {}

# Get Org for Arp request
org = params.get('connect_app_instance_cache')
org = (((org.split(": "))[1]).replace('"', "")).strip("}")

# Set threads for Multi threaded operation
versa_func.debug('Max Threads checked: ' + params.get('connect_versa_maxthread'))

if (params.get('connect_versa_maxthread')) == "true":
    num_workers = None
    versa_func.debug('Max Threads Selected')
else:
    num_workers = params.get('connect_versa_threadnum')
    versa_func.debug('Number of threads used: ' + str(num_workers))

# Discovery only Versa Appliances
if (params.get('connect_versa_applonly')) == "true":
    applonly = "true"
    versa_func.debug('Discovery Versa Appliances Only')
else:
    applonly = "false"

# Get Appliance List
(code, appliances) = versa_func.versa_get_appliances(URL, TOKEN, ssl_context)

# Debug list appliances
versa_func.debug("\n=====  OUTPUT APPLIANCE  =====")
for row in appliances:
    versa_func.debug("appliance: " + row["appliance"])

# Get ARP entries and process Versa appliances
if code == 200:
    versa_func.debug("Appliances Returned Successfully {}".format(appliances))
    # Discover Endpoints
    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
        futures_endpoints = {executor.submit(versa_func.versa_discover, URL, TOKEN, ssl_context, applonly, org, app) for app in appliances}
        for future in concurrent.futures.as_completed(futures_endpoints):
            try:
                results = future.result()
                endpoints.extend(results)
            except Exception as exc:
                versa_func.debug('generated an exception: %s' % (exc))
else:
    versa_func.debug('Error discovering Versa endpoints')
    response["error"] = 'Error discovering Versa endpoints'

response["endpoints"] = endpoints
elapsed_time = (datetime.datetime.now() - begin_time)
versa_func.debug(str(endpoints))
versa_func.debug('Ending Versa Director Poll Script, Polling Time: ' + str(elapsed_time))
