# TEST: for Ansible Tower
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

import urllib.request
import logging

logging.info('===>Starting Ansible Tower Test Script')

# Test for V2 API, this does not require authentication
base_url = params['connect_ansible_tower']
test_url = base_url + '/api/v2'

headers = {
    'Content-Type': "application/json",
    'charset': 'utf-8',
    'User-Agent': "FSCT/1.16.2020"
    }

response = {}

try:
    request = urllib.request.Request(test_url, headers=headers)
    resp = urllib.request.urlopen(request, context=ssl_context)
    if resp.getcode() == 200:
        response['succeeded'] = True
        response['result_msg'] = 'Successfully connected to Ansible tower!'
    else:
        response['succeeded'] = False
        response['result_msg'] = 'Could not connect to Ansible Tower...'

except Exception as err:
    response['succeeded'] = False
    logging.info("=======>>>>>Error sending data to Ansible Tower, server returned ===> " + str(err))
    response['troubleshooting'] = str(err)

logging.info('===>Ending Ansible Tower Test Script')
