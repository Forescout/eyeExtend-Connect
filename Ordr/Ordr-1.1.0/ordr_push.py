# Resolve script for CounterACT
import urllib.request,urllib.error
import base64
import logging
import json
import requests

REQUEST_POST_TIMEOUT = 10


logging.debug('===>Starting Ordr Push Script')
# Defining Variables
resp = None

base_url = params.get("connect_ordr_url")
username = params.get("connect_ordr_username")
password = params.get("connect_ordr_password")
ordrPushPolicy = params.get("ordr_push_policy")
pushData = params.get("connect_ordr_push")
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
batchMode = False
itemresponse = {}

try:
    reqBody={
        'messageType': "ResponseFromFSConnectApp",
        'requester': "FSConnectApp",
    }
    forescoutdata=[]
    
    logging.debug(">>>pushData : "+str(pushData))
    
    if pushData:
        if 'endpoints' in vars() or 'endpoints' in globals():
            logging.debug("Endpoints>>> "+str(endpoints))
            batchMode = True
            for host in endpoints:
                logging.debug("Host Info >>> "+str(host))
                data = {}
                itemresponse = {}
                cid = host["correlation_id"]
                if 'ip' in host:
                    data["ip"] = str(host["ip"])
                if 'mac' in host:
                    data["macAddress"] = str(host["mac"])
                    data["id"] = str(host["mac"])
                else:
                    logging.debug("MAC is missing in the host : "+str(host))
                if 'os_classification' in host:
                    data["osClassification"] = str(host["os_classification"])
                if 'va_netfunc' in host:
                    data["nwFunction"] = str(host["va_netfunc"])
                if 'prim_classification' in host:
                    data["primClassification"] = str(host["prim_classification"])
                if 'vendor_classification' in host:
                    data["vendorModel"] = str(host["vendor_classification"])
                if 'mac_vendor_string' in host:
                    data["nicVendor"] = str(host["mac_vendor_string"])
                if 'is_behind_nat' in host:
                    data["isBehindNat"] = str(host["is_behind_nat"])
                if 'dhcp_class' in host:
                    data["dhcpDeviceClass"] = str(host["dhcp_class"])
                if 'dhcp_os' in host:
                    data["dhcpDeviceOs"] = str(host["dhcp_os"])
                if 'dhcp_hostname' in host:
                    data["dhcpHostname"] = str(host["dhcp_hostname"])
                if 'dhcp_domain_name' in host:
                    data["dhcpDomainName"] = str(host["dhcp_domain_name"])
                if 'hostname' in host:
                    data["dnsName"] = str(host["hostname"])
                if 'fingerprint' in host:
                    data["osFingerprint"] = str(host["fingerprint"])
                if 'is_iot' in host:
                    data["isIot"] = str(host["is_iot"])
                if 'online' in host:
                    data["online"] = str(host["online"])
                
                # Setting up Switch Info
                if 'sw_port_multi' in host:
                    data["hostsOfPort"] = str(host["sw_port_multi"])
                if 'sw_ip' in host:
                    data["switchIpFqdn"] = str(host["sw_ip"])
                if 'sw_port_desc' in host:
                    data["switchPortName"] = str(host["sw_port_desc"])
                if 'sw_location' in host:
                    data["switchLocation"] = str(host["sw_location"])
                if 'sw_port_alias' in host:
                    data["switchPortDescr"] = str(host["sw_port_alias"])
                if 'sw_port_vlan' in host:
                    data["switchPortVlan"] = str(host["sw_port_vlan"])
                if 'sw_port_vlan_name' in host:
                    data["switchPortVlanName"] = str(host["sw_port_vlan_name"])
                if 'sw_vendor' in host:
                    data["switchVendor"] = str(host["sw_vendor"])
                if 'sw_hostname' in host:
                    data["switchHostname"] = str(host["sw_hostname"])
                if 'sw_os' in host:
                    data["switchOs"] = str(host["sw_os"])
                if 'sw_voip_port' in host:
                    data["switchPortVoiceDevice"] = str(host["sw_voip_port"])
                if 'sw_port_voice_vlan' in host:
                    data["switchPortVoiceVlan"] = str(host["sw_port_voice_vlan"])
                    
                #Setting up WLAN details
                if 'wifi_ap_name' in host:
                    data["wlanApName"] = str(host["wifi_ap_name"])
                if 'wifi_ip' in host:
                    data["wlanControllerIpFqdn"] = str(host["wifi_ip"])
                if 'wifi_ssid' in host:
                    data["wlanSsid"] = str(host["wifi_ssid"])
                if 'wifi_ap_location' in host:
                    data["wlanApLocation"] = str(host["wifi_ap_location"])
                if 'wifi_client_vlan' in host:
                    data["wlanClientVlan"] = str(host["wifi_client_vlan"])
                if 'wifi_vendor' in host:
                    data["wlanDeviceVendor"] = str(host["wifi_vendor"])
                if 'wireless_netfunc_os' in host:
                    data["wlanDeviceSoftware"] = str(host["wireless_netfunc_os"])
                if 'wifi_client_auth' in host:
                    data["wlanAuthMethod"] = str(host["wifi_client_auth"])
                if 'wifi_client_role' in host:
                    data["wlanClientRole"] = str(host["wifi_client_role"])
                if 'wifi_client_hostname' in host:
                    data["wlanClientUsername"] = str(host["wifi_client_hostname"])
                if 'wifi_bssid' in host:
                    data["wlanBssid"] = str(host["wifi_bssid"])
                if 'wifi_client_status' in host:
                    data["wlanConnStatus"] = str(host["wifi_client_status"])
                
                #Setting up other details
                if 'nmap_banner7' in host:
                    data["nmapBanner"] = str(host["nmap_banner7"])
                if 'guest_corporate_state' in host:
                    data["guestCorporateState"] = str(host["guest_corporate_state"])
                if 'in-group' in host:
                    data["inGroup"] = str(host["in-group"])
                if 'compliance_state' in host:
                    data["complianceState"] = str(host["compliance_state"])
                if 'device_role' in host:
                    data["deviceRole"] = str(host["device_role"])
                itemresponse["succeeded"] = True
                response[cid] = itemresponse
                
                forescoutdata.append(data)
        else:
            logging.debug("Params >>>> "+str(params))
            data = {}
            if 'ip' in params:
                data["ip"] = str(params["ip"])
            if 'mac' in params:
                data["macAddress"] = str(params["mac"])
                data["id"] = str(params["mac"])
            else:
                logging.debug("MAC is missing in the host : "+str(host))
            if 'os_classification' in params:
                data["osClassification"] = str(params["os_classification"])
            if 'va_netfunc' in params:
                data["nwFunction"] = str(params["va_netfunc"])
            if 'prim_classification' in params:
                data["primClassification"] = str(params["prim_classification"])
            if 'vendor_classification' in params:
                data["vendorModel"] = str(params["vendor_classification"])
            if 'mac_vendor_string' in params:
                data["nicVendor"] = str(params["mac_vendor_string"])
            if 'is_behind_nat' in params:
                data["isBehindNat"] = str(params["is_behind_nat"])
            if 'dhcp_class' in params:
                data["dhcpDeviceClass"] = str(params["dhcp_class"])
            if 'dhcp_os' in params:
                data["dhcpDeviceOs"] = str(params["dhcp_os"])
            if 'dhcp_hostname' in params:
                data["dhcpHostname"] = str(params["dhcp_hostname"])
            if 'dhcp_domain_name' in params:
                data["dhcpDomainName"] = str(params["dhcp_domain_name"])
            if 'hostname' in params:
                data["dnsName"] = str(params["hostname"])
            if 'fingerprint' in params:
                data["osFingerprint"] = str(params["fingerprint"])
            if 'is_iot' in params:
                data["isIot"] = str(params["is_iot"])
            if 'online' in params:
                data["online"] = str(params["online"])
            
            # Setting up Switch Info
            if 'sw_port_multi' in params:
                data["hostsOfPort"] = str(params["sw_port_multi"])
            if 'sw_ip' in params:
                data["switchIpFqdn"] = str(params["sw_ip"])
            if 'sw_port_desc' in params:
                data["switchPortName"] = str(params["sw_port_desc"])
            if 'sw_location' in params:
                data["switchLocation"] = str(params["sw_location"])
            if 'sw_port_alias' in params:
                data["switchPortDescr"] = str(params["sw_port_alias"])
            if 'sw_port_vlan' in params:
                data["switchPortVlan"] = str(params["sw_port_vlan"])
            if 'sw_port_vlan_name' in params:
                data["switchPortVlanName"] = str(params["sw_port_vlan_name"])
            if 'sw_vendor' in params:
                data["switchVendor"] = str(params["sw_vendor"])
            if 'sw_hostname' in params:
                data["switchHostname"] = str(params["sw_hostname"])
            if 'sw_os' in params:
                data["switchOs"] = str(params["sw_os"])
            if 'sw_voip_port' in params:
                data["switchPortVoiceDevice"] = str(params["sw_voip_port"])
            if 'sw_port_voice_vlan' in params:
                data["switchPortVoiceVlan"] = str(params["sw_port_voice_vlan"])
                
            #Setting up WLAN details
            if 'wifi_ap_name' in params:
                data["wlanApName"] = str(params["wifi_ap_name"])
            if 'wifi_ip' in params:
                data["wlanControllerIpFqdn"] = str(params["wifi_ip"])
            if 'wifi_ssid' in params:
                data["wlanSsid"] = str(params["wifi_ssid"])
            if 'wifi_ap_location' in params:
                data["wlanApLocation"] = str(params["wifi_ap_location"])
            if 'wifi_client_vlan' in params:
                data["wlanClientVlan"] = str(params["wifi_client_vlan"])
            if 'wifi_vendor' in params:
                data["wlanDeviceVendor"] = str(params["wifi_vendor"])
            if 'wireless_netfunc_os' in params:
                data["wlanDeviceSoftware"] = str(params["wireless_netfunc_os"])
            if 'wifi_client_auth' in params:
                data["wlanAuthMethod"] = str(params["wifi_client_auth"])
            if 'wifi_client_role' in params:
                data["wlanClientRole"] = str(params["wifi_client_role"])
            if 'wifi_client_hostname' in params:
                data["wlanClientUsername"] = str(params["wifi_client_hostname"])
            if 'wifi_bssid' in params:
                data["wlanBssid"] = str(params["wifi_bssid"])
            if 'wifi_client_status' in params:
                data["wlanConnStatus"] = str(params["wifi_client_status"])
            
            #Setting up other details
            if 'nmap_banner7' in params:
                data["nmapBanner"] = str(params["nmap_banner7"])
            if 'guest_corporate_state' in params:
                data["guestCorporateState"] = str(params["guest_corporate_state"])
            if 'in-group' in params:
                data["inGroup"] = str(params["in-group"])
            if 'compliance_state' in params:
                data["complianceState"] = str(params["compliance_state"])
            if 'device_role' in params:
                data["deviceRole"] = str(params["device_role"])
                
            forescoutdata.append(data)
        
        reqBody["forescoutdata"] = forescoutdata     
        url = base_url+"/Rest/Relay"
        logging.debug('===>Sending request POST request with req-body : '+str(reqBody))
        resp = requests.post(url, headers=headers, json=reqBody, auth=(username, password), verify=False, timeout=REQUEST_POST_TIMEOUT)
        if resp.status_code == 202 :
            if batchMode:
                response["succeeded"] = True
            else:
                response["properties"] = properties
        else:
            logging.debug("Connection Error to Ordr : "+str(resp.status_code))
            if batchMode:
                itemresponse["error"] = "Connection Error to Ordr : "+str(resp.status_code)
                response["succeeded"] = True
            else:
                response["error"] = "Connection Error to Ordr : "+str(resp.status_code)
    else:
        logging.debug("Push Data not cofigured, Skipping to invoke Ordr API to push data")
except Exception as e:
    if batchMode:
        itemresponse["error"] = "Connection Error to Ordr in exception : "+str(e)
        response["default_response"] = itemresponse
    else:
        response["error"] = "Connection Error to Ordr in exception : "+str(e)
    error = str(e)
    logging.debug("Error in Exception : " + error)

logging.debug('===>End of Ordr Push Script')
