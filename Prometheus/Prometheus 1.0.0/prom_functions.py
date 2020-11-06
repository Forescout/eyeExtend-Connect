# LIBRARY: for Prometheus Server
# Connect Plugin V1.2

"""
Copyright © 2020 Forescout Technologies, Inc.

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

import urllib.request
import urllib.parse
import json
import logging
import socket

####################################
# --- Global Functions ---
####################################


# Enable debug to get log messages
def debug(MESSAGE):
    message = "==>" + MESSAGE
    logging.info(message)
    # print(message)


# --- Query the database directly ---
def querydb(QUERY, BASE_URL):
    req_url = BASE_URL + "/api/v1/query?query=" + QUERY

    headers = {
        'User-Agent': "FSCT/9.12.2020",
        'Accept': "application/json",
        'charset': "utf-8"
        }

    debug('Starting Prometheus querydb() Function')

    try:
        request = urllib.request.Request(req_url, headers=headers)
        resp = urllib.request.urlopen(request)
        debug("Ending Prometheus querydb() Function. Response Code:" + str(resp.getcode()))
        return(resp.getcode(), resp.read().decode('utf-8'))

    except Exception as err:
        print(str(err))
        debug("Error getting query data, Server returned => " + str(err))
        return("500", "ERROR")


# Return hostname
def resolve(IP, HOSTNAME):
    if HOSTNAME:
        left = HOSTNAME.split('.')
        return (left[0])
    else:
        try:
            name = socket.gethostbyaddr(IP)
            left = name[0].split('.')
            return (left[0])
        except:
            return("")

####################################
# --- LINUX Computations ---
####################################


# Function to compute the file system use percentage for the root file system "/"
def node_filesystem_rootfs(HOST, PORT, BASE_URL):
    # Build the query
    query = "100 - ((node_filesystem_avail_bytes{instance=~\"" + HOST + ":" + PORT + "\",mountpoint=\"/\",fstype!=\"rootfs\"} * 100) / node_filesystem_size_bytes{instance=~\"" + HOST + ":" + PORT + "\",mountpoint=\"/\",fstype!=\"rootfs\"})"
    # Encode the query string
    QUERY = urllib.parse.quote(query)
    (code, resp) = querydb(QUERY, BASE_URL)
    if code == 200:
        response = json.loads(resp)
        if not response['data']['result']:
            debug("NO VALUE IN RESULTS")
            return("500", "ERROR")
        percent_used = round(float(response['data']['result'][0]['value'][1]))
        return(code, percent_used)
    else:
        return(code, resp)


# Function to compute the RAM used percentage
def node_memory(HOST, PORT, BASE_URL):
    # Build the query
    query = "100 - ((node_memory_MemAvailable_bytes{instance=~\"" + HOST + ":" + PORT + "\"} * 100) / node_memory_MemTotal_bytes{instance=~\"" + HOST + ":" + PORT + "\"})"
    # Encode the query string
    QUERY = urllib.parse.quote(query)
    (code, resp) = querydb(QUERY, BASE_URL)
    if code == 200:
        response = json.loads(resp)
        if not response['data']['result']:
            debug("NO VALUE IN RESULTS")
            return("500", "ERROR")
        percent_used = round(float(response['data']['result'][0]['value'][1]))
        return(code, percent_used)
    else:
        return(code, resp)


# Function to compute the SWAP used percentage
def node_swap(HOST, PORT, BASE_URL):
    # Build the query
    query = "((node_memory_SwapTotal_bytes{instance=~\"" + HOST + ":" + PORT + "\"} - node_memory_SwapFree_bytes{instance=~\"" + HOST + ":" + PORT + "\"}) / (node_memory_SwapTotal_bytes{instance=~\"" + HOST + ":" + PORT + "\"} )) * 100"
    # Encode the query string
    QUERY = urllib.parse.quote(query)
    (code, resp) = querydb(QUERY, BASE_URL)
    if code == 200:
        response = json.loads(resp)
        if not response['data']['result']:
            debug("NO VALUE IN RESULTS")
            return("500", "ERROR")
        percent_used = response['data']['result'][0]['value'][1]
        # Deal with NaN being returned
        if "NaN" in percent_used:
            percent_used = 0
        percent_used = round(float(percent_used))
        return(code, percent_used)
    else:
        return(code, resp)


# Function to return total number of CPU on the machine
def node_cpu_count(HOST, PORT, BASE_URL):
    # Build the query
    query = "count(count(node_cpu_seconds_total{instance=~\"" + HOST + ":" + PORT + "\"}) by (cpu))"
    # Encode the query string
    QUERY = urllib.parse.quote(query)
    (code, resp) = querydb(QUERY, BASE_URL)
    if code == 200:
        response = json.loads(resp)
        if not response['data']['result']:
            debug("NO VALUE IN RESULTS")
            return("500", "ERROR")
        percent_used = round(float(response['data']['result'][0]['value'][1]))
        return(code, percent_used)
    else:
        return(code, resp)


# Function to return uptime of the machine in minutes
def node_uptime_min(HOST, PORT, BASE_URL):
    # Build the query
    query = "node_time_seconds{instance=~\"" + HOST + ":" + PORT + "\"} - node_boot_time_seconds{instance=~\"" + HOST + ":" + PORT + "\"}"
    # Encode the query string
    QUERY = urllib.parse.quote(query)
    (code, resp) = querydb(QUERY, BASE_URL)
    if code == 200:
        response = json.loads(resp)
        if not response['data']['result']:
            debug("NO VALUE IN RESULTS")
            return("500", "ERROR")
        uptime_min = round(float(response['data']['result'][0]['value'][1]) / 60)
        return(code, uptime_min)
    else:
        return(code, resp)


# Function to return 5M system load average
def node_load5(HOST, PORT, BASE_URL):
    # Build the query
    query = "avg(node_load5{instance=~\"" + HOST + ":" + PORT + "\"}) /  count(count(node_cpu_seconds_total{instance=~\"" + HOST + ":" + PORT + "\"}) by (cpu)) * 100"
    # Encode the query string
    QUERY = urllib.parse.quote(query)
    (code, resp) = querydb(QUERY, BASE_URL)
    if code == 200:
        response = json.loads(resp)
        if not response['data']['result']:
            debug("NO VALUE IN RESULTS")
            return("500", "ERROR")
        load5 = round(float(response['data']['result'][0]['value'][1]))
        return(code, load5)
    else:
        return(code, resp)


# Function to return 15M system load average
def node_load15(HOST, PORT, BASE_URL):
    # Build the query
    query = "avg(node_load15{instance=~\"" + HOST + ":" + PORT + "\"}) /  count(count(node_cpu_seconds_total{instance=~\"" + HOST + ":" + PORT + "\"}) by (cpu)) * 100"
    # Encode the query string
    QUERY = urllib.parse.quote(query)
    (code, resp) = querydb(QUERY, BASE_URL)
    if code == 200:
        response = json.loads(resp)
        if not response['data']['result']:
            debug("NO VALUE IN RESULTS")
            return("500", "ERROR")
        load5 = round(float(response['data']['result'][0]['value'][1]))
        return(code, load5)
    else:
        return(code, resp)


####################################
# --- Windows Computations ---
####################################


# Function to return 5M system load average
def win_load5(HOST, PORT, BASE_URL):
    # Build the query - normalizing to percent, subtracting idle time to get busy
    query = "(1 - sum by (mode) (rate(wmi_cpu_time_total{instance=~\"" + HOST + ":" + PORT + "\", mode=\"idle\"}[5m]))) * 100"
    # Encode the query string
    QUERY = urllib.parse.quote(query)
    (code, resp) = querydb(QUERY, BASE_URL)
    if code == 200:
        response = json.loads(resp)
        if not response['data']['result']:
            debug("NO VALUE IN RESULTS")
            return("500", "ERROR")
        percent_used = round(float(response['data']['result'][0]['value'][1]))
        return(code, percent_used)
    else:
        return(code, resp)


# Function to return 15M system load average
def win_load15(HOST, PORT, BASE_URL):
    # Build the query - normalizing to percent, subtracting idle time to get busy
    query = "(1 - sum by (mode) (rate(wmi_cpu_time_total{instance=~\"" + HOST + ":" + PORT + "\", mode=\"idle\"}[15m]))) * 100"
    # Encode the query string
    QUERY = urllib.parse.quote(query)
    (code, resp) = querydb(QUERY, BASE_URL)
    if code == 200:
        response = json.loads(resp)
        if not response['data']['result']:
            debug("NO VALUE IN RESULTS")
            return("500", "ERROR")
        percent_used = round(float(response['data']['result'][0]['value'][1]))
        return(code, percent_used)
    else:
        return(code, resp)

# Function to return Windows disk use %
def win_disk(HOST, PORT, BASE_URL):
    # Build the query
    query = "(1 - (wmi_logical_disk_free_bytes{instance=~\"" + HOST + ":" + PORT + "\", volume=\"C:\"} / wmi_logical_disk_size_bytes{instance=~\"" + HOST + ":" + PORT + "\", volume=\"C:\"})) * 100"
    # Encode the query string
    QUERY = urllib.parse.quote(query)
    (code, resp) = querydb(QUERY, BASE_URL)
    if code == 200:
        response = json.loads(resp)
        if not response['data']['result']:
            logging.info("===>NO VALUE IN RESULTS")
            return("500", "ERROR")
        percent_used = round(float(response['data']['result'][0]['value'][1]))
        return(code, percent_used)
    else:
        return(code, resp)


# Function to return Windows % of Physucal Memory Used
def win_ram(HOST, PORT, BASE_URL):
    # Build the query
    query = "(1 - (wmi_os_physical_memory_free_bytes{instance=~\"" + HOST + ":" + PORT + "\"} / wmi_cs_physical_memory_bytes{instance=~\"" + HOST + ":" + PORT + "\"})) * 100"
    # Encode the query string
    QUERY = urllib.parse.quote(query)
    (code, resp) = querydb(QUERY, BASE_URL)
    if code == 200:
        response = json.loads(resp)
        if not response['data']['result']:
            logging.info("===>NO VALUE IN RESULTS")
            return("500", "ERROR")
        percent_used = round(float(response['data']['result'][0]['value'][1]))
        return(code, percent_used)
    else:
        return(code, resp)
