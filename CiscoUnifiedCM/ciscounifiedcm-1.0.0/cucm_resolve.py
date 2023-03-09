from connectproxyserver import ConnectProxyServer, ProxyProtocol
import requests
import xml.etree.ElementTree as ET
import logging
import json
# Mapping between SampleApp API response fields to CounterACT properties
cucm_to_ct_props_map = {
	"status": "connect_cucm_status",
}

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params["connect_cucm_url"] # Server URL
username = params["connect_cucm_username"]  # login
password = params["connect_cucm_password"]  # password

response = {}
properties = {}
logging.debug("CUCM resolve")

if "ip" in params:
	logging.debug(f'ip is: {params["ip"]}')
	ip = params["ip"]
	headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "get"}
	body = f"""
	<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' xmlns:soap='http://schemas.cisco.com/ast/soap'>
	    <soapenv:Header/>
	    <soapenv:Body>
	        <soap:selectCmDevice>
	        <soap:StateInfo></soap:StateInfo>
	        <soap:CmSelectionCriteria>
	        <soap:MaxReturnedDevices>100</soap:MaxReturnedDevices>
	        <soap:DeviceClass>Any</soap:DeviceClass>
	        <soap:Model>255</soap:Model>
	        <soap:Status>Any</soap:Status>
	        <soap:NodeName></soap:NodeName>
	        <soap:SelectBy>IPV4Address</soap:SelectBy>
	        <soap:SelectItems>
	            <soap:item>
	                <soap:Item>{ip}</soap:Item>
	            </soap:item>
			</soap:SelectItems>
	        <soap:Protocol>Any</soap:Protocol>
	        <soap:DownloadStatus>Any</soap:DownloadStatus>
	        </soap:CmSelectionCriteria>
	        </soap:selectCmDevice>
	    </soapenv:Body>
	</soapenv:Envelope>
	"""
	try:
		resolve_response = requests.post(url, headers=headers, data=body, auth=(username, password), verify=False)
		logging.debug(f"Resolve response code: {resolve_response.status_code}")
		if 200 == resolve_response.status_code:
			root = ET.fromstring(resolve_response.text)
			ns = {'ns1': 'http://schemas.cisco.com/ast/soap'}
			resolve_response = root.find(".//ns1:Status", ns).text
			logging.debug(f"Resolve response text: {resolve_response}")

					# """
					# # All responses from scripts must contain the JSON object 'response'. Host property resolve scripts will
					# need to populate a 'properties' JSON object within the JSON object 'response'. The 'properties' object will
					# be a key, value mapping between the CounterACT property name and the value of the property
					# """

			if resolve_response:
				properties[cucm_to_ct_props_map['status']] = resolve_response
				logging.info("==========>>>>>>>" + json.dumps(properties))

			else:
				response["error"] = "VoIP not registered in CUCM"
			response["properties"] = properties
			logging.info("========>>>>>>" + json.dumps(response))
	except Exception as e:
		response["error"] = f"Could not resolve properties: {e}."
