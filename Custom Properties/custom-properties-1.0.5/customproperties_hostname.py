import logging

enabled = params.get("connect_customproperties_hostname_enabled")

response = {}

if enabled == "true":

    ip = params.get("ip")
    dhcpname = params.get("dhcp_hostname_v2")
    dnsname = params.get("hostname")
    netbiosname = params.get("nbthost")

    properties = {}

    # Check which of DNS, DHCP and NetBIOS exist

    totalvalues = 0

    if dhcpname:
        totalvalues += 1
        dhcpname = dhcpname.lower()

    if dnsname:
        totalvalues += 3
        dnsname = dnsname.lower()
        dnssections = dnsname.split('.')
        dnsname = dnssections[0]

    if netbiosname:
        totalvalues += 5
        netbiosname = netbiosname.lower()

    logging.debug("***Custom Props*** DHCP: {} DNS: {} NetBIOS: {} Total Values: {}".format(dhcpname,dnsname,netbiosname,totalvalues))

    if totalvalues == 0:
        logging.debug("***Custom Props*** No hostnames found")
        properties["connect_customproperties_normalisedhostname"] = ""
    elif totalvalues == 1:
        logging.debug("***Custom Props*** Only DHCP Hostname found: [ {} ]".format(dhcpname))
        properties["connect_customproperties_normalisedhostname"] = dhcpname
    elif totalvalues == 3:
        logging.debug("***Custom Props*** Only DNS Hostname found: [ {} ]".format(dnsname))
        properties["connect_customproperties_normalisedhostname"] = dnsname
    elif totalvalues == 4:
        logging.debug("***Custom Props*** Found DHCP: [ {} ], and DNS: [ {} ]".format(dhcpname,dnsname))
        if dnsname == dhcpname:
            logging.debug("***Custom Props*** DHCP and DNS Hostnames match")
            properties["connect_customproperties_normalisedhostname"] = dnsname
        else:
            logging.debug("***Custom Props*** DHCP and DNS Hostnames do not match. Preferring DNS: [ {} ]".format(dnsname))
            properties["connect_customproperties_normalisedhostname"] = dnsname
    elif totalvalues == 5:
        logging.debug("***Custom Props*** Only NetBIOS Hostname found: [ {} ]".format(netbiosname))
        properties["connect_customproperties_normalisedhostname"] = netbiosname
    elif totalvalues == 6:
        logging.debug("***Custom Props*** Found DHCP: [ {} ], and NetBIOS: [ {} ]".format(dhcpname,netbiosname))
        if netbiosname == dhcpname:
            logging.debug("***Custom Props*** DHCP and NetBIOS Hostnames match")
            properties["connect_customproperties_normalisedhostname"] = dhcpname
        else:
            logging.debug("***Custom Props*** DHCP and NetBIOS Hostnames do not match. Preferring DHCP: [ {} ]".format(dhcpname))
            properties["connect_customproperties_normalisedhostname"] = dhcpname
    elif totalvalues == 8:
        logging.debug("***Custom Props*** Found NetBIOS: [ {} ], and DNS: [ {} ]".format(netbiosname,dnsname))
        if dnsname == dhcpname:
            logging.debug("***Custom Props*** NetBIOS and DNS Hostnames match")
            properties["connect_customproperties_normalisedhostname"] = dnsname
        else:
            logging.debug("***Custom Props*** NetBIOS and DNS Hostnames do not match. Preferring DNS: [ {} ]".format(dnsname))
            properties["connect_customproperties_normalisedhostname"] = dnsname
    elif totalvalues == 9:
        logging.debug("***Custom Props*** Found DHCP: [ {} ], DNS: [ {} ], and NetBIOS: [ {} ]".format(dhcpname,dnsname,netbiosname))
        if dnsname == dhcpname == netbiosname:
            logging.debug("***Custom Props*** DHCP, DNS and NetBIOS Hostnames match")
            properties["connect_customproperties_normalisedhostname"] = dnsname
        elif dnsname == dhcpname:
            logging.debug("***Custom Props*** DHCP and DNS Hostnames match. Ignoring NetBIOS")
            properties["connect_customproperties_normalisedhostname"] = dnsname
        elif dnsname == netbiosname:
            logging.debug("***Custom Props*** NetBIOS and DNS Hostnames match. Ignoring DHCP")
            properties["connect_customproperties_normalisedhostname"] = dnsname
        elif netbiosname == dhcpname:
            logging.debug("***Custom Props*** DHCP and NetBIOS Hostnames match. Ignoring DNS")
            properties["connect_customproperties_normalisedhostname"] = dhcpname
        else:
            logging.debug("***Custom Props*** DHCP, DNS and NetBIOS Hostnames do not match. Preferring DNS")
            properties["connect_customproperties_normalisedhostname"] = dnsname
    else:
        logging.debug("***Custom Props*** Error normalising hostname. Review all debug logs.")

    response["ip"] = ip
    response["properties"] = properties

    logging.debug("***Custom Props*** Returning resolved values: [ {} ]".format(response))

else:
    response["error"] = "Normalise Hostname disabled, check app configuration"
    logging.debug("***Custom Props*** {}".format(response["error"]))