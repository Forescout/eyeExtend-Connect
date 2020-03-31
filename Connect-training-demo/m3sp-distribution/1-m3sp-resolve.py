# Sample connect resolve scrip in simplest form
import uuid
import json
import urllib.request, urllib.error, urllib.parse
# import logging so that we can log to the python server at /usr/local/forescout/plugin/connect/python_logs
import logging

logging.info("=======>>>>>Starting sample resolve Script.")

# mapping between our App properties and the CT internal properties
# in this case, 'department' is returned from our remote host, and 'connect_m3sp_department' is the internal CT property name which must be unique & defined in 'properties.conf'
m3sp_to_ct_props_map = {
    "department": "connect_m3sp_department",
    "description": "connect_m3sp_description"
}

# CT will provide a params{} dictionary with the dependent properties you defined in 'properties.conf' for each of your App's custom properties.
# so we can check for mac address as follows:

if "mac" in params:
    logging.info("=======>>>>>Resolving mac address: " + params["mac"])

# All responses from scripts must contain the JSON object 'response'.
# Host property resolve scriptswill need to populate a 'properties' JSON object within the
# JSON object 'response'. The 'properties' object will be a key, value mapping between the CT #property name and the value of the property.
response = {}
properties = {}
properties["connect_m3sp_department"] = "Marketing"
properties["connect_m3sp_description"] = "Somewhere over the rainbow"
response["properties"] = properties
logging.info("=======>>>>> m3sp properties returned: {}".format(properties))
