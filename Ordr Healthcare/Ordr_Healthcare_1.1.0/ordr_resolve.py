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

base_url = params.get("connect_ordrhealthcare_url")
username = params.get("connect_ordrhealthcare_username")
password = params.get("connect_ordrhealthcare_password")
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
        url = base_url+"/Rest/Devices?ip="+ip+"&include=location,subcategory,asset-info,connectivity-info,clinical-info"
        resp = requests.get(url, headers=headers, auth=(username, password), verify=False, timeout=REQUEST_GET_TIMEOUT)
        if resp.status_code == 200 :
            detail = json.loads(resp.content)
            if len(detail) > 0 :
                if "MacAddress" in detail:
                    properties["connect_ordrhealthcare_macAddress"] = detail['MacAddress']
                    logging.debug("connect_ordrhealthcare_macAddress : " + detail['MacAddress'])
                else:
                    properties["connect_ordrhealthcare_macAddress"] = ""
                if "IpAddress" in detail:
                    properties["connect_ordrhealthcare_ipAddress"] = detail['IpAddress']
                    logging.debug("connect_ordrhealthcare_ipAddress : " + detail['IpAddress'])
                else:
                    properties["connect_ordrhealthcare_ipAddress"] = ""
                if "accessType" in detail:
                    properties["connect_ordrhealthcare_accessType"] = detail['accessType']
                    logging.debug("connect_ordrhealthcare_accessType : " + detail['accessType'])
                else:
                    properties["connect_ordrhealthcare_accessType"] = ""
                if "dhcpHostname" in detail:
                    properties["connect_ordrhealthcare_dhcpHostname"] = detail['dhcpHostname']
                    logging.debug("connect_ordrhealthcare_dhcpHostname : " + detail['dhcpHostname'])
                else:
                    properties["connect_ordrhealthcare_dhcpHostname"] = ""
                if "fqdn" in detail:
                    properties["connect_ordrhealthcare_fqdn"] = detail['fqdn']
                    logging.debug("connect_ordrhealthcare_fqdn : " + detail['fqdn'])
                else:
                    properties["connect_ordrhealthcare_fqdn"] = ""
                if "deviceName" in detail:
                    properties["connect_ordrhealthcare_devicename"] = detail['deviceName']
                    logging.debug("connect_ordrhealthcare_devicename : " + detail['deviceName'])
                else:
                    properties["connect_ordrhealthcare_devicename"] = ""
                if "criticality" in detail:
                    properties["connect_ordrhealthcare_deviceCriticality"] = detail['criticality']
                    logging.debug("connect_ordrhealthcare_deviceCriticality : " + detail['criticality'])
                else:
                    properties["connect_ordrhealthcare_deviceCriticality"] = ""
                if "Group" in detail:
                    properties["connect_ordrhealthcare_group"] = detail['Group']
                    logging.debug("connect_ordrhealthcare_group : " + detail['Group'])
                else:
                    properties["connect_ordrhealthcare_group"] = ""
                if "Profile" in detail:
                    properties["connect_ordrhealthcare_profile"] = detail['Profile']
                    logging.debug("connect_ordrhealthcare_profile : " + detail['Profile'])
                else:
                    properties["connect_ordrhealthcare_profile"] = ""
                if "policyProfileGuid" in detail:
                    policyProfileGuid = detail['policyProfileGuid']
                    policyUrl = base_url+"/Rest/Profiles?types=GROUP_TYPE_POLICY&include=name"
                    policyResp = requests.get(policyUrl, headers=headers, auth=(username, password), verify=False, timeout=REQUEST_GET_TIMEOUT)
                    if policyResp.status_code == 200 :
                        policyProfile = json.loads(policyResp.content)
                        if len(policyProfile) :
                            if "Profiles" in  policyProfile:
                                for item in policyProfile['Profiles']:
                                    if item['guid'] == policyProfileGuid :
                                        properties["connect_ordrhealthcare_policyProfile"] = item['name']
                                        logging.debug("connect_ordrhealthcare_policyProfile : " + item['name'])
                                        break
                            else:
                                logging.debug("connect_ordrhealthcare_policyProfile : Policy Profile not found for device : "+detail['IpAddress'])
                                properties["connect_ordrhealthcare_policyProfile"] = ""
                        else:
                            logging.debug("No Policy Profile defined, Error to Ordr : "+str(policyResp.content))
                            properties["connect_ordrhealthcare_policyProfile"] = ""
                    else:
                        logging.debug("Failed to fetch Policy Profile, Error to Ordr : "+str(policyResp.content))
                        properties["connect_ordrhealthcare_policyProfile"] = ""
                else:
                    properties["connect_ordrhealthcare_policyProfile"] = ""
                if "DeviceDescr" in detail:
                    properties["connect_ordrhealthcare_category"] = detail['DeviceDescr']
                    logging.debug("connect_ordrhealthcare_category : " + detail['DeviceDescr'])
                else:
                    properties["connect_ordrhealthcare_category"] = ""
                if "LongMfgName" in detail:
                    properties["connect_ordrhealthcare_manufacturer"] = detail['LongMfgName']
                    logging.debug("connect_ordrhealthcare_manufacturer : " + detail['LongMfgName'])
                else:
                    properties["connect_ordrhealthcare_manufacturer"] = ""
                if "OsType" in detail:
                    properties["connect_ordrhealthcare_osType"] = detail['OsType']
                    logging.debug("connect_ordrhealthcare_osType : " + detail['OsType'])
                else:
                    properties["connect_ordrhealthcare_osType"] = ""
                if "OsVersion" in detail:
                    properties["connect_ordrhealthcare_osVersion"] = detail['OsVersion']
                    logging.debug("connect_ordrhealthcare_osVersion : " + detail['OsVersion'])
                else:
                    properties["connect_ordrhealthcare_osVersion"] = ""
                if "Vlan" in detail:
                    properties["connect_ordrhealthcare_vlan"] = str(detail['Vlan'])
                    logging.debug("connect_ordrhealthcare_vlan : " + str(detail['Vlan']))
                else:
                    properties["connect_ordrhealthcare_vlan"] = ""
                if "vlanName" in detail:
                    properties["connect_ordrhealthcare_vlanName"] = str(detail['vlanName'])
                    logging.debug("connect_ordrhealthcare_vlanName : " + str(detail['vlanName']))
                else:
                    properties["connect_ordrhealthcare_vlanName"] = ""
                if "ModelNameNo" in detail:
                    properties["connect_ordrhealthcare_modelNo"] = detail['ModelNameNo']
                    logging.debug("connect_ordrhealthcare_modelNo : " + detail['ModelNameNo'])
                else:
                    properties["connect_ordrhealthcare_modelNo"] = ""
                if "SerialNo" in detail:
                    properties["connect_ordrhealthcare_serialNo"] = detail['SerialNo']
                    logging.debug("connect_ordrhealthcare_serialNo : " + detail['SerialNo'])
                else:
                    properties["connect_ordrhealthcare_serialNo"] = ""
                if "RiskState" in detail:
                    properties["connect_ordrhealthcare_riskLevel"] = detail['RiskState']
                    logging.debug("connect_ordrhealthcare_riskLevel : " + detail['RiskState'])
                else:
                    properties["connect_ordrhealthcare_riskLevel"] = ""
                if "riskScore" in detail:
                    properties["connect_ordrhealthcare_riskScore"] = str(detail['riskScore'])
                    logging.debug("connect_ordrhealthcare_riskScore : " + str(detail['riskScore']))
                else:
                    properties["connect_ordrhealthcare_riskScore"] = ""
                if "alarmCount" in detail:
                    properties["connect_ordrhealthcare_alarmCount"] = str(detail['alarmCount'])
                    logging.debug("connect_ordrhealthcare_alarmCount : " + str(detail['alarmCount']))
                else:
                    properties["connect_ordrhealthcare_alarmCount"] = ""
                if "fdaClass" in detail:
                    properties["connect_ordrhealthcare_fdaClass"] = str(detail['fdaClass'])
                    logging.debug("connect_ordrhealthcare_fdaClass : " + str(detail['fdaClass']))
                else:
                    properties["connect_ordrhealthcare_fdaClass"] = ""
                if "hasPhi" in detail:
                    properties["connect_ordrhealthcare_hasPhi"] = str(detail['hasPhi'])
                    logging.debug("connect_ordrhealthcare_hasPhi : " + str(detail['hasPhi']))
                else:
                    properties["connect_ordrhealthcare_hasPhi"] = ""
                if "knownVulnRiskState" in detail:
                    properties["connect_ordrhealthcare_vulnLevel"] = detail['knownVulnRiskState']
                    logging.debug("connect_ordrhealthcare_vulnLevel : " + detail['knownVulnRiskState'])
                else:
                    properties["connect_ordrhealthcare_vulnLevel"] = ""
                if "hasExternalFlows" in detail:
                    properties["connect_ordrhealthcare_internetCommunication"] = detail['hasExternalFlows']
                    logging.debug("connect_ordrhealthcare_internetCommunication : " + detail['hasExternalFlows'])
                else:
                    properties["connect_ordrhealthcare_internetCommunication"] = ""
                if "nwEquipInterface" in detail:
                    properties["connect_ordrhealthcare_nwInterface"] = detail['nwEquipInterface']
                    logging.debug("connect_ordrhealthcare_nwInterface : " + detail['nwEquipInterface'])
                else:
                    properties["connect_ordrhealthcare_nwInterface"] = ""
                if "nwEquipHostname" in detail:
                    properties["connect_ordrhealthcare_nwDeviceName"] = detail['nwEquipHostname']
                    logging.debug("connect_ordrhealthcare_nwDeviceName : " + detail['nwEquipHostname'])
                else:
                    properties["connect_ordrhealthcare_nwDeviceName"] = ""
                if "nwEquipScrapeIp" in detail:
                    properties["connect_ordrhealthcare_nwDeviceIp"] = detail['nwEquipScrapeIp']
                    logging.debug("connect_ordrhealthcare_nwDeviceIp : " + detail['nwEquipScrapeIp'])
                else:
                    properties["connect_ordrhealthcare_nwDeviceIp"] = ""
                if "nwLocation" in detail:
                    properties["connect_ordrhealthcare_nwLocation"] = detail['nwLocation']
                    logging.debug("connect_ordrhealthcare_nwLocation : " + detail['nwLocation'])
                else:
                    properties["connect_ordrhealthcare_nwLocation"] = ""
                if "firstSeen" in detail:
                    properties["connect_ordrhealthcare_firstSeen"] = str(detail['firstSeen'])
                    logging.debug("connect_ordrhealthcare_firstSeen : " + str(detail['firstSeen']))
                else:
                    properties["connect_ordrhealthcare_firstSeen"] = ""
                if "lastSeen" in detail:
                    properties["connect_ordrhealthcare_lastSeen"] = str(detail['lastSeen'])
                    logging.debug("connect_ordrhealthcare_lastSeen : " + str(detail['lastSeen']))
                else:
                    properties["connect_ordrhealthcare_lastSeen"] = ""
                if "clinicalInfo" in detail:
                    if "Clinical Risk" in detail['clinicalInfo']:
                        properties["connect_ordrhealthcare_clinicalRisk"] = detail['clinicalInfo']['Clinical Risk']
                        logging.debug("connect_ordrhealthcare_clinicalRisk : " + detail['clinicalInfo']['Clinical Risk'])
                    else:
                        properties["connect_ordrhealthcare_clinicalRisk"] = ""
                    if "Device Portability" in detail['clinicalInfo']:
                        properties["connect_ordrhealthcare_devicePortability"] = detail['clinicalInfo']['Device Portability']
                        logging.debug("connect_ordrhealthcare_devicePortability : " + detail['clinicalInfo']['Device Portability'])
                    else:
                        properties["connect_ordrhealthcare_devicePortability"] = ""
                    if "FDA Product Code" in detail['clinicalInfo']:
                        properties["connect_ordrhealthcare_fdaProductCode"] = detail['clinicalInfo']['FDA Product Code']
                        logging.debug("connect_ordrhealthcare_fdaProductCode : " + detail['clinicalInfo']['FDA Product Code'])
                    else:
                        properties["connect_ordrhealthcare_fdaProductCode"] = ""
                    if "FDA Product Name" in detail['clinicalInfo']:
                        properties["connect_ordrhealthcare_fdaProductName"] = detail['clinicalInfo']['FDA Product Name']
                        logging.debug("connect_ordrhealthcare_fdaProductName : " + detail['clinicalInfo']['FDA Product Name'])
                    else:
                        properties["connect_ordrhealthcare_fdaProductName"] = ""
                    if "Life Sustaining" in detail['clinicalInfo']:
                        properties["connect_ordrhealthcare_lifeSustaining"] = detail['clinicalInfo']['Life Sustaining']
                        logging.debug("connect_ordrhealthcare_lifeSustaining : " + detail['clinicalInfo']['Life Sustaining'])
                    else:
                        properties["connect_ordrhealthcare_lifeSustaining"] = ""
                    if "Mission Critical" in detail['clinicalInfo']:
                        properties["connect_ordrhealthcare_missionCritical"] = detail['clinicalInfo']['Mission Critical']
                        logging.debug("connect_ordrhealthcare_missionCritical : " + detail['clinicalInfo']['Mission Critical'])
                    else:
                        properties["connect_ordrhealthcare_missionCritical"] = ""
                else:
                    properties["connect_ordrhealthcare_clinicalRisk"] = ""
                    properties["connect_ordrhealthcare_devicePortability"] = ""
                    properties["connect_ordrhealthcare_lifeSustaining"] = ""
                    properties["connect_ordrhealthcare_missionCritical"] = ""
                    properties["connect_ordrhealthcare_fdaProductCode"] = ""
                    properties["connect_ordrhealthcare_fdaProductName"] = ""
                
                properties["connect_ordrhealthcare_blocklistStatus"] = "False"
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
