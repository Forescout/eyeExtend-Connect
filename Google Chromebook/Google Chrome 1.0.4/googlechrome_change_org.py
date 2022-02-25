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

import logging
import uuid
import json
import urllib.request
from datetime import datetime, timedelta

# There are five debug levels for python: critical, error, warning, info, debug, which have values 1-5 respectively.
# A user can control the debug level by setting the plugin debug level.
# logging.critical("The server url is {}".format(url))

timeout = 1800  # 30 minutes from now
now = datetime.utcnow()
timeout_datetime = now + timedelta(seconds=timeout)
epoch_time = int((now - datetime(1970, 1, 1)).total_seconds())
epoch_timeout = int((timeout_datetime - datetime(1970, 1, 1)).total_seconds())
jti_val = str(uuid.uuid4())

# Get the token
bearer_token = params["connect_authorization_token"]

# Setup for change of org unit
google_device_id = params["connect_googlechrome_device_id"]

request_header = {
    'Authorization': 'Bearer ' + bearer_token,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


request_url = 'https://www.googleapis.com/admin/directory/v1/customer/my_customer/devices/chromeos/' + google_device_id

body = {
    'deviceId': google_device_id,
    'orgUnitPath': params['googlechrome_org_unit']
}


# For actions, you can specify user inputted parameters that must be defined in the 'property.conf' file. These parameters will take in user input
# from the CounterACT console and will be available in the 'params' dictionary.
request = urllib.request.Request(request_url, headers=request_header, data=bytes(json.dumps(body), encoding="utf-8"), method='PUT')
r = urllib.request.urlopen(request, context=ssl_context)
response = {}

# For actions, the response object must have a field named "succeeded" to denote if the action suceeded or not.
# The field "troubleshooting" is optional to display user defined messages in CounterACT for actions. The field
# "cookie" is available for continuous/cancellable actions to store information for the same action. For this example,
# the cookie stores the id of the user, which will be used to delete the same user when this action is cancelled.
if r.getcode() == 200:
	response["succeeded"] = True
	request_response = json.loads(r.read())
	id = request_response['deviceId']
	logging.debug("The cookie content is {}".format(id))
	#response["cookie"] = id
else:
	response["succeeded"] = False
	response["troubleshooting"] = "Failed action. Response code: {}".format(r.getcode())
