# standalone python code that exercises the m3sp
import urllib.request
import json

base_url = "http://localhost:3000/api"
payload = {
    'username' : 'forescout',
    'password' : '4Scout123'
    }

headers = {
    'Content-Type': "application/json",
    'charset': 'utf-8',
    'User-Agent': "FSCT/1.16.2020"
    }

# Authenticate
request = urllib.request.Request(base_url + '/authenticate', headers=headers, data=bytes(json.dumps(payload), encoding="utf-8"))
resp = urllib.request.urlopen(request)
jwt_token = json.loads(resp.read())['token']
print('Recieved Token: ' + jwt_token)

# Device headers with the authorization token
device_headers = {
    'Content-Type': "application/json",
    'charset': 'utf-8',
    'User-Agent': "FSCT/1.16.2020",
    'Authorization': 'Bearer ' + str(jwt_token)
    }

# Get device information
mac_addr = 'ac87a3163207'    # define a static mac address to test, CT will provide this in the params["mac"]
print('\nGetting Device Information from M3SP for ' + mac_addr)
request = urllib.request.Request(base_url + '/getdevice/' + mac_addr, headers=device_headers)
resp = urllib.request.urlopen(request)
request_response = json.loads(resp.read())
if request_response:
    return_values = request_response[0]
    for key, value in return_values.items():
        print('\t' + key + '=' + value)

# Get malware information
mac_addr = 'c4b301cf8274'    # define a static mac address to test, CT will provide this in the params["mac"]
print('\nGetting Malware Information from M3SP for ' + mac_addr)
request = urllib.request.Request(base_url + '/getmalware/' + mac_addr, headers=device_headers)
resp = urllib.request.urlopen(request)
request_response = json.loads(resp.read())
if request_response:
    return_values = request_response[0]
    for key, value in return_values.items():
        print('\t' + key + '=' + value)

    # if request_response:
    #     return_values = request_response[0]
    #     for key, value in return_values.items():
    #         if key in cylance_to_ct_props_map:
    #             properties[cylance_to_ct_props_map[key]] = value

# ----   ACTION ----
# Send data
mac_addr = 'c4b301cf8275'
device_info = {
    'mac' : mac_addr,
    'department' : 'produce',
    'location' : 'aisle 3'
    }
print('\nSending Information to M3SP for ' + mac_addr)
request = urllib.request.Request(base_url + '/senddata', headers=device_headers, data=bytes(json.dumps(device_info), encoding="utf-8"))
resp = urllib.request.urlopen(request)
request_response = json.loads(resp.read())
