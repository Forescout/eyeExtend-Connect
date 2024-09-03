import jwt  # PyJWT version 1.6.1 as of the time of authoring
import uuid
from datetime import datetime, timedelta
import logging
import requests
import urllib.request
from enum import Enum
import ssl
import json
import re
import random
import time
import math
#import exception
from base64 import b64encode


#import ciscodnacapp_library as ciscodnacapp_library
#from ciscodnacapp_testdata import *

logging.debug("Resolver for Ciscodnac Connect App")


response = {}
properties = {}
ciscodata = []

del ciscodata[:]

# Mapping between ciscodnacapp API response fields to CounterACT properties
ciscodnacapp_to_ct_props_map = {
    "status": "connect_ciscodnacapp_status"

}

if params["connect_ciscodnacapp_kmac"] == None or params["mac"] == None:
    ciscodata.append(f"No Mac defined or provided")
    ciscodata.append(f"")
    ciscodata.append(f"")
    ciscodata.append(f"")   
    logging.debug(f"PARAM MAC or of config MAC passed as NULL")
else:

    if params["connect_ciscodnacapp_kmac"] != params["mac"]:
        ciscodata.append(f"Mac of device does not match, switch update aborted.")
        ciscodata.append(f"")
        ciscodata.append(f"")
        ciscodata.append(f"")  
        logging.debug(f"PARAM MAC " + params["mac"] + " Does not match config MAC " +  params["connect_ciscodnacapp_kmac"])
    else:

        try:
            logging.debug(f"Init library for resolver")
            MyCiscoDNAC=ciscodnacapp_library.CiscoDNACTopClass(params,response) 
            AuthorToken = MyCiscoDNAC.GetTokenWithUserName()
            if AuthorToken:
                ciscodata.append(f"Successfully connected to Cisco API.")
            else:
                ciscodata.append(f"Could not connect to the Cisco API.")
            logging.debug(f"{ciscodata}")
            CAToken=MyCiscoDNAC.GetCAAPIToken()
            if CAToken:
                ciscodata.append(f"Successfully connected to CounterACT API")
            else:
                ciscodata.append(f"Could not connect to CounterACT API server.")
            logging.debug(f"{ciscodata}")
            if (CAToken and AuthorToken):
                logging.debug(f"Trying to do a poll action")
                PollStatus=MyCiscoDNAC.PolSwitchData()
                if (PollStatus == True):
                    ciscodata.append(f"Poll status succeeded")
                else:
                    ciscodata.append(f"Poll status failed")

        except Exception as e:
            logging.debug(f"Error in test")
            logging.debug(e)
            response["succeeded"] = False
            ciscodata.append = str(e)

properties[ciscodnacapp_to_ct_props_map['status']] = ciscodata
response['properties'] = properties