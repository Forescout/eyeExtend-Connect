import logging
import urllib.request
import json
import re
import datetime

logging.debug("SentinelOne Resolve Script Starting")
# Get app user defined parameters from server
token = params.get("connect_sentinelone_api_token")
server = params.get("connect_sentinelone_server")

# Properties mapping, tied to property.conf
MAPPING = {
    "status": ["activeThreats", "infected", "scanStatus", "scanAbortedAt", "threatRebootRequired"],
    "agent_info": [
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
    ],
    "device_info": [
        "encryptedApplications",
        "lastIpToMgmt",
        "lastLoggedInUserName",
        "machineType",
        "modelName",
        "networkStatus",
        "osUsername",
    ],
}

# Empty dictionaries for storing responses and mapped properties
response = {}
properties = {}


# Subfields method
def getSubFields(json_data, prop_name):
    global sub_fields_response
    sub_fields_response = {}
    for property in MAPPING[prop_name]:
        try:
            sub_fields_response[property] = json_data[property]
        except:
            logging.debug("{} does not exist.".format(property))
    return sub_fields_response


# Time-Date method
def timedate(json_data):
    date = re.search(r"\d+-\d+-\d+", json_data)
    time = re.search(r"\d+:\d+:\d+", json_data)
    time_date = date[0] + " at " + datetime.datetime.strptime(time[0], "%H:%M:%S").strftime("%I:%M:%S %p") + " UTC"
    return time_date


# Should def this in the future, main code
try:
    if "ip" in params:
        ip = str(params["ip"])
        logging.debug("Sending SentinelOne request for " + ip)
        request = urllib.request.Request(
            server
            + "/web/api/v2.1/agents?networkInterfaceInet__contains="
            + ip
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
                logging.debug("There is no data for " + ip)
                pass
            else:
                properties["connect_sentinelone_status"] = getSubFields(req["data"][0], "status")
                if properties["connect_sentinelone_status"]["scanAbortedAt"]:
                    properties["connect_sentinelone_status"]["scanAbortedAt"] = timedate(
                        properties["connect_sentinelone_status"]["scanAbortedAt"]
                    )
                properties["connect_sentinelone_agent_info"] = getSubFields(req["data"][0], "agent_info")
                if properties["connect_sentinelone_agent_info"]["updatedAt"]:
                    properties["connect_sentinelone_agent_info"]["updatedAt"] = timedate(
                        properties["connect_sentinelone_agent_info"]["updatedAt"]
                    )
                if properties["connect_sentinelone_agent_info"]["registeredAt"]:
                    properties["connect_sentinelone_agent_info"]["registeredAt"] = timedate(
                        properties["connect_sentinelone_agent_info"]["registeredAt"]
                    )
                if properties["connect_sentinelone_agent_info"]["lastActiveDate"]:
                    properties["connect_sentinelone_agent_info"]["lastActiveDate"] = timedate(
                        properties["connect_sentinelone_agent_info"]["lastActiveDate"]
                    )
                properties["connect_sentinelone_device_info"] = getSubFields(req["data"][0], "device_info")
                response["properties"] = properties
                # logging.debug("Mapped properties " + response["properties"])
        else:
            response["error"] = "Server response not '200'"
            logging.debug("Server response not '200'")
    else:
        response["error"] = "ForeScout error: No IP address to query the endpoint"
        logging.debug("ForeScout error: No IP address to query the endpoint")

except Exception as e:
    response["error"] = "Unknown Connection Error to SentinelOne"
    error = str(e)
    logging.debug("Error is : " + error)
