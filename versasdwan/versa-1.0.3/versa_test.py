# TEST: Test connection for Versa Director
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

versa_func.debug('Starting Versa Director Test Script')

URL = params.get('connect_versa_director') + ":" + params.get("connect_versa_director_port")
versa_func.debug(URL)
versa_username = params.get('connect_versa_username')
versa_password = params.get('connect_versa_password')
TOKEN = b64encode(bytes(versa_username + ':' + versa_password, "utf-8")).decode("ascii")
response = {}

# Grab the org to verify connection
org = versa_func.versa_get_org(URL, TOKEN, ssl_context)
if org:
    response['succeeded'] = True
    response['result_msg'] = 'Successfully connected to Versa Organization: ' + org
else:
    response['succeeded'] = False
    response['result_msg'] = 'Could NOT connect to Versa Director...'

versa_func.debug('Ending Versa Director Test Script')
