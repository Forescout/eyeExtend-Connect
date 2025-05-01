###############################################################################
# Syslog message parsing script.                                              #
###############################################################################

import re

# Get the message
msg = params.get("connect_syslog_message")

# Prepare response dictionary
response = {}
properties = {}

# Connect/disconnect patterns
pattern_up = re.compile(r'.*"distinguished_name_device_id":"([\da-f]{32})","distinguished_name_ou":"(\S+)","distinguished_name_user":"(\S+)","event_type":"tunnel_established".*"pool_v4_ip":"((?:[0-9]{1,3}\.){3}[0-9]{1,3})".*')
pattern_down = re.compile(r'.*"distinguished_name_user":"(\S+)","event_type":"tunnel_closed".*"pool_v4_ip":"((?:[0-9]{1,3}\.){3}[0-9]{1,3})".*')

if result:= re.match(pattern_up, msg):
    properties['connect_appgatesdp_id'] = result.group(1)
    properties['connect_appgatesdp_idp'] = result.group(2)
    properties['connect_appgatesdp_user'] = result.group(3)
    response['ip'] = result.group(4)

    properties['online'] = True
    response['properties'] = properties

elif result:= re.match(pattern_down, msg):
    response['ip'] = result.group(2)
    properties['online'] = False
    response['properties'] = properties