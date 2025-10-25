#from connectproxyserver import ConnectProxyServer, ProxyProtocol
import requests
import xml.etree.ElementTree as ET
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import logging
import json
import re
import random
#from unigy_testdata import *
# Mapping between SampleApp API response fields to CounterACT properties
unigy_to_ct_props_map = {
    "status": "connect_unigy_status"
}


def str2bool(v):
    logging.debug(f"str2bool")
    if isinstance(v, (bool,int, float)):
        return v   
    return v.lower() in ("yes", "true", "t", "1")


# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
#hostname = params["connect_unigy_hostname"] # Server Hostname
#token = params["connect_unigy_token"]  # token



response = {}
properties = {}

logging.debug(f"Unigy resolve")

if "mac" in params:

    try:

        jdata = json.loads(params["connect_unigy_rest_servers"])
        elements = len(jdata['Servers'])
        unique_numbers = random.sample(range(0, elements), elements) 
        unigydata = []
#        for server in jdata['Servers']:
        for i in range (0, elements):    
            item = int(unique_numbers[i])
            server = jdata['Servers'][item]
            unigydata.clear()
            ResponseFound = False
            state = str(server['active']) 
            hostname = str(server['hostname'])
            token = str(server['password'])
            version = str(server['version'])
            certificate = str(server['certificate'])
            cert = str2bool(certificate)
            enablestate = str2bool(state)

            location = str(server['location'])
            logging.debug(f'location is: {location}')            
            logging.debug(f'hostname is: {hostname}')
            logging.debug(f'token is: {token}') 
            logging.debug(f'state is: {str(state)}')
            logging.debug(f'version is: {version}')
            logging.debug(f'certificate is: {str(cert)}')
            if enablestate == False:
                continue                          
            logging.debug(f'mac is: {params["mac"]}')
            mac = params["mac"].upper()
            #### Bluewave Session Request ####

            header = {'Content-Type': 'application/xml','Authorization': 'Basic '+token+'','X-IPCBWAPIVersion': version}
            xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ns1:CreateSession xmlns:ns1="http://www.ipc.com/bw"><ns1:SessionInfo><ns1:ClientType>DATA</ns1:ClientType></ns1:SessionInfo></ns1:CreateSession>"""
            try:
                auth_resolve_response = requests.post(hostname+'/svc/bw/session', data=xml, headers=header, verify=cert)
            except Exception as e:
                logging.debug(f"Connection Timeout or other issue" + str(e))
                continue
            logging.debug(f"Authentication Resolve response code: {auth_resolve_response.status_code}")
            #### Bluewave API authentication ####

            if auth_resolve_response.status_code == 200:
                bwResponseXML = ET.fromstring(auth_resolve_response.content)
                bwToken = bwResponseXML.find(".//{http://www.ipc.com/bw}AuthenticationToken").text
                dataHeaders = {'X-IPCAuthToken': bwToken,'X-IPCBWAPIVersion': version}
            else:
                Error = "Unable to Authenticate to Unigy:"
                response["error"] = Error + hostname
                response["properties"] = properties
                raise ValueError('Wrong HTTP Response:' + Error )

            #### BlueWave API query for turrets configuration ####
            try:
                resolve_response = requests.get(hostname+'/svc/bw/data/inventory/device?querystr=DeviceUUID="'+mac+'"', headers=dataHeaders, verify=cert)
            except Exception as e:
                logging.debug(f"Connection Timeout or other issue" + str(e))
                continue
            logging.debug(f"Resolve response code: {resolve_response.status_code}")
            #### Turret check ####

            if resolve_response.status_code != 200:
                unigydata.append('Failed to get device data')
                logging.debug(f"========>>>>>>" + str(resolve_response))
                continue
            else:
                logging.debug(f"========>>>>>>" + str(resolve_response))
                #FilteredResponse = re.sub( "\\\\n","",str(resolve_response.content))
                namespace = {'ns1' : 'http://www.ipc.com/bw'}
                ResponseXML = ET.fromstring(resolve_response.content)
                Base=".//ns1:"
                FStr = Base  + "ReasonDescription"
                TagValue = ResponseXML.find(FStr, namespace).text
    
                if TagValue == None or "No Device Inventory Data found" in TagValue:
                    logging.debug(f"Aborting loop no device inventory")
                    continue
                if ResponseXML:
                    tags = ["ReasonCode","ReasonDescription", "DeviceRole","ParentInstanceName"]

                    for Tag in tags:
                        FStr = Base + Tag
                        try:
                            TagValue = ResponseXML.find(FStr, namespace).text
                            logging.debug(f"Tag:" + str(Tag) + " TagValue:" + str(TagValue))
                            Present = Tag + ":" +  TagValue
                            unigydata.append(Present)
                        except Exception as e:
                            unigydata.append(f"" + Tag + ":data not found")


                    unigydata.append('BW:'+ hostname)
                    unigydata.append('Success')
                    logging.debug(f"==========>>>>>>>" + str(properties))
                    ResponseFound = True
                    break
                else:
                    unigydata.append('Unable to Decode XML')
                    unigydata.append('Falied')
                    logging.debug(f"==========>>>>>>>" + str(properties))
                ResponseFound = True
        if ResponseFound == False:
            unigydata.append('All REST calls failed')
            unigydata.append('Falied')
        properties[unigy_to_ct_props_map['status']] = unigydata
        response['properties'] = properties
        exit
    except Exception as e:
        logging.debug(f"Error Getting Data" + str(e))
        response["error"] = f"Could not resolve properties: {e}."
        exit
   

