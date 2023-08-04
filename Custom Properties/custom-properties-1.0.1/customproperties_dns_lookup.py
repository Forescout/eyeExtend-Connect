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

import socket
import logging

def remove_domain(hostname):
    # Split the hostname by dots and keep only the first part
    parts = hostname.split('.')
    hostname_without_domain = parts[0]
    logging.debug("***Custom Props*** Remove Domain function returned {}".format(hostname_without_domain))
    return hostname_without_domain

def reverse_dns_lookup(ip_address):
    try:
        # Perform reverse DNS lookup
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        logging.debug("***Custom Props*** DNS query for {} returned [ {} ]".format(ip_address,hostname))
        return remove_domain(hostname)
    except socket.herror as e:
        logging.debug("***Custom Props*** DNS query for {} returned [ {} ]".format(ip_address,e))
        return None

def remove_domain_custom(hostname, domains):
    # Split the hostname by each domain in the list and take the first part
    for domain in domains:
        parts = hostname.split(domain, 1)
        hostname = parts[0]
    
    hostname = hostname.rstrip('.')
    return hostname

def reverse_dns_lookup_custom(ip_address, domains):
    try:
        # Perform reverse DNS lookup
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        return remove_domain_custom(hostname, domains)
    except socket.herror as e:
        return None

custom_dns = params.get("connect_customproperties_custom_dns")
ip = params.get("ip")
custom_dns_list = custom_dns.split(',')
response = {}

if ip:
    logging.debug("***Custom Props*** Retrieved IP Address [ {} ] to begin lookup process".format(ip))
    if custom_dns:
        logging.debug("***Custom Props*** Performing Reverse DNS Lookup for IP [ {} ] Using custom DNS [ {} ] for formatting of result.".format(ip, custom_dns_list))
        hostname = reverse_dns_lookup_custom(ip, custom_dns_list)
    else:
        logging.debug("***Custom Props*** Performing Reverse DNS Lookup for IP [ {} ] Using default formatting of result.".format(ip))
        hostname = reverse_dns_lookup(ip)

    if hostname:
        logging.debug("***Custom Props*** Reverse DNS lookup for IP address {} : {}".format(ip, hostname))
        properties = {}
        
        properties["ip"] = ip
        properties["connect_customproperties_short_dns"] = hostname
        logging.debug("***Custom Props*** Mapping properties [ {} ]".format(properties))
        
        response["properties"] = properties
        logging.debug("***Custom Props*** Returning properties [ {} ]".format(response["properties"]))
    else:
        response["error"] = "Unable to perform reverse DNS lookup for IP address {}".format(ip)
        logging.debug("***Custom Props*** {}".format(response["error"]))
else:
    response["error"] = "Cannot find IP Address for lookup"
    logging.debug("***Custom Props*** {}".format(response["error"]))