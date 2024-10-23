import logging
import re
import json

syslog = params.get("connect_syslog_message")

response = {}
properties = {}
actions = {"CREATE","CLEAR","EXPIRE","CONFIRM","EXTEND","REACTIVATE_CLEARED","REACTIVATE_EXPIRED"}

if syslog:
    logging.debug("***DARKTRACE SYSLOG*** - Syslog message retrieved: {}".format(syslog))

    jsonregex = '{.*}'
    jsonextract = re.findall(jsonregex,syslog)
    jsonsyslog = json.loads(jsonextract[0])

    # Check if log contains iris-event-type field as it is otherwise not a RESPOND event
    if "iris-event-type" in jsonsyslog:
        logging.debug("***DARKTRACE SYSLOG*** - 'iris-event-type' key word found in log message")
        # Ensure the value for the iris-event-type is "antigena_state_change"
        if jsonsyslog['iris-event-type'] == "antigena_state_change":     
            logging.debug("***DARKTRACE SYSLOG*** - 'iris-event-type' value is antigena_state_change")      
            # Ensure action log is for a NETWORK type event and not something else, e.g. FIREWALL 
            if jsonsyslog['action_family'] == "NETWORK":
                logging.debug("***DARKTRACE SYSLOG*** - 'action_family' value is NETWORK")      
                # Check if Inhibitor contains "quarantine" in it. We lower all the characters to ensure case insensitivity match
                if "quarantine" in jsonsyslog['inhibitor'].lower():
                    logging.debug("***DARKTRACE SYSLOG*** - 'inhibitor' contains QUARANTINE")  
                    # Ensure the action extracted matches one of the expected ones stored in the actions dictionary above                 
                    if jsonsyslog['action'] in actions:
                        logging.debug("***DARKTRACE SYSLOG*** - valid action found")

                        action = jsonsyslog.get('action')
                        deviceIP = jsonsyslog.get('device')['ip']
                        inhibitor = jsonsyslog.get('inhibitor')

                        response["ip"] = deviceIP
                        properties["connect_darktrace_syslog_sourceIP"] = deviceIP
                        properties["connect_darktrace_syslog_action"] = action
                        properties["connect_darktrace_syslog_inhibitor"] = inhibitor

                        response["properties"] = properties

                        logging.debug("***DARKTRACE SYSLOG*** - Returning properties: {}".format(response["properties"]))
                    else:
                        logging.debug("***DARKTRACE SYSLOG*** - no valid action found. Value found: {}".format(jsonsyslog['action']))
                else:
                    logging.debug("***DARKTRACE SYSLOG*** - keyword 'quarantine' not part of the inhibitor field. Value found: {}".format(jsonsyslog['inhibitor']))
            else:
                logging.debug("***DARKTRACE SYSLOG*** - action_family value is not 'NETWORK'. Value found: {}".format(jsonsyslog['action_family']))
        else:
            logging.debug("***DARKTRACE SYSLOG*** - 'iris-event-type' is not set to 'antigena_state_change'. Value found: {} ".format(jsonsyslog['iris-event-type']))
    else:
        logging.debug("***DARKTRACE SYSLOG*** - 'iris-event-type' field not found in log")
                
else:
    logging.debug("***DARKTRACE SYSLOG*** - No syslog found")
