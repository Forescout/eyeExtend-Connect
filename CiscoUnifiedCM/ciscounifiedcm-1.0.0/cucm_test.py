import requests
import xml.etree.ElementTree as ET

# All server configuration fields will be available in the 'params' dictionary.
url = params["connect_cucm_url"] # Server URL
username = params["connect_cucm_username"]  # login
password = params["connect_cucm_password"]  # password

headers = {
    'Content-Type': 'text/xml; charset=utf-8',
    'SOAPAction': 'get'
}

body = """
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
                <soap:Item>*</soap:Item>
            </soap:item>
		</soap:SelectItems>
        <soap:Protocol>Any</soap:Protocol>
        <soap:DownloadStatus>Any</soap:DownloadStatus>
        </soap:CmSelectionCriteria>
        </soap:selectCmDevice>
    </soapenv:Body>
</soapenv:Envelope>
"""

response = {}
response1 = requests.post(url, headers=headers, data=body,auth=(username, password), verify=False)

if response1.status_code == 200:
    response["succeeded"] = True
    response["result_msg"] = "Successfully connected."

else:
    response["succeeded"] = False
    response["result_msg"] = "Could not connect to CUCM URL"

