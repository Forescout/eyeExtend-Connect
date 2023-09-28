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

network_adapters = params.get("hwi_network_adapters")
ip = params.get("ip")
match_key = "ip_address"
response = {}

network_adapters_subproperty_mapping = {
    "index" : "index",
    "description" : "description",
    "service_name" : "servicename",
    "ip_address" : "ipaddress",
    "ip_subnet" : "ipsubnet",
    "default_ip_gateway" : "defaultipgateway",
    "ip_enabled" : "ipenabled",
    "ip_connection_metric" : "ipconnectionmetric",
    "mac_address" : "macaddress",
    "dhcp_enabled" : "dhcpenabled",
    "dhcp_server" : "dhcpserver",
    "dns_domain" : "dnsdomain",
    "dns_hostname" : "dnshostname",
    "dns_server_search_order" : "dnsserversearchorder",
    "domain_dns_registration_enabled" : "domaindnsregistrationenabled",
    "igmp_level" : "igmplevel"
}

if ip:
    logging.debug("***Custom Props*** Retrieved IP Address [ {} ] to check Network Adapters".format(ip))
    if network_adapters:
        logging.debug("***Custom Props*** For IP [ {} ] Retrieved [ {} ] Network Adapters for processing.".format(ip, network_adapters))
        network_adapters_list = network_adapters.split("},{")
        properties = {}
        subproperties = {}
        for entry in network_adapters_list:
            if f"{match_key}={ip}" in entry:
                key_value_pairs = entry.strip("{}").split(", ")

                for key_value_pair in key_value_pairs:
                    key, value = key_value_pair.split("=")
                    if key in network_adapters_subproperty_mapping:
                        subproperties[network_adapters_subproperty_mapping[key]] = value
            
        properties["connect_customproperties_active_network_adapter"] = subproperties

        if properties:
            logging.debug("***Custom Props*** Found matching adapter: [ {} ]".format(properties))
            response["ip"] = ip
            response["properties"] = properties
            logging.debug("***Custom Props*** Sending response: [ {} ]".format(response))
        else:
            response["error"] = "No matching adapter found!"
            logging.debug("***Custom Props*** {}".format(response["error"]))
    else:
        response["error"] = "No Network Adapters found. Check HWI Property is being Resolved."
        logging.debug("***Custom Props*** For IP [ {} ] No Network Adapters for processing. Check HWI Property is being Resolved.".format(ip))
else:
    response["error"] = "Cannot find IP Address"
    logging.debug("***Custom Props*** {}".format(response["error"]))