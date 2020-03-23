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
# v1.0.0 Azure Active Directory Resolve
# Keith Gilbert
from urllib import request, parse

# Values system.conf passed to params
tenant_id = params["connect_azuread_tenant_id"]
client_id = params["connect_azuread_client_app_id"]
client_secret = params["connect_azuread_access_key"]

# Azure Graph API login URL
login_url_start = "https://login.microsoftonline.com/"
login_url_end = "/oauth2/v2.0/token"
graph_url = "https://graph.microsoft.com/.default"
login_url = login_url_start + tenant_id + login_url_end
raw = {"client_id": client_id, "client_secret": client_secret,  "scope": graph_url,  "grant_type": "client_credentials"}

# Get bearer access_token
data = parse.urlencode(raw).encode()
req = request.Request(login_url, data=data)
resp = request.urlopen(req, context=ssl_context)
logging.debug("response code: " + str(resp.getcode()))
json_resp = json.loads(resp.read())

response = {}
if resp.getcode() == 200:
    response["token"] = json_resp['access_token']
else:
    response["token"] = ""
