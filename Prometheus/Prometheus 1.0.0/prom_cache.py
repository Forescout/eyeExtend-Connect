# TEST: for Prometheus Server
# Connect Plugin V1.2

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

import urllib.request
import logging

prom_functions.debug('Starting Prometheus Server Cache Script')

base_url = params['connect_prometheus_server']
req_url = base_url + "/api/v1/targets"

headers = {
    'Content-Type': "application/json",
    'charset': 'utf-8',
    'User-Agent': "FSCT/10.16.2020"
    }

response = {}
hosts = {}

try:
    request = urllib.request.Request(req_url, headers=headers)
    resp = urllib.request.urlopen(request, context=ssl_context)
    rjson = json.loads(resp.read())
    # Create the host object to check against at runtime
    targets = rjson['data']['activeTargets']

    for i in targets:
        health = i['health']
        scrapeurl = i['scrapeUrl']
        linesplit = scrapeurl.split('//')
        right = linesplit[1]
        left = right.split(':')
        host = left[0]
        right = left[1].split('/')
        port = right[0]
        hosts[host] = port

    if resp.getcode() == 200:
        response['succeeded'] = True
        response["connect_app_instance_cache"] = json.dumps(hosts)
    else:
        response['succeeded'] = False
        response['error'] = "Error Querying Prometheus Server, server returned code => " + str(resp.getcode())

except Exception as err:
    response['succeeded'] = False
    prom_functions.debug("Error Querying Prometheus Server, server returned => " + str(err))
    response['error'] = str(err)

prom_functions.debug('Ending Prometheus Server Cache Script')
