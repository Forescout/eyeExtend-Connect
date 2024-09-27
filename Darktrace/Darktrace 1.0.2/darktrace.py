import logging
import re
import json

syslog = params.get("connect_syslog_message")

response = {}
properties = {}
actionlog = {}

if syslog:
    logging.debug("***DARKTRACE SYSLOG*** - Syslog message retrieved: {}".format(syslog))

    # Check if the read syslog line is a Darktrace RESPOND Syslog message
    respond_exp = ".*antigena_state_change.*"
    respondlog = re.findall(respond_exp, syslog)

    if respondlog:
        logging.debug("***DARKTRACE SYSLOG*** - 'antigena_state_change' found in log message")

        quarantine_exp = ".*Quarantine.*"
        quarantinelog = re.findall(quarantine_exp,respondlog[0])

        if quarantinelog:
            logging.debug("***DARKTRACE SYSLOG*** - 'Quarantine' key word found in log message")

            # Check if the darktracelog has an acceptable value for the 'action' field
            action_exp ='.*"action": "CREATE".*|.*"action": "CLEAR".*|.*"action": "EXPIRE".*|.*"action": "CONFIRM".*|.*"action": "EXTEND".*|.*"action": "REACTIVATE_CLEARED".*|.*"action": "REACTIVATE_EXPIRED".*'
            actionlog = re.findall(action_exp, quarantinelog[0])

        else:
            logging.debug("***DARKTRACE SYSLOG*** - No valid 'action' found in log message")

    if actionlog:
        # If darktracelog is not empty
        actionlog = actionlog[0]
        logging.debug("***Darktrace SYSLOG*** - Darktrace log matches")

        # Use a regular expression to extract the JSON part
        match = re.search(r'{.*}', actionlog)
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
