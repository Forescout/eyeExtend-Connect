# LIBRARY: Common Versa Director functions
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


# Supress certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

####################################
# --- Global Functions ---
####################################


# Streamline Logging
def debug(MESSAGE):
    message = "==>" + MESSAGE
    logging.debug(message)


# Web REST calls, returns HTTP response Code and Response
def versa_get_data(URL, TOKEN, CTX):
    session = requests.Session()
    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json",
        'charset': "utf-8",
        'User-Agent': "FSCT/7.17.2020",
        'Authorization': 'Basic %s' % TOKEN
        }

    rjson = {}  # if the response is empty/errors, need to return something

    try:
        with session.get(URL, headers=headers, timeout=90, verify=False) as response:
            code = response.status_code
            rjson = response.json()
            return(code, rjson)
    except Exception as err:
        code = 500
        debug("get_data() - Error sending data to Versa Director, URL Requested ==> " + str(URL) + "| Error Returned: " + str(err))
        return(code, str(err))


# Return the Organization
def versa_get_org(URL, TOKEN, CTX):
    debug('Starting Versa Org Function.')
    debug('Getting Versa Director Version')
    req_url = URL + "/api/operational/system/package-info"
    (code, resp) = versa_get_data(req_url, TOKEN, CTX)
    if code == 200:
        package = resp['package-info'][0]
        version = int(package["major-version"])
        debug("Versa Director Version returned: " + str(version))
    else:
        debug("get_org() Version - Error, get_data() returned ==> " + resp)
        version = 0
    if version >= 21:
        req_url = URL + "/nextgen/organization/roots"
    else:
        req_url = URL + "/api/config/nms/provider/organizations/organization?format=json&select=name"

    (code, resp) = versa_get_data(req_url, TOKEN, CTX)
    if code == 200:
        if version >= 21:
            org = resp[0]
            debug("Versa Director Organization returned: " + org)
        else:
            oray = resp.get("organization")
            if oray:
                firstorg = oray[0]  # Use the first Org, can there be more than one?
                org = firstorg.get("name")
            else:
                org = str(oray)
            debug("Versa Director Organization returned: " + org)
    else:
        debug("get_org() - Error, get_data() returned ==> " + resp)
        org = ""
    debug("Ending Versa Org Function.")
    return(org)


# Return dict of Appliances
def versa_get_appliances(URL, TOKEN, CTX):
    debug("Starting Versa Get Appliances Function.")

    offset = 0
    limit = 1000

    appliances = []
    url = URL + "/vnms/appliance/appliance/?offset=" + str(offset) + "&limit=" + str(limit)

    (code, resp) = versa_get_data(url, TOKEN, CTX)
    if code == 200:
        numrecords = resp.get("versanms.ApplianceStatusResult").get("totalCount")
        if numrecords:
            # First set of appliance records
            rapp = resp.get("versanms.ApplianceStatusResult").get("appliances")
            for appd in rapp:
                appliances.append({"appliance": appd.get("name", ""), "uuid": appd.get("uuid", ""), "ip": appd.get("ipAddress", ""), "ping-status": appd.get("ping-status", ""), "sync-status": appd.get("sync-status"), "location": appd.get("location", ""), "softwareVersion": appd.get("softwareVersion", ""), "Hardware": appd.get("Hardware", "")})
            # Deal wth paging additional records, untested to date as it requires a large deployment
            offset = offset + limit
            while numrecords > offset:
                url = URL + "/vnms/appliance/appliance/?offset=" + str(offset) + "&limit=" + str(limit)
                (code, resp) = versa_get_data(url, TOKEN, CTX)
                if code == 200:
                    rapp = resp.get("versanms.ApplianceStatusResult").get("appliances")
                    for appd in rapp:
                        appliances.append({"appliance": appd.get("name", ""), "uuid": appd.get("uuid", ""), "ip": appd.get("ipAddress", ""), "ping-status": appd.get("ping-status", ""), "sync-status": appd.get("sync-status"), "location": appd.get("location", ""), "softwareVersion": appd.get("softwareVersion", ""), "Hardware": appd.get("Hardware", "")})
                offset = offset + limit

        debug("Ending Versa Get Appliances Function.")
        return(code, appliances)
    else:
        debug("get_appliances() - Error get_data() returned ==> " + resp)
        return(code, resp)


# Return dict of VRF's
def versa_get_vrf(URL, TOKEN, CTX, appliance):
    debug("Starting Versa Get VRF Function: " + appliance)

    # Seems to be no paging capability for the VRF, setting to a high limit
    offset = 0
    limit = 1000

    vrfs = []
    url = URL + "/api/config/devices/device/" + appliance + "/config/routing-instances/routing-instance?deep&offset=" + str(offset) + "&limit=" + str(limit)
    try:
        (code, resp) = versa_get_data(url, TOKEN, CTX)
    except Exception as err:
        debug("Error sending data to Versa Director, server returned: " + str(code))
    if code == 200:
        rvrfs = resp.get("routing-instance")
        for vrfd in rvrfs:
            if vrfd.get("instance-type", "") == "vrf":
                vrfs.append({"appliance": appliance, "vrf": vrfd.get("name", "")})

    else:
        debug("Error sending data to Versa Director, server returned: " + str(code))
        return(code, resp)

    debug("Ending Versa Get VRF Function: " + appliance)
    return(code, vrfs)


# Discover endpoints both Appliances and from the ARP tables
def versa_discover(URL, TOKEN, CTX, applonly, org, appliance):

    # Seems to be no paging capability for the ARP Table, setting to a high limit
    limit = 1000

    endpoints = []

    # Create Appliance endpoints

    debug("Starting Versa Discover Endpoint For: " + appliance["appliance"])
    endpoint = {}
    properties = {}
    endpoint["ip"] = appliance["ip"]
    properties["connect_versa_appliance"] = True
    properties["connect_versa_appliance_location"] = (appliance["location"]).strip()
    properties["connect_versa_appliance_uuid"] = appliance["uuid"]
    properties["connect_versa_appliance_pingstatus"] = appliance["ping-status"]
    properties["connect_versa_appliance_syncstatus"] = appliance["sync-status"]
    properties["connect_versa_appliance_softwareversion"] = appliance["softwareVersion"]
    # this is a composite field that can be set to null if there is no hardware info for the appliance
    # different versions of Versa return different hardware fields the "keys_to_extract" is a subset of the hardware fields
    if appliance["Hardware"]:
        keys_to_extract = ["model", "cpuCores", "memory", "freeMemory", "diskSize", "freeDisk", "lpm", "fanless", "intelQuickAssistAcceleration", "manufacturer", "serialNo", "cpuModel", "cpuCount", "interfaceCount", "packageName", "sku"]
        AppHardware = appliance["Hardware"]
        AppHardware_subset = {key: AppHardware[key] for key in keys_to_extract}
        properties["connect_versa_appliance_hardware"] = AppHardware_subset
    endpoint["properties"] = properties
    endpoints.append(endpoint)

    # Get VRF's and ARP for the appliance if appliance only is not selected
    if applonly == "false":
        (code, vrfs) = versa_get_vrf(URL, TOKEN, CTX, appliance["appliance"])
        if code == 200:
            # Create Endpoints from ARP entries
            uuid = appliance.get("uuid", "")
            url = URL + "/vnms/dashboard/appliance/" + appliance["appliance"] + "/pageable_arp?orgName=" + org + "&limit=" + str(limit)
            # url = URL + "/api/operational/devices/device/" + appliance["appliance"] + "/live-status/arp/all"
            (code, resp) = versa_get_data(url, TOKEN, CTX)
            if (code == 202 or code == 200):
                code = 200  # always wants 200 on exit
                arpt = resp.get("collection", {}).get("arp")   # if the VRF has no ARP entries, this can be empty
                vrflist = []
                for rec in vrfs:
                    vrf = rec.get("vrf", "")
                    debug("versa_discover() - VRF: " + vrf)
                    vrflist.append(vrf)
                arpt = (arp for arp in arpt if ((arp["routing-instance"] in vrflist) and (arp["hwaddr"]!="00:00:00:00:00:00")))
                if arpt:
                    for arp in arpt:
                        endpoint = {}
                        properties = {}
                        # Internal mac for CT needs any : or - removed
                        mac_raw = arp.get("hwaddr", "")
                        mac = "".join(mac_raw.split(":"))
                        endpoint["mac"] = mac
                        endpoint["ip"] = arp.get("ip", "")
                        properties["connect_versa_appliance"] = False
                        properties["connect_versa_appliance_name"] = appliance["appliance"]
                        properties["connect_versa_appliance_location"] = (appliance["location"]).strip()
                        properties["connect_versa_vrf_name"] = arp["routing-instance"]
                        properties["connect_versa_arp_interface"] = arp["interface"]
                        endpoint["properties"] = properties
                        debug("Endpoint For " + appliance["appliance"] + ": " + mac + " - " + endpoint["ip"])
                        endpoints.append(endpoint)

            else:
                if "Expecting value:" in resp:
                    code = 200  # Continue if APR table is empty
                    debug("versa_discover() - Info: ARP Table Empty: " + appliance["appliance"])
                else:
                    debug("versa_discover() - Error getting ARP Tables: " + appliance["appliance"])

    else:
        debug("versa_discover() - Skipping ARP: " + appliance["appliance"])
    return(endpoints)
    debug("Ending Versa Discover Endpoint Function.")
