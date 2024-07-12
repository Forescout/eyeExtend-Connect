import logging
import re
import json

syslog = params.get("connect_syslog_message")

response = {}
properties = {}

if syslog:

    logging.debug("***DARKTRACE SYSLOG*** - Syslog message retrieved: {}".format(syslog))

    # Check if the read syslog line is a Darktrace RESPOND Syslog message
    exp = ".*antigena_state_change.*"
    darktracelog = re.findall(exp, syslog)[0]

    if darktracelog:

        logging.debug("***Darktrace SYSLOG*** - Darktrace log matches")

        # Use a regular expression to extract the JSON part
        match = re.search(r'{.*}', darktracelog)
        JSONlog = match.group()

        # Parse the JSON
        parsedLog = json.loads(JSONlog)

        # Extract the values for "action" and "device"
        action = parsedLog.get('action')
        deviceIP = parsedLog.get('device')['ip']
        inhibitor = parsedLog.get('inhibitor')

        response["ip"] = deviceIP
        properties["connect_darktrace_syslog_sourceIP"] = deviceIP
        properties["connect_darktrace_syslog_action"] = action
        properties["connect_darktrace_syslog_inhibitor"] = inhibitor

    response["properties"] = properties

    logging.debug("***DARKTRACE SYSLOG*** - Returning properties: {}".format(response["properties"]))

else:
    logging.debug("***DARKTRACE SYSLOG*** - No syslog found")