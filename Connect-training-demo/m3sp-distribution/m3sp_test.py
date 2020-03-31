# Test script for CounterACT
import urllib.request
import json
import logging

logging.info('===>Starting m3sp Test Script')

# Server configuration fields will be available in the 'params' dictionary.
base_url = params['connect_m3sp_url']

headers = {
    'Content-Type': "application/json",
    'charset': 'utf-8',
    'User-Agent': "FSCT/1.16.2020"
    }

request = urllib.request.Request(base_url, headers=headers)
resp = urllib.request.urlopen(request)

# Return the 'response' dictionary, must have a 'succeded' field.
response = {}

if resp.getcode() == 200:
    response['succeeded'] = True
    response['result_msg'] = 'Successfull connected.'
else:
    response['succeeded'] = False
    response['result_msg'] = 'Could not connect to m3sp Server'

logging.info('===>Ending m3sp Test Script')
