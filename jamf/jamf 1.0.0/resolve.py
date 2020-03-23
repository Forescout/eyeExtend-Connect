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

from urllib.request import HTTPError, URLError

general_map = {
	"name": "connect_jamf_deviceName",
	"id": "connect_jamf_id"
}

composite_map = {
	"hardware": ["total_ram", "os_name", "make", "battery_capacity", "processor_speed", "model", "os_version", "processor_type", "os_build", "number_cores", "processor_architecture", "number_processors"],
	"location": ["real_name", "email_address", "username", "phone_number", "position"],
	"purchasing": ["is_leased", "is_purchased"],
	"general": ["jamf_version", "initial_entry_date_epoch", "last_contact_time_epoch"],
}

def getSubFields(json_data, prop_name):
	sub_fields_response = {}
	for property in composite_map[prop_name]:
		try:
			sub_fields_response[property] = json_data[prop_name][property]
		except:
			logging.debug("{} does not exist.".format(property))
	return sub_fields_response

url = params["connect_jamf_url"]
url += "/JSSResource/computers/"
username = params["connect_jamf_username"] 
password = params["connect_jamf_password"]  
response = {}
if "dhcp_hostname" in params:
	url = url + "name/" + params["dhcp_hostname"]
elif "mac" in params:
	uppercase_mac = params["mac"].upper()
	colon_mac = ":".join(uppercase_mac[i:i+2] for i in range(0,12,2))
	url = url + "macaddress/" + colon_mac
else:
	logging.error("Insufficient information to query.")

logging.info("The URL is: {}".format(url))
request = urllib.request.Request(url)
request.add_header("Authorization", "Basic %s" % jamf_lib.create_auth(username, password))
request.add_header("Accept", "application/json")
try:
	resp = urllib.request.urlopen(request, context=ssl_context)
	request_response = json.loads(resp.read())["computer"]
	logging.debug("The response from Jamf is {}".format(request_response))
	properties = {}
	general = request_response["general"]
	for key in general_map:
		properties[general_map[key]] = general[key]
	properties["connect_jamf_asset_purchasing"] = getSubFields(request_response, "purchasing")
	properties["connect_jamf_user_information"] = getSubFields(request_response, "location")
	general_subfields = getSubFields(request_response, "general")
	try:
		general_subfields["initial_entry_date_epoch"] //= 1000
		general_subfields["last_contact_time_epoch"] //= 1000
	except:
		logging.debug("Response does not have epoch fields.")
	properties["connect_jamf_agent_information"] = general_subfields
	hardware_subfields = getSubFields(request_response, "hardware")
	hardware_subfields["serial_number"] = request_response["general"]["serial_number"]
	properties["connect_jamf_device_details"] = hardware_subfields
	software_installed = []
	for application in request_response["software"]["applications"]:
		software_installed.append(application["name"])
	properties["connect_jamf_software_installed"] = software_installed
	properties["connect_jamf_managed"] = request_response["general"]["remote_management"]["managed"]
	response["properties"] = properties
except HTTPError as e:
	response["error"] = "Could not resolve properties. Response code: {}".format(e.code)
except URLError as e:
	response["error"] = "Could not resolve properties. {}".format(e.reason)
except Exception as e:
	response["error"] = "Could not resolve properties. {}".format(str(e))
