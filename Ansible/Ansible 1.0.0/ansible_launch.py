# ACTION: Launch Ansible Tower Job
# Connect Plugin V1.1

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
import urllib.parse
from base64 import b64encode
import logging

logging.info("=======>>>>>Starting Ansible Launch Script.")

# CT will provide a params{} dictionary with the dependent properties you defined in 'properties.conf' & 'system.conf' for each of your App's custom properties.
base_url = params['connect_ansible_tower']
ansible_username = params['connect_ansible_username']
ansible_password = params['connect_ansible_password']
ansible_template_id = params['connect_ansible_template_id']
ansible_extra_vars = params['connect_ansible_extra_vars']
auth_token = b64encode(bytes(ansible_username + ':' + ansible_password, "utf-8")).decode("ascii")
launch_url = base_url + '/api/v2/job_templates/' + ansible_template_id + '/launch/'
extravars = {}
payload = {}
response = {}

# User needs to send keyword = value, 1 per line from CT interface
extravarlines = ansible_extra_vars.splitlines()
for line in extravarlines:
    linesplit = line.split('=')
    keyword = linesplit[0].lstrip().rstrip()
    value = linesplit[1].lstrip().rstrip()
    extravars.update({keyword: value})

payload['extra_vars'] = extravars

# Tower uses basic auth
headers = {
    'Content-Type': "application/json",
    'charset': 'utf-8',
    'User-Agent': "FSCT/7.20.2020",
    'Authorization': 'Basic %s' % auth_token
    }

# ----  ACTION ----
try:
    request = urllib.request.Request(launch_url, headers=headers, data=bytes(json.dumps(payload), encoding="utf-8"))
    resp = urllib.request.urlopen(request, context=ssl_context)
    request_response = json.loads(resp.read())
    logging.info("=======>>>>>Ansible: Tower Response: {}".format(request_response))
    if resp.getcode() == 201:
        response['succeeded'] = True
    else:
        response['succeeded'] = False

except Exception as err:
    response['succeeded'] = False
    logging.info("=======>>>>>Error sending data to Ansible Tower, server returned ===> " + str(err))
    response['troubleshooting'] = str(err)

logging.info("=======>>>>>Ending Ansible Launch Script.")
