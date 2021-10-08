"""
Copyright © 2021 Forescout Technologies, Inc.

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

import base64
import logging
from datetime import datetime


def get_general_authentication_headers(WO_SERVER_USERNAME, WO_SERVER_PASSWORD, WO_API_KEY):
	logging.debug("Generating general headers for authentication...")
	auth_string = "{}:{}".format(WO_SERVER_USERNAME, WO_SERVER_PASSWORD)
	base64string = base64.b64encode(auth_string.encode('utf-8'))
	header_auth_string = "".join(chr(x) for x in base64string)

	headers = {
	  'Content-Type': 'application/json',
	  'Aw-Tenant-Code': WO_API_KEY,
	  'Authorization': 'Basic ' + header_auth_string
	}
	return(headers)


def get_action_authentication_headers_with_xmlmessage_encoding(WO_SERVER_USERNAME, WO_SERVER_PASSWORD, WO_API_KEY, payload):
	logging.debug("Generating data for actions and headers for authentication...")
	auth_string = "{}:{}".format(WO_SERVER_USERNAME, WO_SERVER_PASSWORD)
	base64string = base64.b64encode(auth_string.encode('utf-8'))
	header_auth_string = "".join(chr(x) for x in base64string)

	headers = {}
	headers['Authorization'] = 'Basic ' + header_auth_string
	headers['Aw-Tenant-Code'] = WO_API_KEY

	# message body headers & data
	logging.debug("XML MessageBody: " + payload)
	data = payload.encode("utf-8")
	headers['Content-Length'] = str(len(payload))
	headers['Content-Type'] = 'text/xml'
	return(headers, data)


def convert_to_epoch(timestamp_str):
	try:
		epoch = int(datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f").timestamp())
		logging.debug('Time string "{}" converted to epoch successfully to {}'.format(timestamp_str, epoch))
	except ValueError as e:
		epoch = None
		logging.debug('Time string is: {} | Error: {} | epoch = None'.format(timestamp_str, e))
	return(epoch)
