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
import uuid
import urllib.request, urllib.error, urllib.parse

def get_str_timestamp(time_timestamp):
	temp_str = datetime.datetime.fromtimestamp(int(time_timestamp)/1000)  # using the local timezone
	return temp_str.strftime("%Y-%m-%d %H:%M:%S")


logging.info("=======>>>>>Starting ManageEngine resolve Script.")

# mapping between our App properties and the CT internal properties
mepm_to_ct_props_map = {
	"resource_health_status": "connect_manageenginepm_rhs",
	"service_pack": "connect_manageenginepm_sp",
	"branch_office_name": "connect_manageenginepm_branch_office_name",
	"os_name": "connect_manageenginepm_os_name",
	"scan_status": "connect_manageenginepm_scan_status"
}

response = {}
properties = {}

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

# Authenticate
try:
	request = urllib.request.Request(base_url + '/1.0/desktop/authentication', headers=headers, data=bytes(json.dumps(payload), encoding="utf-8"))
	resp = urllib.request.urlopen(request, context=ssl_context)
	jwt_token = json.loads(resp.read())['message_response']['authentication']['auth_data']['auth_token']
	logging.info('=======>>>>>mepm: Received Token: ' + jwt_token)
except:
	logging.info('=======>>>>>mepm: ERROR Authenticating to Server!')

# Device headers with the authorization token
device_headers = {
	'Content-Type': "application/json",
	'charset': 'utf-8',
	'User-Agent': "FSCT/1.16.2020",
	'Authorization': '' + str(jwt_token)
	}

# CT will provide a params{} dictionary with the dependent properties you defined in 'properties.conf' for each of your App's custom properties.
logging.info("=======>>>>>mepm: parameters supplied by CT: {}".format(params))

# Get info on the passed resource id from server
if "script_result.f35e875fc87aa0a8a52c7516dc30e49a" in params:
	resid = params["script_result.f35e875fc87aa0a8a52c7516dc30e49a"]
	logging.info("=======>>>>>mepm: Resolving resource ID: " + resid)
	
	# Get device information
	try:
		request = urllib.request.Request(base_url + '/1.0/patch/allsystems?resid=' + resid, headers=device_headers)
		resp = urllib.request.urlopen(request, context=ssl_context)
		request_response = json.loads(resp.read())
		return_values = request_response['message_response']['allsystems'][0]
		properties['connect_manageenginepm_last_successful_scan'] = get_str_timestamp(return_values["last_successful_scan"])
		properties['connect_manageenginepm_agent_last_contact_time'] = get_str_timestamp(return_values["agent_last_contact_time"])  
		properties[mepm_to_ct_props_map["resource_health_status"]] = return_values["resource_health_status"]
		properties[mepm_to_ct_props_map["service_pack"]] = return_values["service_pack"]
		properties[mepm_to_ct_props_map["branch_office_name"]] = return_values["branch_office_name"]
		properties[mepm_to_ct_props_map["os_name"]] = return_values["os_name"]
		properties[mepm_to_ct_props_map["scan_status"]] = return_values["scan_status"]

	except:
		response["error"] = "=======>>>>>mepm: Error resolving resource ID: " + resid
		logging.info(response["error"])

	# Resolve <Vulnerabilites> property..
	ctr = 0
	vuln_list=''
	logging.info('-----------------START RESOLVING Vulnerability List Property-------------------')
	try:
		request = urllib.request.Request(base_url + '/1.0/patch/systemreport?resid=' + resid, headers=device_headers)
		resp = urllib.request.urlopen(request, context=ssl_context)
		request_response = json.loads(resp.read())
		if request_response:
			return_values = request_response['message_response']['systemreport']
			while ctr < len(return_values): 
				vuln_list = vuln_list+return_values[ctr]['bulletin_id']+': '+return_values[ctr]['patch_description']+'\n'
				ctr=ctr+1
			
			properties['connect_manageenginepm_vulnerabilities'] = vuln_list
				
	except:
		response["error"] = "=======>>>>>mepm: Error resolving COMPOSITE ID: " + resid
		logging.info(response["error"])

  
	response["properties"] = properties
	logging.info("=======>>>>>mepm: response returned: {}".format(response))

else:
	response["error"] = "=======>>>>>mepm: No resource ID to query."
	logging.info(response["error"])
