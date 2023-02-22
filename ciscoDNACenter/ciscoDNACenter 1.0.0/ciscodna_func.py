# LIBRARY: Common Cisco DNA Center functions
# Connect Plugin V1.6

"""
Copyright @ 2020 Forescout Technologies, Inc.

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

import requests
import json
import logging
import ssl
import urllib3
import time


# Supress certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

####################################
# --- Global Functions ---
####################################


# Streamline Logging
def debug(MESSAGE):
    message = "==>" + MESSAGE
    logging.debug(message)


# Web REST calls, Login and retrieve session
def ciscodna_login(URL, encodedData, CTX):
    login_url = URL + "/dna/system/api/v1/auth/token"
    payload = {}
    headers = {
        #'Content-Type': "application/json",
        #'Accept': "application/json",
        #'charset': "utf-8",
        #'User-Agent': "FSCT/7.17.2020",
        'Authorization': 'Basic %s' % encodedData
        }
    rjson = {}  # if the response is empty/errors, need to return something
    try:
        with requests.request("POST", login_url, headers=headers, data = payload, timeout=90, verify=False) as response:
            code = response.status_code
            rjson = response.json()
            token = rjson['Token']
            return(code, token)
    except Exception as err:
        code = 500
        debug("get_data() - Error logging in to Cisco DNA Center, URL Requested ==> " + str(URL) + "| Error Returned: " + str(err))
        return(code, str(err))

# Web REST calls, returns HTTP response Code and Response
def ciscodna_get_data(URL, TOKEN, CTX):
    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json",
        'charset': "utf-8",
        'User-Agent': "FSCT/7.17.2020",
        'X-Auth-Token': '%s' % TOKEN
        }
    rjson = {}  # if the response is empty/errors, need to return something
    payload = {}
    try:
        with requests.request("GET", URL, headers=headers, data = payload, timeout=90, verify=False) as response:
            code = response.status_code
            rjson = response.json()
            return(code, rjson)
    except Exception as err:
        code = 500
        debug("get_data() - Error sending data to Cisco DNA Center, URL Requested ==> " + str(URL) + "| Error Returned: " + str(err))
        return(code, str(err))

# Get Wireless Sensors from Cisco DNA Center
def ciscodna_get_wireless_sensors(URL, TOKEN, CTX):
    debug('Starting Cisco DNA Center wireless Sensor Function.')
    debug('Getting Cisco DNA Center wireless Sensors')
    req_url = URL + "/dna/intent/api/v1/sensor"
    endpoints = []
    (code, resp) = ciscodna_get_data(req_url, TOKEN, CTX)
    if code == 200:
        allwirelesssensors = resp.get("response")
        onlysensors = [wirelesssensor for wirelesssensor in allwirelesssensors if wirelesssensor['type'] != 'AP_AS_SENSOR']
        for sensor in onlysensors:
            endpoint = {}
            properties = {}
            epochtime = (sensor['lastSeen']/1000)
            endpoint["ip"] = sensor['ipAddress']
            endpoint["mac"] = (sensor['ethernetMacAddress']).replace(':', '')
            properties["connect_ciscodna_sensor_name"] = str(sensor['name'])
            properties["connect_ciscodna_sensor_status"] = str(sensor['status'])
            properties["connect_ciscodna_sensor_version"] = str(sensor['version'])
            properties["connect_ciscodna_sensor_backhaultype"] = str(sensor['backhaulType'])
            properties["connect_ciscodna_sensor_lastseen"] = str(round(epochtime))
            properties["connect_ciscodna_sensor_serialnumber"] = str(sensor['serialNumber'])
            endpoint["properties"] = properties
            debug("Endpoint Cisco DNA wireless sensor " + endpoint["ip"] + " - " + endpoint["mac"])
            
            endpoints.append(endpoint)
        debug("Cisco DNA Center Sensors returned: " + str(endpoints))
    else:
        debug("ciscodna_get_wireless_sensors() - Error, get_data() returned ==> " + allwirelesssensors)
        version = 0
    
    debug("Ending Cisco DNA Center wireless Sensor Function.")
    return(code, endpoints)