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
#import traceback

#import ciscodnacapp_library as ciscodnacapp_library
#from ciscodnacapp_testdata import *


logging.debug(f"Test for Ciscodnac Connect App")

response = {}
properties = {}
ciscodata = []



try:
    logging.debug(f"Init library")

    MyCiscoDNAC=ciscodnacapp_library.CiscoDNACTopClass(params,response) 
    AuthorToken = MyCiscoDNAC.GetTokenWithUserName()
#    raise ValueError('A Token was received.') 
# Like the acti response, the response object must have a "succeeded" field to denote success.
# It can also optionally have a "result_msg" field to display a custom test result message.
    if AuthorToken:
        response["succeeded"] = True
        response["result_msg"] = "Successfully connected to Cisco API."
    else:
        response["succeeded"] = False
        response["result_msg"] = "Could not connect to the Cisco API."

#    raise ValueError('Line 45') 
    logging.debug(f"{response}")
    CAToken=MyCiscoDNAC.GetCAAPIToken()
    if CAToken:
        response["succeeded"] = True
        response["result_msg"] = "Successfully connected to CounterACT API"
    else:
        response["succeeded"] = False
        response["result_msg"] = "Could not connect to CounterACT API server."
    logging.debug(f"{response}")
    if (CAToken and AuthorToken):
        logging.debug(f"Trying to do a poll action")
        PollStatus=MyCiscoDNAC.PolSwitchData()
        if (PollStatus == True):
            response["succeeded"] = True
            response["result_msg"] = "Poll status succeeded"
        else:
            response["succeeded"] = False
            response["result_msg"] = "Poll status failed"

except Exception as e:
    logging.debug(f"Error in test {e}")
    response["succeeded"] = False
    response["result_msg"] = str(e)
