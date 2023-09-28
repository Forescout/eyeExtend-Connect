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

import datetime
import socket
import logging

timetest = params.get("connect_customproperties_time_enabled")
dnstest = params.get("connect_customproperties_dns_enabled")

timeformat = params.get("connect_currenttime_time_format")

response = {}
timeresult = []
result = []
testcomplete = "1"

logging.debug("***Custom Props*** Testing: Time [{}] DNS [{}]".format(timetest,dnstest))

# If enabled, test for setting time
if timetest == "true":

    logging.debug("***Custom Props*** Time test started")
    # Get the current time in UTC
    current_time_utc = datetime.datetime.now(datetime.timezone.utc)
    current_time_utc_string = current_time_utc.strftime("%Y-%m-%d %H:%M:%S")
    timeresult.append("Current time (UTC): {}".format(current_time_utc_string))

    # Convert to epoch time
    epoch_time = str(current_time_utc.timestamp())
    timeresult.append("Epoch time: {}".format(epoch_time))

    if timeformat == "tz_time_format":
        tz_required = params.get("connect_currenttime_custom_tz")
        tz_required_int = int(tz_required)

        # Get the current time in a specific timezone
        timezone = datetime.timedelta(hours=tz_required_int)
        current_time_timezone = current_time_utc + timezone
        current_time_timezone_string = current_time_timezone.strftime("%Y-%m-%d %H:%M:%S")
        timeresult.append("Current time ({} Hours): {}".format(tz_required,current_time_timezone_string))

    if timeresult:
        logging.debug("***Custom Props*** Time test completed successfully, results: [ {} ]".format(timeresult))
        result.append("Time Test Successful")
    else:
        logging.debug("***Custom Props*** Time test failed, results: [ {} ]".format(timeresult))
        testcomplete = "0"
        result.append("!!! Time Test Failed. Review debug logs. !!!")

# If enabled, test for dns resolution
if dnstest == "true":
    logging.debug("***Custom Props*** DNS test started")
    try:
        hostname, _, _ = socket.gethostbyaddr("8.8.8.8")
        parts = hostname.split('.')
        hostname_without_domain = parts[0]
        logging.debug("***Custom Props*** DNS query for 8.8.8.8 returned [ {} ]".format(hostname))
    
        if hostname == "dns.google":
            if hostname_without_domain == "dns":
                logging.debug("***Custom Props*** DNS test completed successfully, results: [ {} , {} ]".format(hostname, hostname_without_domain))
                result.append("DNS Test Successful")
            else:
                logging.debug("***Custom Props*** DNS test failed to strip domain for [ {} ] returned [ {} ]".format(hostname, hostname_without_domain))
                testcomplete = "0"
                result.append("!!! DNS Test Failed. Review debug logs. !!!")
        else:
            logging.debug("***Custom Props*** DNS test failed to resolve correct domain for 8.8.8.8, returned [ {} ]".format(hostname))
            testcomplete = "0"        
            result.append("!!! DNS Test Failed. Review debug logs. !!!")
    
    except socket.herror as e:
        logging.debug("***Custom Props*** DNS query for 8.8.8.8 returned [ {} ]".format(e))

# Update final test result
if testcomplete == "1":
    response["succeeded"] = True
    response["result_msg"] = result
else:
    response["succeeded"] = False
    response["result_msg"] = result
    logging.debug("***Custom Props*** {}".format(response["result_msg"]))