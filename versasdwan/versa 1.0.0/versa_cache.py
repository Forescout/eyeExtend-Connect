# Cache: App Cache for Versa
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

versa_func.debug('Starting Versa Director Cache Script')

URL = params.get('connect_versa_director') + ":" + params.get("connect_versa_director_port")
versa_username = params.get('connect_versa_username')
versa_password = params.get('connect_versa_password')
TOKEN = b64encode(bytes(versa_username + ':' + versa_password, "utf-8")).decode("ascii")
response = {}
cache = {}

# Cache the Org to start
org = versa_func.versa_get_org(URL, TOKEN, ssl_context)

if org:
    cache["org"] = org
    versa_func.debug(str(cache))
    response['succeeded'] = True
    response["connect_app_instance_cache"] = json.dumps(cache)
else:
    response['succeeded'] = False
    response['error'] = 'Could NOT connect to Versa Director...'

versa_func.debug('Ending Versa Director Cache Script')
