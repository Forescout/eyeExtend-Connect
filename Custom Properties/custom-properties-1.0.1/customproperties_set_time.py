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
import logging

timeformat = params.get("connect_customproperties_time_format")

response = {}
properties = {}
result = []

# Get the current time in UTC
current_time_utc = datetime.datetime.now(datetime.timezone.utc)
current_time_utc_string = current_time_utc.strftime("%Y-%m-%d %H:%M:%S")

# Convert to epoch time
epoch_time = current_time_utc.timestamp()
epoch_time_string = str(current_time_utc.timestamp())

logging.debug("***Custom Props*** Setting time, values retrieved: UTC [ {} ] Epoch [ {} ]".format(current_time_utc_string, epoch_time_string))

if timeformat == "utc_time_format":
    result.append("Current time (UTC): {}".format(current_time_utc_string))
    logging.debug("***Custom Props*** Current time (UTC): {}".format(current_time_utc_string))
    
    properties["connect_customproperties_timestamp_date"] = epoch_time
    properties["connect_customproperties_timestamp_string"] = current_time_utc_string

elif timeformat == "epoch_time_format":
    result.append("Epoch time: {}".format(epoch_time_string))
    logging.debug("***Custom Props*** Epoch time: {}".format(epoch_time_string))
    
    properties["connect_customproperties_timestamp_date"] = epoch_time
    properties["connect_customproperties_timestamp_string"] = epoch_time_string

elif timeformat == "tz_time_format":
    
    tz_required = params.get("connect_customproperties_custom_tz")
    tz_required_int = int(tz_required)

    # Get the current time in a specific timezone
    timezone = datetime.timedelta(hours=tz_required_int)
    current_time_timezone = current_time_utc + timezone
    current_time_timezone_string = current_time_timezone.strftime("%Y-%m-%d %H:%M:%S")
    epoch_time_timezone = current_time_timezone.timestamp()
    result.append("Current time ({} Hours): {}".format(tz_required,current_time_timezone_string))
    logging.debug("***Custom Props*** Current time ({} Hours): {}".format(tz_required,current_time_timezone_string))
    
    properties["connect_customproperties_timestamp_date"] = epoch_time_timezone
    properties["connect_customproperties_timestamp_string"] = current_time_timezone_string

if result:
    response["succeeded"] = True
    response["properties"] = properties
else:
    response["succeeded"] = False
    response["troubleshooting"] = "Failed to set time. Review debug logs."
    logging.debug("***Custom Props*** {}".format(response["troubleshooting"]))