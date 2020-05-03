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
# Test script for ManageEngine Patch Management Server
logging.info('===>Starting ManageEngine Test Script...')

# Convert the password to base64 format..
mepm_pass64 = str(base64.b64encode(params['connect_manageenginepm_password'].encode('ascii')))
mepm_pass = mepm_pass64[2:-1]

# CT will provide a params{} dictionary with the dependent properties you defined in 'properties.conf' & 'ssytem.conf' for each of your App's custom properties.
base_url = params['connect_manageenginepm_url']

payload = {
	'username' : params['connect_manageenginepm_username'],
	'password' : mepm_pass,
	'auth_type' : 'local_authentication'
	}

headers = {
	'Content-Type': "application/json",
	'charset': 'utf-8',
	'User-Agent': "FSCT/1.16.2020"
	}

# Return the 'response' dictionary, must have a 'succeeded' field.
response = {}
request = urllib.request.Request(base_url, headers=headers)

try:
	resp = urllib.request.urlopen(request, context=ssl_context)

	# Return the 'response' dictionary, must have a 'succeeded' field.
	response = {}

	# Authenticate
	request = urllib.request.Request(base_url + '/1.0/desktop/authentication', headers=headers, data=bytes(json.dumps(payload), encoding="utf-8"))
	try:
		resp = urllib.request.urlopen(request, context=ssl_context)
		jwt_token = json.loads(resp.read())['status']
 
		if jwt_token!='error':
			response['succeeded'] = True
			response['result_msg'] = 'Successfully connected to ManageEngine server.'
			logging.info('=======>>>>>mepm: Received a token, successfully connected to ManageEngine server.')
		else:
			response['succeeded'] = False
			response['result_msg'] = 'User credentials appears to be incorrect. Please try again or use a different user name/password.'
			logging.info('Test failed - authentication error..\n=======>>>>>mepm: ERROR Authenticating to Server!')
	except:
			response['succeeded'] = False
			response['result_msg'] = 'User credentials appears to be incorrect. Please try again or use a different user name/password.'
			logging.info('Test failed - authentication error..\n=======>>>>>mepm: ERROR Authenticating to Server!')		
except:
	response['succeeded'] = False
	response['result_msg'] = 'ManageEngine server appears to be unreachable. Please verify hostname/ip and port, and try again.'
	logging.info('Test failed - could not connect to ManageEngine Server')

logging.info('===>Ending ManageEngine Test Script')