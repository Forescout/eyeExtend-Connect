"""
Copyright © 2021 Forescout Technologies, Inc.

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

import logging
import re

logging.debug("***** PULSE SECURE LOGGING - BEGIN *****")

syslog = params.get("connect_syslog_message")

response = {}
properties = {}

if syslog:
    logging.debug("Syslog message retrieved: {}".format(syslog))
    
    # Check if this is a Connect or Disconnect message
    exp_state = ".*Session\sended.*"
    disconnect = re.search(exp_state, syslog)

    if disconnect:

        exp_dis = ".*VPN\sTunneling\:\sSession\sended\sfor\suser\s.*\s(\d+\.\d+\.\d+\.\d+).*"
        x = re.findall(exp_dis, syslog)
        
        logging.debug("Pulse Secure VPN Disconnect match found: {}".format(x))
        
        response["ip"] = x[0]
        properties["online"] = False

    else:

        # Check if message contains IVS before Username. If so, filter it out when populating Username property
        exp = ".*\:{2}.*"
        msg_form = re.search(exp, syslog)

        if msg_form:

            exp_conn = ".*\[(\d+\.\d+\.\d+\.\d+)\]\s.*\:(.*)\(.*VPN\sTunneling\:\sSession\sstarted\sfor\suser\s*\(session\:\s(.*)\).*address\s(\d+\.\d+\.\d+\.\d+)\,.*"

            x = re.findall(exp_conn, syslog)
            
            logging.debug("Pulse Secure VPN Connect matches found: {}".format(x))
            
            response["ip"] = x[0][3]
            properties["connect_pulsesecure_source_ip"] = x[0][0]
            properties["connect_pulsesecure_active_username"] = x[0][1]
            properties["connect_pulsesecure_session_id"] = x[0][2]
            properties["online"] = True

        else:

            exp_conn = ".*\[(\d+\.\d+\.\d+\.\d+)\]\s(.*)\(.*VPN\sTunneling\:\sSession\sstarted\sfor\suser\s*\(session\:\s(.*)\).*address\s(\d+\.\d+\.\d+\.\d+)\,.*"
            x = re.findall(exp_conn, syslog)
            
            logging.debug("Pulse Secure VPN Connect matches found: {}".format(x))
            
            response["ip"] = x[0][3]
            properties["connect_pulsesecure_source_ip"] = x[0][0]
            properties["connect_pulsesecure_active_username"] = x[0][1]
            properties["connect_pulsesecure_session_id"] = x[0][2]
            properties["online"] = True

    response["properties"] = properties
    
    logging.debug("For endpoint at {}, returning properties: {}".format(response["ip"],response["properties"]))

else:
    logging.debug("No syslog found")
    
logging.debug("***** PULSE SECURE LOGGING - END *****")