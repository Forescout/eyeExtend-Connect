# ACTION: Resolve Endpoint Metrics
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

import logging

prom_functions.debug('Starting Resolve Prometheus Endpoint Script')

# dump all params values
# logging.debug("params: {}".format(params))

response = {}
properties = {}

# Use the instance cache to identify targets and ports
cache = json.loads(params.get('connect_app_instance_cache'))
response = {}
IP = params.get('ip')
OS = params.get('os_classification')

hostname = params.get("hostname")
HOSTNAME = prom_functions.resolve(IP,hostname)
BASE_URL = params.get('connect_prometheus_server')

target = ""

if IP in cache:
    target = IP
    port = cache[IP]
    prom_functions.debug("{IP} TARGET FOUND IN CACHE.")

if HOSTNAME:
    if HOSTNAME in cache:
        target = HOSTNAME
        port = cache[HOSTNAME]
        prom_functions.debug("{HOSTNAME} TARGET FOUND IN CACHE.")

# We must have a target from cache to proceed
if target:
    prom_functions.debug("Using Target: " + target + " port:" + port)
    # Functins are OS specific
    if "Linux" in OS:
        # rootfs
        (code, percent_used) = prom_functions.node_filesystem_rootfs(target, port, BASE_URL)
        if code == 200:
            prom_functions.debug("Percentage of root filesystem used: " + str(percent_used) + "%")
            properties['connect_prometheus_lin_rootfs'] = percent_used
        # ram
        (code, percent_used) = prom_functions.node_memory(target, port, BASE_URL)
        if code == 200:
            prom_functions.debug("Percentage of RAM used: " + str(percent_used) + "%")
            properties['connect_prometheus_lin_ram'] = percent_used
        # swap
        (code, percent_used) = prom_functions.node_swap(target, port, BASE_URL)
        if code == 200:
            prom_functions.debug("Percentage of SWAP used: " + str(percent_used) + "%")
            properties['connect_prometheus_lin_swap'] = percent_used
        # cpu count
        (code, count) = prom_functions.node_cpu_count(target, port, BASE_URL)
        if code == 200:
            prom_functions.debug("Number of CPU: " + str(count))
            properties['connect_prometheus_lin_cpu_count'] = count
        # Uptime in minutes
        (code, count) = prom_functions.node_uptime_min(target, port, BASE_URL)
        if code == 200:
            prom_functions.debug("Uptime in Minutes: " + str(count))
            properties['connect_prometheus_lin_uptime'] = count
        # Load5
        (code, load) = prom_functions.node_load5(target, port, BASE_URL)
        if code == 200:
            prom_functions.debug("5 Minute System Load AVG: " + str(load))
            properties['connect_prometheus_lin_load5'] = load
        (code, load) = prom_functions.node_load15(target, port, BASE_URL)
        if code == 200:
            prom_functions.debug("15 Minute System Load AVG: " + str(load))
            properties['connect_prometheus_lin_load15'] = load
        # other functions here
        response["properties"] = properties

    elif "Windows" in OS:
        # load5
        (code, load5) = prom_functions.win_load5(target, port, BASE_URL)
        if code == 200:
            prom_functions.debug("5M AVG of Windows CPU used: " + str(load5) + "%")
            properties['connect_prometheus_win_load5'] = load5
        # load15
        (code, load15) = prom_functions.win_load15(target, port, BASE_URL)
        if code == 200:
            prom_functions.debug("15M AVG of Windows CPU used: " + str(load15) + "%")
            properties['connect_prometheus_win_load15'] = load15
        # Disk Use
        (code, disk) = prom_functions.win_disk(target, port, BASE_URL)
        if code == 200:
            prom_functions.debug("Percentage of C drive used: " + str(disk) + "%")
            properties['connect_prometheus_win_disk'] = disk
        # Physical Nemory Use
        (code, ram) = prom_functions.win_ram(target, port, BASE_URL)
        if code == 200:
            prom_functions.debug("Percentage of Physical Memory used: " + str(ram) + "%")
            properties['connect_prometheus_win_ram'] = ram
            # other functions here
        response["properties"] = properties

    else:
        prom_functions.debug("OS Not currently supported =>" + OS)
        response["error"] = "OS Not currently supported"

else:
    prom_functions.debug("NO TARGET FOUND IN CACHE.")
    response["error"] = "No Prometheus Target Found"

prom_functions.debug('Ending Resolve Prometheus Endpoint Script')
