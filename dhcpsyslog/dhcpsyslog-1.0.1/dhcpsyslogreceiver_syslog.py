"""
Copyright © 2023 Forescout Technologies, Inc.

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

syslog = params.get("connect_syslog_message")

response = {}
properties = {}

if syslog:
    logging.debug("***DHCP Receive*** - Syslog message retrieved: {}".format(syslog))
    
    # Check this is a DHCP Syslog message
    exp = ".*DHCPACK\son.*"
    dhcpack = re.search(exp, syslog)

    if dhcpack:

        logging.debug("***DHCP Receive*** - DHCP ACK Syslog Matched")

        exp_ack = ".*\s([1-9][0-9]{0,2}\.[1-9][0-9]{0,2}\.[1-9][0-9]{0,2}\.[1-9][0-9]{0,2})\sto\s(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})).*"
        x = re.findall(exp_ack, syslog)
       
        logging.debug("***DHCP Receive*** - DHCP Syslog: x = {}".format(x[0]))
        
        ip = x[0][0]
        mac = x[0][1].replace(":","")

        logging.debug("***DHCP Receive*** - DHCP match found: {}".format(mac))
        
        response["mac"] = mac
        properties["ip"] = ip
        properties["online"] = True
        properties["connect_dhcpsyslogreceiver_learnt_ip"] = ip
        properties["connect_dhcpsyslogreceiver_learnt_mac"] = mac


    response["properties"] = properties
    
    logging.debug("***DHCP Receive*** - For endpoint at {} , returning properties: {}".format(response["mac"],response["properties"]))

else:
    logging.debug("***DHCP Receive*** - No syslog found")