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

from urllib import request, parse
from urllib.request import HTTPError, URLError
import json

tenantId = params.get("connect_intune_tenant_id")
appId = params.get("connect_intune_application_id")
username = params.get("connect_intune_user")
password = params.get("connect_intune_password")

# Grab token
ms_login_url = "https://login.microsoftonline.com/"
oauth2_endpoint = "/oauth2/v2.0/token"
token_url = ms_login_url + tenantId + oauth2_endpoint
graph_url = "https://graph.microsoft.com/.default"
raw = {"client_id": appId,
       "username": username,
       "password": password,
       "scope": graph_url,
       "grant_type": "password"}

# Get bearer access_token
data = parse.urlencode(raw).encode()
response = {}
try:
       req = request.Request(token_url, data=data)
       resp = request.urlopen(req, context=ssl_context)
       json_resp = json.loads(resp.read())
       access_token = json_resp['access_token']
       response["succeeded"] = True
       response["token"] = str(access_token)
except HTTPError as e:
    response["succeeded"] = False
    response["error"] = "Could not connect to Intune. Response code: {}".format(e.code)
    response["token"] = ""
except URLError as e:
    response["succeeded"] = False
    response["error"] = "Could not connect to Intune. {}".format(e.reason)
    response["token"] = ""
except Exception as e:
    response["succeeded"] = False
    response["error"] = "Could not connect to Intune. {}".format(str(e))
    response["token"] = ""
