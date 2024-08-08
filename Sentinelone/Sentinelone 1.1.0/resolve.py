''' Updated 2024 Jesse Netz (SentinelOne)
**********
- Changed filtering from IP contains to MAC Address to eliminate false matching
- Updated to the most recent SentinelOne Icon
- Extended resolved fields (nearly 50 in total)

**********
MIT License

Copyright (c) 2020 Ryan Kelleher (Welltok)

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

import logging
import urllib.request
import json
import re
import datetime

logging.debug("SentinelOne Resolve Script Starting - jnetz")
# Get app user defined parameters from server
token = params.get("connect_sentinelone_api_token")
server = params.get("connect_sentinelone_server")

try:
    logging.debug("The params mac value is: " + str(params['mac']))
except Exception as e:
    logging.debug("Error: " + str(e))


# Properties mapping, tied to property.conf
MAPPING = {
    "activeThreats",
       "infected",
    "scanStatus",
    "scanAbortedAt",
    "threatRebootRequired",
     "allowRemoteShell",
        "accountName",
        "accountId",
        "id",
        "updatedAt",
        "registeredAt",
        "computerName",
        "groupName",
        "agentVersion",
        "installerType",
        "isActive",
        "isUpToDate",
        "isPendingUninstall",
        "lastActiveDate",
        "agentVersion",
        "externalIp",
        "firstFullModeTime",
        "fullDiskScanLastUpdatedAt",
        "groupId",
        "groupIp",
        "lastSuccessfulScanDate",
        "mitigationMode",
        "mitigationModeSuspicious",
        "rangerVersion",
        "scanFinishedAt",
        "scanStartedAt",
        "showAlertIcon",
        "siteId",
        "siteName",
        "uuid",
        "encryptedApplications",
        "lastIpToMgmt",
        "lastLoggedInUserName",
        "machineType",
        "modelName",
        "networkStatus",
    "osUsername",
    "appsVulnerabilityStatus",
    "coreCount",
    "cpuCount",
    "cpuId",
    "createdAt",
    "detectionState",
    "domain",
    "firewallEnabled",
    "hasContainerizedWorkload",
    "inRemoteShellSession",
    "isDecommissioned",
    "isUninstalled",
    "locationEnabled",
    "locationType",
    "networkQuarantineEnabled",
    "osArch",
    "osName",
    "osRevision",
    "osStartTime",
    "osType",
    "rangerStatus",
    "serialNumber",
    "totalMemory",
}


# Empty dictionaries for storing responses and mapped properties
response = {}
properties = {}


# Subfields method
def getSubFields(json_data):
    sub_fields_response = {}
    for property in MAPPING:
        try:
            sub_fields_response["connect_sentinelone_"+property] = json_data[property]
        except:
            logging.debug("{} does not exist.".format(property))
    logging.debug("subfields: " + json.dumps(sub_fields_response))
    return sub_fields_response


# Time-Date method
def timedate(json_data):
    date = re.search(r"\d+-\d+-\d+", json_data)
    time = re.search(r"\d+:\d+:\d+", json_data)
    time_date = date[0] + " at " + datetime.datetime.strptime(time[0], "%H:%M:%S").strftime("%I:%M:%S %p") + " UTC"
    logging.debug("Altered time/date: " + time_date)
    return time_date

def isoTimeToEpoch(timeStamp):
    # Define the format of the time string
    time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    # Convert the time string to a datetime object
    datetime_object = datetime.datetime.strptime(timeStamp, time_format)

    # Convert the datetime object to a timestamp (epoch)
    epoch_time = int(datetime_object.timestamp())

    logging.debug(f"Epoch Time:{epoch_time}")
    return epoch_time

# Should def this in the future, main code
try:
    if "mac" in params:
        mac = ":".join(params["mac"][i:i + 2] for i in range(0, 12, 2))
        logging.debug(f"Sending SentinelOne request for {mac}")
        request = urllib.request.Request(
            server
            + "/web/api/v2.1/agents?networkInterfacePhysical__contains="
            + mac
            + "&countOnly=false&limit=1&ApiToken="
            + token,
            headers={
                "User-Agent": "FSCT/1.16.2020",
                "Accept": "*/*",
                "Cache-Control": "no-cache",
                "charset": "utf-8",
                "Connection": "keep-alive",
            },
        )
        resp = urllib.request.urlopen(request, timeout=5)
        if resp.status == 200:
            req = json.loads(resp.read())
            if not req["data"]:
                logging.debug(f"There is no data for {mac}")
                pass
            else:
                properties = getSubFields(req["data"][0])

                if properties.get("connect_sentinelone_scanAbortedAt"):
                    properties["connect_sentinelone_scanAbortedAt"] = timedate(properties["connect_sentinelone_scanAbortedAt"])

                if properties.get("connect_sentinelone_updatedAt"):
                    properties["connect_sentinelone_updatedAt"] = timedate(properties["connect_sentinelone_updatedAt"])

                if properties.get("connect_sentinelone_registeredAt"):
                    properties["connect_sentinelone_registeredAt"] = timedate(properties["connect_sentinelone_registeredAt"])

                if properties.get("connect_sentinelone_lastActiveDate"):
                    properties["connect_sentinelone_lastActiveDate"] = timedate(properties["connect_sentinelone_lastActiveDate"])

                if properties.get("connect_sentinelone_firstFullModeTime"):
                    properties["connect_sentinelone_firstFullModeTime"] = timedate(properties["connect_sentinelone_firstFullModeTime"])

                if properties.get("connect_sentinelone_fullDiskScanLastUpdatedAt"):
                    properties["connect_sentinelone_fullDiskScanLastUpdatedAt"] = timedate(properties["connect_sentinelone_fullDiskScanLastUpdatedAt"])

                if properties.get("connect_sentinelone_lastSuccessfulScanDate"):
                    properties["connect_sentinelone_lastSuccessfulScanDate"] = timedate(properties["connect_sentinelone_lastSuccessfulScanDate"])

                if properties.get("connect_sentinelone_scanFinishedAt"):
                    properties["connect_sentinelone_scanFinishedAt"] = timedate(properties["connect_sentinelone_scanFinishedAt"])

                if properties.get("connect_sentinelone_scanStartedAt"):
                    properties["connect_sentinelone_scanStartedAt"] = timedate(properties["connect_sentinelone_scanStartedAt"])

                if properties.get("connect_sentinelone_createdAt"):
                    properties["connect_sentinelone_createdAt"] = timedate(properties["connect_sentinelone_createdAt"])

                if properties.get("connect_sentinelone_osStartTime"):
                    properties["connect_sentinelone_osStartTime"] = timedate(properties["connect_sentinelone_osStartTime"])

                response["properties"] = properties
                # logging.debug("Mapped properties " + response["properties"])
        else:
            response["error"] = "Server response not '200'"
            logging.debug("Server response not '200'")
    else:
        response["error"] = "Forescout error: No MAC address to query the endpoint"
        logging.debug("Forescout error: No MAC address to query the endpoint")

except Exception as e:
    response["error"] = "Unknown Connection Error to SentinelOne"
    error = str(e)
    logging.debug("Error is : " + error)
