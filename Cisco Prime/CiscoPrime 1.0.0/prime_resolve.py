""""
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


# Resolve script for CounterACT
import urllib.request,urllib.error
import base64
import logging
import xml.etree.ElementTree as ET


logging.debug('===>Starting Cisco Prime Resolve Script')
# Defining Variables
resp = None

# Obtaining Global Variables
base_url = params.get("connect_ciscoprime_url")
username = params.get("connect_ciscoprime_username")
password = params.get("connect_ciscoprime_password")
ctx = ssl_context

#--Property Mapping ----------
CiscoPrime_TO_PROPS_MAP = {
       "deviceName":"connect_ciscoprime_deviceName",
       "deviceType":"connect_ciscoprime_deviceType",
        "managementStatus":"connect_ciscoprime_managementStatus",
        "reachability":"connect_ciscoprime_reachability",
        "softwareType":"connect_ciscoprime_softwareType",
        "softwareVersion":"connect_ciscoprime_softwareVersion",
        "adminStatus":"connect_ciscoprime_adminStatus",
        "partNumber":"connect_ciscoprime_partNumber",
        "serialNumber":"connect_ciscoprime_serialNumber",
        "collectionStatus":"connect_ciscoprime_collectionStatus"
}
#------------End of Property Mapping


# Defining Headers and Adding Authentication header-----
headers = {
    'Content-Type': "application/xml",
    'charset': 'utf-8',
    'User-Agent': "FSCT/1.16.2020",
    }
credentials = ('%s:%s' % (username, password))
encoded_credentials = base64.b64encode(credentials.encode('ascii'))
headers['Authorization'] = 'Basic %s' % encoded_credentials.decode("ascii")

#-------------------------End of Headers

response = {}
properties = {}

try:
        if "ip" in params:
            ip = str(params["ip"])
            logging.debug('===>IP address ' + ip + ' found . Sending request')
            request = urllib.request.Request(base_url + "/webacs/api/v4/data/Devices?ipAddress="+ ip  +"&.full=true", headers=headers)
            resp = urllib.request.urlopen(request,context=ctx)
            if resp.getcode() == 200 :
                    xmlTree = ET.parse(resp)
                    root = xmlTree.getroot()
                    if (int(root.attrib['count'])) > 0 :
                        for child in root.iter():
                            if child.tag in CiscoPrime_TO_PROPS_MAP:
                                properties[CiscoPrime_TO_PROPS_MAP[child.tag]] = child.text
                                logging.debug(child.tag + " : " + child.text )

                        response["properties"] = properties
                        logging.debug("Mapping was a success")
                        logging.debug("=======>>>>>Prime: response returned: {}".format(response))
                    else:
                        logging.debug("Error: IP is not found in Cisco Prime")
                        response["error"] = "Error: IP is not found in Cisco Prime"

            else:
                response["error"] = "Connection Error to Cisco Prime "
                logging.debug("Connection Error to Cisco Prime")
        else:
            response["error"] = "No IP address to query the endpoint"
            logging.debug("No IP address to query the endpoint")

except Exception as e:
        response["error"] = "Connection Error to Cisco Prime"
        error = str(e)
        logging.debug("Error is : " + error)

logging.debug('===>End of Cisco Prime Resolve Script')
