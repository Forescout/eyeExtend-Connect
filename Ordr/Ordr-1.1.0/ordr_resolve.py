# Resolve script for CounterACT
import urllib.request,urllib.error
import base64
import logging
import json
import requests

REQUEST_GET_TIMEOUT = 10


logging.debug('===>Starting Ordr Resolve Script')
# Defining Variables
resp = None

# Obtaining Global Variables
base_url = params.get("connect_ordr_url")
username = params.get("connect_ordr_username")
password = params.get("connect_ordr_password")
ctx = ssl_context


# Defining Headers and Adding Authentication header-----
headers = {
    'Content-Type': "application/xml",
    'charset': 'utf-8',
    'User-Agent': "FSCT/1.16.2020",
    'X-external-service': "FORESCOUT",
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
        url = base_url+"/Rest/Devices?ip="+ip+"&include=location,subcategory,asset-info,connectivity-info"
        resp = requests.get(url, headers=headers, auth=(username, password), verify=False, timeout=REQUEST_GET_TIMEOUT)
        if resp.status_code == 200 :
            detail = json.loads(resp.content)
            if len(detail) > 0 :
                if "MacAddress" in detail:
                    properties["connect_ordr_macAddress"] = detail['MacAddress']
                    logging.debug("connect_ordr_macAddress : " + detail['MacAddress'])
                else:
                    properties["connect_ordr_macAddress"] = ""
                if "IpAddress" in detail:
                    properties["connect_ordr_ipAddress"] = detail['IpAddress']
                    logging.debug("connect_ordr_ipAddress : " + detail['IpAddress'])
                else:
                    properties["connect_ordr_ipAddress"] = ""
                if "accessType" in detail:
                    properties["connect_ordr_accessType"] = detail['accessType']
                    logging.debug("connect_ordr_accessType : " + detail['accessType'])
                else:
                    properties["connect_ordr_accessType"] = ""
                if "dhcpHostname" in detail:
                    properties["connect_ordr_dhcpHostname"] = detail['dhcpHostname']
                    logging.debug("connect_ordr_dhcpHostname : " + detail['dhcpHostname'])
                else:
                    properties["connect_ordr_dhcpHostname"] = ""
                if "fqdn" in detail:
                    properties["connect_ordr_fqdn"] = detail['fqdn']
                    logging.debug("connect_ordr_fqdn : " + detail['fqdn'])
                else:
                    properties["connect_ordr_fqdn"] = ""
                if "deviceName" in detail:
                    properties["connect_ordr_devicename"] = detail['deviceName']
                    logging.debug("connect_ordr_devicename : " + detail['deviceName'])
                else:
                    properties["connect_ordr_devicename"] = ""
                if "criticality" in detail:
                    properties["connect_ordr_deviceCriticality"] = detail['criticality']
                    logging.debug("connect_ordr_deviceCriticality : " + detail['criticality'])
                else:
                    properties["connect_ordr_deviceCriticality"] = ""
                if "Group" in detail:
                    properties["connect_ordr_group"] = detail['Group']
                    logging.debug("connect_ordr_group : " + detail['Group'])
                else:
                    properties["connect_ordr_group"] = ""
                if "Profile" in detail:
                    properties["connect_ordr_profile"] = detail['Profile']
                    logging.debug("connect_ordr_profile : " + detail['Profile'])
                else:
                    properties["connect_ordr_profile"] = ""
                if "policyProfileGuid" in detail:
                    policyProfileGuid = detail['policyProfileGuid']
                    #logging.debug("Saurabh=> policyProfileGuid found" + policyProfileGuid)
                    policyUrl = base_url+"/Rest/Profiles?types=GROUP_TYPE_POLICY&include=name"
                    policyResp = requests.get(policyUrl, headers=headers, auth=(username, password), verify=False, timeout=REQUEST_GET_TIMEOUT)
                    if policyResp.status_code == 200 :
                        policyProfile = json.loads(policyResp.content)
                        if len(policyProfile) :
                            if "Profiles" in  policyProfile:
                                for item in policyProfile['Profiles']:
                                    if item['guid'] == policyProfileGuid :
                                        properties["connect_ordr_policyProfile"] = item['name']
                                        logging.debug("connect_ordr_policyProfile : " + item['name'])
                                        break
                            else:
                                logging.debug("connect_ordr_policyProfile : Policy Profile not found for device : "+detail['IpAddress'])
                                properties["connect_ordr_policyProfile"] = ""
                        else:
                            logging.debug("No Policy Profile defined, Error to Ordr : "+str(policyResp.content))
                            properties["connect_ordr_policyProfile"] = ""
                    else:
                        logging.debug("Failed to fetch Policy Profile, Error to Ordr : "+str(policyResp.content))
                        properties["connect_ordr_policyProfile"] = ""
                else:
                    properties["connect_ordr_policyProfile"] = ""
                if "DeviceDescr" in detail:
                    properties["connect_ordr_category"] = detail['DeviceDescr']
                    logging.debug("connect_ordr_category : " + detail['DeviceDescr'])
                else:
                    properties["connect_ordr_category"] = ""
                if "LongMfgName" in detail:
                    properties["connect_ordr_manufacturer"] = detail['LongMfgName']
                    logging.debug("connect_ordr_manufacturer : " + detail['LongMfgName'])
                else:
                    properties["connect_ordr_manufacturer"] = ""
                if "OsType" in detail:
                    properties["connect_ordr_osType"] = detail['OsType']
                    logging.debug("connect_ordr_osType : " + detail['OsType'])
                else:
                    properties["connect_ordr_osType"] = ""
                if "OsVersion" in detail:
                    properties["connect_ordr_osVersion"] = detail['OsVersion']
                    logging.debug("connect_ordr_osVersion : " + detail['OsVersion'])
                else:
                    properties["connect_ordr_osVersion"] = ""
                if "Vlan" in detail:
                    properties["connect_ordr_vlan"] = str(detail['Vlan'])
                    logging.debug("connect_ordr_vlan : " + str(detail['Vlan']))
                else:
                    properties["connect_ordr_vlan"] = ""
                if "vlanName" in detail:
                    properties["connect_ordr_vlanName"] = str(detail['vlanName'])
                    logging.debug("connect_ordr_vlanName : " + str(detail['vlanName']))
                else:
                    properties["connect_ordr_vlanName"] = ""
                if "ModelNameNo" in detail:
                    properties["connect_ordr_modelNo"] = detail['ModelNameNo']
                    logging.debug("connect_ordr_modelNo : " + detail['ModelNameNo'])
                else:
                    properties["connect_ordr_modelNo"] = ""
                if "SerialNo" in detail:
                    properties["connect_ordr_serialNo"] = detail['SerialNo']
                    logging.debug("connect_ordr_serialNo : " + detail['SerialNo'])
                else:
                    properties["connect_ordr_serialNo"] = ""
                if "RiskState" in detail:
                    properties["connect_ordr_riskLevel"] = detail['RiskState']
                    logging.debug("connect_ordr_riskLevel : " + detail['RiskState'])
                else:
                    properties["connect_ordr_riskLevel"] = ""
                if "riskScore" in detail:
                    properties["connect_ordr_riskScore"] = str(detail['riskScore'])
                    logging.debug("connect_ordr_riskScore : " + str(detail['riskScore']))
                else:
                    properties["connect_ordr_riskScore"] = ""
                if "alarmCount" in detail:
                    properties["connect_ordr_alarmCount"] = str(detail['alarmCount'])
                    logging.debug("connect_ordr_alarmCount : " + str(detail['alarmCount']))
                else:
                    properties["connect_ordr_alarmCount"] = ""
                if "knownVulnRiskState" in detail:
                    properties["connect_ordr_vulnLevel"] = detail['knownVulnRiskState']
                    logging.debug("connect_ordr_vulnLevel : " + detail['knownVulnRiskState'])
                else:
                    properties["connect_ordr_vulnLevel"] = ""
                if "hasExternalFlows" in detail:
                    properties["connect_ordr_internetCommunication"] = detail['hasExternalFlows']
                    logging.debug("connect_ordr_internetCommunication : " + detail['hasExternalFlows'])
                else:
                    properties["connect_ordr_internetCommunication"] = ""
                if "nwEquipInterface" in detail:
                    properties["connect_ordr_nwInterface"] = detail['nwEquipInterface']
                    logging.debug("connect_ordr_nwInterface : " + detail['nwEquipInterface'])
                else:
                    properties["connect_ordr_nwInterface"] = ""
                if "nwEquipHostname" in detail:
                    properties["connect_ordr_nwDeviceName"] = detail['nwEquipHostname']
                    logging.debug("connect_ordr_nwDeviceName : " + detail['nwEquipHostname'])
                else:
                    properties["connect_ordr_nwDeviceName"] = ""
                if "nwEquipScrapeIp" in detail:
                    properties["connect_ordr_nwDeviceIp"] = detail['nwEquipScrapeIp']
                    logging.debug("connect_ordr_nwDeviceIp : " + detail['nwEquipScrapeIp'])
                else:
                    properties["connect_ordr_nwDeviceIp"] = ""
                if "nwLocation" in detail:
                    properties["connect_ordr_nwLocation"] = detail['nwLocation']
                    logging.debug("connect_ordr_nwLocation : " + detail['nwLocation'])
                else:
                    properties["connect_ordr_nwLocation"] = ""
                if "firstSeen" in detail:
                    properties["connect_ordr_firstSeen"] = str(detail['firstSeen'])
                    logging.debug("connect_ordr_firstSeen : " + str(detail['firstSeen']))
                else:
                    properties["connect_ordr_firstSeen"] = ""
                if "lastSeen" in detail:
                    properties["connect_ordr_lastSeen"] = str(detail['lastSeen'])
                    logging.debug("connect_ordr_lastSeen : " + str(detail['lastSeen']))
                else:
                    properties["connect_ordr_lastSeen"] = ""
                
                properties["connect_ordr_blocklistStatus"] = "False"
                response["properties"] = properties
                logging.debug("Response : {}".format(response))
                logging.debug("Mapping was a success")
                logging.debug("=======>>>>>Ordr: response returned: {}".format(response))
            else:
                logging.debug("Record not found for give MacAddress")
                response["error"] = "Record not found for give MacAddress"
        else:
            response["error"] = "Connection Error to Ordr : "+str(resp.status_code)
            logging.debug("Connection Error to Ordr : "+str(resp.status_code))
    else:
            response["error"] = "No IP address to query the endpoint"
            logging.debug("No IP address to query the endpoint")
except Exception as e:
    response["error"] = "Connection Error to Ordr in exception : "+str(e)
    error = str(e)
    logging.debug("Error in Exception : " + error)

logging.debug('===>End of Ordr Resolve Script')
