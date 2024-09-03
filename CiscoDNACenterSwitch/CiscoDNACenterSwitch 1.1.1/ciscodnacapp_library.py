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
#import traceback
#import exception
from base64 import b64encode
from requests.auth import HTTPProxyAuth
from enum import Enum


#from ciscodnacapp_testdata import *



class ProxyProtocol(Enum):
    """ Choices for proxy server proxies

    Indicate what proxy server proxies (string) shall use in the request. Can
    be all, http, https or none. If proxy server supports both protocols,
    can use ProxyProtocol.all. It is a good practise to use
    ProxyProtocol.all if supporting both protocols. If only support http, then
    use ProxyProtocol.http. If support https, then use ProxyProtocol.https.
    """
    all = 1
    http = 2
    https = 3
    none = 4


class ConnectProxyServer:
    """ ConnectProxyServer

    This class will take param as input and setup proxy server info if there
    is any in the constructor. User can use class methods that 1) use
    requests or 2) use urllib.request to invoke http requests. If proxy
    server is enabled, both the proxy IP and proxy port are required, in this
    case, if not specified, ValueError is raised. Username and password for
    the proxy serve are optional. Only when proxy server is enabled,
    which specified in params.get("connect_proxy_enable"), proxy server info
    is used in the method calls. When constructed, the self.proxies is None.

    :keyword params, variables passed by the connect script

    - connect_proxy_enable, if not specified or false, indicate no proxy server.

    - connect_proxy_ip, required when connect_proxy_enable is true

    - connect_proxy_port, required when connect_proxy_enabled is true

    - connect_proxy_username, optional

    - connect_proxy_password, optional

    :raise ValueError if proxy server is enabled and proxy ip or port is not specified
    """
    def __init__(self, inparams):
        is_proxy_enabled = inparams.get("connect_proxy_enable")
        logging.debug(f"Proxy enabled status: " + str(is_proxy_enabled))
        if is_proxy_enabled == "true":  # Cover the case is_proxy_enable is None, it is not equal to "true"
            #: A boolean to indicate if the proxy server is enabled
            self.is_enabled = True
        else:
            self.is_enabled = False
        if self.is_enabled:
            #: Proxy server ip. None if proxy server is not enabled.
            # Required if proxy server is enabled, otherwise, a ValueError is
            # raised
            self.ip = inparams.get("connect_proxy_ip")
            if not self.ip:
                raise ValueError("Proxy IP is empty or null.")
            #: Proxy server port. None if proxy server is not enabled.
            # Required if proxy server is enabled, otherwise, a ValueError is
            # raised
            self.port = inparams.get("connect_proxy_port")
            if not self.port:
                raise ValueError("Proxy port is empty or null.")

            # Username and password can be null
            #: Proxy server username. (Optional), None if proxy server is not enabled.
            self.username = inparams.get("connect_proxy_username")
            #: Proxy server password. (Optional), None if proxy server is not enabled.
            self.password = inparams.get("connect_proxy_password")
        else:
            self.ip = None
            self.port = None
            self.username = None
            self.password = None
        # : Proxies, default is none
        self.proxies = None
        logging.debug(f"Proxy IP: {self.ip}")
        logging.debug(f"Proxy port: {self.port}")
        logging.debug(f"Proxy username: {self.username}")

    def get_proxies(self, protocol=ProxyProtocol.https):
        """ Returns proxies string used to connect to proxy server base on
        protocol passed in.

        The proxies will contain username, password and port info in required
        format to connect to proxy server
        :param protocol: Proxy server protocol to use.
            Value can be ProxyProtocol.https, ProxyProtocol.http or
            ProxyProtocol.none. Default is ProxyProtocol.https.

        :return: Proxies in hash with proxy server info set
        """
        proxies = {
            "https:": None,
            "http:": None
        }

        if ProxyProtocol.none == protocol:
            return proxies

        if ProxyProtocol.https == protocol:
            if self.username and self.password:
                proxies = {
                    "https": "https://{}:{}@{}:{}".format(self.username, self.password, self.ip, self.port)
                }
            elif self.username and not self.password:
                proxies = {
                    "https": "https://{}:{}@{}:{}".format(self.username, "", self.ip, self.port)
                }
            else:
                proxies = {
                    "https": "https://{}:{}".format(self.ip, self.port)
                }
        elif ProxyProtocol.http == protocol:
            if self.username and self.password:
                proxies = {
                    "http": "http://{}:{}@{}:{}".format(self.username, self.password, self.ip, self.port),
                }
            elif self.username and not self.password:
                proxies = {
                    "http": "https://{}:{}@{}:{}".format(self.username, "", self.ip, self.port)
                }
            else:
                proxies = {
                    "http": "http://{}:{}".format(self.ip, self.port)
                }
        elif ProxyProtocol.all == protocol:
            if self.username and self.password:
                proxies = {
                    "http": "http://{}:{}@{}:{}".format(self.username, self.password, self.ip, self.port),
                    "https": "https://{}:{}@{}:{}".format(self.username, self.password, self.ip, self.port)
                }
            elif self.username and not self.password:
                proxies = {
                    "http": "https://{}:{}@{}:{}".format(self.username, "", self.ip, self.port),
                    "https": "https://{}:{}@{}:{}".format(self.username, "", self.ip, self.port)
                }
            else:
                proxies = {
                    "http": "http://{}:{}".format(self.ip, self.port),
                    "https": "https://{}:{}".format(self.ip, self.port)
                }
        return proxies

    def get_empty_proxies_string(self):
        return self.get_proxies(ProxyProtocol.none)

    @staticmethod
    def set_no_cache_connection_pool():
        """ Do not cache the pool"""
        with requests.Session() as session:
            adapter = requests.adapters.HTTPAdapter(pool_connections=0)
            logging.debug(f"Clear connection pool.")
            session.mount("https://", adapter)
            session.mount("http://", adapter)

    @staticmethod
    def set_default_connection_pool():
        """ Default connection pool setting """
        with requests.Session() as session:
            logging.debug(f"Set default connection pool.")
            session.mount("https://", requests.adapters.HTTPAdapter())
            session.mount("http://", requests.adapters.HTTPAdapter())

    def get_requests_session(self, protocol=ProxyProtocol.https, **kwargs):
        """ Get a requests session with proxy server info set.

        Method will check if the proxy is enabled or not. And after getting
        the requests session, user can use post, delete, put whatever
        requests session supports to invoke a http request. By using this
        method, user proxy server is transparent to the user. The proxy
        server configuration is set. Check sessions to see what variables can
        be passed in details:

        https://requests.readthedocs.io/en/master/api/#request-sessions

        Typical usage example:

            - Use session with headers and verify SSL context (accepts most of requests.Session accepts)

            proxy_server = ConnectProxyServer(params)
            with proxy_server.get_requests_session(
                ProxyProtocol.https,
                headers=headers,
                verify=sslverify) as session:
                post_response = session.post(token_url, json=payload)
                delete_response = session.delete(delete_user_url)

            session will be closed on exiting the with block

            - Use session with SSL context in post request (which accepts everything requests.request accepts)

            proxy_server = ConnectProxyServer(params)

            session =proxy_server.get_requests_session(ProxyProtocol.https,headers=device_headers, verify=sslverify)

            add_response = session.post(add_user_url, json=json_body)

            get_response = session.get(get_user_url)

            proxy_server = ConnectProxyServer(params)

            session = proxy_server.get_requests_session(ProxyProtocol.https)

            add_response = session.post(add_user_url, json=json_body, verify=sslverify, headers=headers)

        :param self:

        :param protocol: Proxies to use in the session for the proxy server if
        proxy server is enabled, can be ProxyProtocol.https, ProxyProtocol.http
        or ProxyProtocol.none. Default is ProxyProtocol.https.
        This sets the session proxies, auth in HTTPProxyAuth and trust_env.

        :param kwargs: (optional) Any arguments that requests.session supports,
        except proxies, auth and trust_env, passed as "headers=headerValue",
        for example. User can also pass the value via session methods such as
        post, get, delete etc. you can also pass use_cache=true which will
        persist in connection pool. By default we don't cache the connection in
        the connection pool.

        :return: A requests.session that has proxy server configured.
        """
        # By default, we don't put the connection back to the connection pool
        # So each session is a new connection. User can chose to use default
        # connection pool, then connection from connection pool would persist
        if kwargs.get("use_cache"):
            self.set_default_connection_pool()
        else:
            self.set_no_cache_connection_pool()

        session = requests.Session()
        if self.is_enabled:
            proxies = self.get_proxies(protocol)
            # Set proxy ones for entire session
            session.auth = HTTPProxyAuth(self.username, self.password)
            session.proxies.update(proxies)
            self.proxies = proxies
        else:
            proxies = self.get_empty_proxies_string()
            session.proxies.update(proxies)
            session.auth = None
            self.proxies = proxies
        # Not trusting default env
        session.trust_env = False

        # Set the variables that session supports. Not including proxies,
        # auth and trust_env. However, There is nothing prevents caller to
        # get the session first then override proxies, auth and trust_env
        if kwargs.get("cert"):
            session.cert = kwargs.get("cert")
        if kwargs.get("cookies"):
            session.cookies = kwargs.get("cookies")
        if kwargs.get("headers"):
            session.headers = kwargs.get("headers")
        if kwargs.get("hooks"):
            session.hooks = kwargs.get("hooks")
        if kwargs.get("max_redirects"):
            session.max_redirects = kwargs.get("max_redirects")
        if kwargs.get("params"):
            session.params = kwargs.get("params")
        if kwargs.get("stream"):
            session.stream = kwargs.get("stream")
        if kwargs.get("verify"):
            session.verify = kwargs.get("verify")
        return session

    def get_urllib_request_opener(self, protocol=ProxyProtocol.https, *handlers):
        """ Get a urllib request opener with proxy server configured

        Get a request opener that can has proxy server set and user can use
        opener.open or urllib.request.urlopen after this method to connect to
        invoke a http request. To check out opener,
        see: https://docs.python.org/3/library/urllib.request.html#urllib.request.build_opener

        Typical usage example:

            -  Use open, pass handlers

            auth_handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

            ssl_handler = urllib.request.HTTPSHandler(context=ssl_context)

            proxy_server = AppProxyServer(params)

            opener_build_opener = proxy_server.get_urllib_request_opener(ProxyProtocol.https, auth_handler, ssl_handler)

            response = opener_build_opener.open(https_url)

            - Use urlopen, pass handlers

            proxy_server = AppProxyServer(params)

            opener_build_opener = proxy_server.get_urllib_request_opener(ProxyProtocol.https, auth_handler, ssl_handler)

            response = urllib.request.urlopen(https_url)

            - Use urlopen, pass info on request

            proxy_server = ConnectProxyServer(params)

            # HTTPS or HTTP or both in the protocol, pass down the ssl_context
            https_handler = urllib.request.HTTPSHandler(context=ssl_context)

            opener = proxy_server.get_urllib_request_opener(ProxyProtocol.https, https_handler)

            get_user_request = urllib.request.Request(get_users_url, headers=device_headers)

            get_user_response = urllib.request.urlopen(get_user_request)

        :param protocol: Proxies to use in the request for the proxy server
        If proxy server is enabled, can be ProxyProtocol.https,
        ProxyProtocol.http or ProxyProtocol.none. Default is
        ProxyProtocol.https.

        :param handlers: (optional) Handlers that urllib.request.build_opener accepts, such as HTTPSHandler.

        :return: opener: OpenerDirector from urllib.request.build_opener that has ProxyHandler set. The consequent
        request call can use opener.open or urllib.request.urlopen.
        """
        if self.is_enabled:
            proxies = self.get_proxies(protocol)
            proxy_handler = urllib.request.ProxyHandler(proxies)
            opener = urllib.request.build_opener(proxy_handler, *handlers)
            self.proxies = proxies
        else:
            proxy_handler = urllib.request.ProxyHandler({})
            opener = urllib.request.build_opener(proxy_handler, *handlers)
            self.proxies = self.get_empty_proxies_string()

        # This is needed to enable opener to able to call urllib.request.urlopen
        urllib.request.install_opener(opener)
        return opener

    def get_urllib_request_https_opener(self, protocol=ProxyProtocol.https, ssl_context=None, basic_auth=None):
        """ Get a urllib request opener with proxy server configured with
        ssl_context and HTTP basic auth handler set.

        Similar to method get_urllib_request_opener, if you want methods to
        set ssl_context and basic auth. The method has HTTPSHandler with SSL
        context and HTTPBasicAuthHandler set for the opener. User can use
        opener.open or urllib.request.urlopen after this method to connect to
        invoke a http request.

        Typical usage example:

            - Use urlopen with ssl_context and HTTPPasswordMgrWithDefaultRealm

            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

            password_mgr.add_password(None, https_url, https_client_id, https_client_secret)

            proxy_server = AppProxyServer(params)

            opener = proxy_server.get_urllib_request_https_opener(ProxyProtocol.https, ssl_context, password_mgr)

            response = urllib.request.urlopen(CrowdStrike_HTTPS_URL)

            - Use urlopen, with ssl_context

            proxy_server = AppProxyServer(params)

            opener = proxy_server.get_urllib_request_https_opener(ProxyProtocol.https, ssl_context)

            http_post_request = urllib.request.Request(https_url, http_post_data.encode('utf-8'), method='POST')

            http_post_request.add_header("Content-Type", "application/x-www-form-urlencoded")

            http_post_request.add_header("accept", "application/json")

            # Use opener.open to get the request ( you can use urlopen as well, look at resolve script
            response = urllib.request.urlopen(http_post_request)

            - Use open, with ssl_context

            proxy_server = ConnectProxyServer(params)

            opener = proxy_server.get_urllib_request_https_opener(ProxyProtocol.https, ssl_context)

            poll_request = urllib.request.Request(get_mac_url, headers=device_headers)

            poll_response = opener.open(poll_request)


        Check out HTTPBasicAuthHandler, see:
        https://docs.python.org/3/library/urllib.request.html#urllib.request.HTTPPasswordMgr

        :param protocol: Proxies to use in the session for the proxy server if
        proxy server is enabled, can be ProxyProtocol.https, ProxyProtocol.http
        or ProxyProtocol.none. Default is ProxyProtocol.https.

        :param ssl_context: ssl_context passed to the context in the
        HTTPSHandler. Default is None.

        :param basic_auth:
        HTTPPasswordMgr or similar passed to create HTTPBasicAuthHandler.
        Default is None.

        :return: opener: OpenerDirector from urllib.request.build_opener that
        has ProxyHandler, HTTPSHandler with SSL context and
        HTTPBasicAuthHandler set. The consequent request call can use
        opener.open or urllib.request.urlopen.
        """
        if ssl_context:
            https_handler = urllib.request.HTTPSHandler(context=ssl_context)
        else:
            https_handler = urllib.request.HTTPSHandler()
        if self.is_enabled:
            proxies = self.get_proxies(protocol)
            proxy_handler = urllib.request.ProxyHandler(proxies)
            self.proxies = proxies
        else:
            self.proxies = self.get_empty_proxies_string()

        if basic_auth:
            auth_handler = urllib.request.HTTPBasicAuthHandler(basic_auth)
        else:
            auth_handler = urllib.request.HTTPBasicAuthHandler()

        if self.is_enabled:
            opener = urllib.request.build_opener(proxy_handler, auth_handler, https_handler)
        else:
            opener = urllib.request.build_opener(auth_handler, https_handler)

        # This is needed to able opener to able to call urlopen
        urllib.request.install_opener(opener)
        return opener




# All server configuration fields will be available in the 'params' dictionary.

def str2bool(v):
    if isinstance(v, (bool,int, float)):
        return v
    logging.debug(f"str2bool")
    return v.lower() in ("yes", "true", "t", "1")



# Initalisae a authorization class
class Authorization:
    def __init__(self , inargs , outargs):
        logging.debug(f"Authorization")
        self._inargs = inargs
        self._outargs = outargs
        self.url = self._inargs.get("connect_ciscodnacapp_url")  # Server URL


        
    # ***** START - AUTH API CONFIGURATION ***** #
        self.timeout = 1800  # 30 minutes from now
        self.now = datetime.utcnow()
        self.timeout_datetime = self.now + timedelta(seconds=self.timeout)
        self.epoch_time = int((self.now - datetime(1970, 1, 1)).total_seconds())
        self.epoch_timeout = int((self.timeout_datetime - datetime(1970, 1, 1)).total_seconds())
        return


    def Acquire_Authorization(self):
        logging.debug(f"Acquire_Authorization")
#        return (True)
        self.sslverify=str2bool(self._inargs.get("connect_ciscodnacapp_sslverify"))
        self.url = self._inargs.get('connect_ciscodnacapp_url')
        self.headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json','Accept-Encoding' : 'gzip, deflate' , 'Connection' : 'keep-alive' }


        self.headers['Authorization']=self.auth


        logging.debug ("Headers: " + str(self.headers))
        self.token_url = self.url + "/dna/system/api/v1/auth/token"
        logging.debug(f"CiscoDNACApp auth " + self.auth)
        logging.debug(f"SSL Verify :" + str(self.sslverify))
        logging.debug(f"Get token url is: " + str(self.token_url))
        try:
            self.proxy_server = ConnectProxyServer(self._inargs)
            # This will close the session when exiting the block.
            # If use session =, then the session can be reused from the connection pool until close
            with self.proxy_server.get_requests_session(ProxyProtocol.all, headers=self.headers) as session:
                logging.debug(f"Making the following URL request :" + str(self.token_url) + " verify: " + str(self.sslverify))
                post_response = session.post(self.token_url,headers=self.headers,  timeout=60,verify=self.sslverify)
                logging.debug(f"Post status code: " + str(post_response.status_code))
                if 200 == post_response.status_code:
                    logging.debug(f"Authorize response encoding: " + str(post_response.encoding))
                    # response.json() has the return info in json format. Can use response.text for a string.
                    self._inargs["connect_ciscodnacapp_authorization_token"] = post_response.json().get('Token')
                    logging.debug(str(self._inargs['connect_ciscodnacapp_authorization_token']))
                    return (self._inargs["connect_ciscodnacapp_authorization_token"])
                else:
                    self._outargs["error"] = post_response.reason
                    return (None)


        except Exception as e:
            emsg="Authorize failed error: " + str(e)
            logging.debug(emsg)
            self._outargs["error"] = emsg
            return (None)


    def basic_auth(self,username,password):
        token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
        self._inargs["connect_ciscodnacapp_auth_id"] = token 
        return f'Basic {token}'

    # Get DANC Toke from username & password
    def GetDNACTokenFromUserNamePassword(self):
    
        self.dnac_ip = self._inargs.get("connect_ciscodnacapp_url")
        self.dnacusername = self._inargs.get("connect_ciscodnacapp_dnacusername")
        self.dnacpassword = self._inargs.get("connect_ciscodnacapp_dnacpassword")
        self.dnacversion = self._inargs.get("connect_ciscodnacapp_dnacversion")

        self.TokenHeader = self.basic_auth(self.dnacusername,self.dnacpassword)

        
        # POST token API URL
        post_url = self.dnac_ip + "/api/system/" + self.dnacversion + "/auth/token"
        # All DNAC REST API request and response content type is JSON.
        self.sslverify=str2bool(self._inargs.get("connect_ciscodnacapp_sslverify"))
        
        self.headers={"Content-Type":"application/json"}
        self.headers['Authorization'] = self.TokenHeader
        try:
            logging.debug(f"DNAC API Headers: " + str(self.headers))
            logging.debug(f"DNAC API URL: " + str(post_url))
            self.proxy_server = ConnectProxyServer(self._inargs)
            # This will close the session when exiting the block.
            # If use session =, then the session can be reused from the connection pool until close
            with self.proxy_server.get_requests_session(ProxyProtocol.all, headers=self.headers) as session:
                logging.debug(f"Making the following URL request :" + str(post_url) + " verify: " + str(self.sslverify))
                post_response = session.post(post_url,headers=self.headers ,timeout=60,verify=self.sslverify)
                logging.debug(f"Post status code: " + str(post_response.status_code))
                if 200 == post_response.status_code:
                    self.data=post_response.json()
                    self.Token=self.data['Token']
                    self._inargs["connect_ciscodnacapp_authorization_token"] = self.Token
                    return (self.Token)
                else:                    
                    return (None)
        except exception as e:
            logging.debug(f"Response: {e}")
        return (None)



    def GetCAAPIToken(self):
        logging.debug(f"GetCAAPIToken")
#        return (True)

        self.url=self._inargs.get('connect_ciscodnacapp_caurl')
        self.authortokenurl="/fsum/oauth2.0/token"
        self.api_url=self.url + self.authortokenurl
        self.headers={"Content-Type":"application/json", "Accept": "*/*", "Accept-encoding": "identity"}
        self.username=self._inargs.get("connect_ciscodnacapp_causername")
        self.password=self._inargs.get("connect_ciscodnacapp_capassword")
        self.data="username=" + self.username + "&password=" + self.password + "&grant_type=password&client_id=fs-oauth-client"
        self.api_url+="?"+self.data
        try:
            logging.debug(f"CounterACT API Headers: " + str(self.headers))
            logging.debug(f"CounterACT Data: " + str(self.data))
            logging.debug(f"CounterACT API URL: " + str(self.api_url))
            httpresponse = requests.post(self.api_url,headers=self.headers, verify=False)
            logging.debug(f"CounterACT REST API Response: " + str(httpresponse.status_code))
            if (httpresponse.status_code == 200):
                self.data=httpresponse.json()
                self.Token=self.data['access_token']
                return (self.Token)
            else:
                return (None)
        except exception as e:
            logging.debug(f"Response: {e}")
        return (None)



class CiscoDNACPollClass:
    def __init__(self , inargs , outargs):
        self._inargs = inargs
        self._outargs = outargs
        logging.debug(f"Creating Poll Class variables")
        self.AuthorClass=Authorization(self._inargs,self._outargs)
#        self.AuthToken=self.AuthorClass.Acquire_Authorization()
        self.caurl=self._inargs.get("connect_ciscodnacapp_caurl")
        self.addswitchesurl="/switch/api/v1/switches"
        self.getswitches="/switch/api/v1/switches/summary"
        self.switchapirate=self._inargs.get('connect_ciscodnacapp_emapirate')
        self.switch_managers=self._inargs.get('connect_ciscodnacapp_switchmanagers')
        self.switch_profiles=self._inargs.get('connect_ciscodnacapp_switchprofiles')
        self.url = self._inargs.get("connect_ciscodnacapp_url")  # Server URL
        self.sslverify=str2bool(self._inargs.get("connect_ciscodnacapp_sslverify"))

        self.clearswitches=str2bool(self._inargs.get('connect_ciscodnacapp_clearswitches'))
        logging.debug(f"SSL Verify: " + str(self.sslverify))

        self.newresponse={}
        self.endpoints = []
    # Mapping between API response fields to CounterACT properties
        logging.debug(f"Poll class created")
        return



    def GetEyeSightToken(self):
        logging.debug(f"GetEyeSightToken")
        self.CAToken=self.AuthorClass.GetCAAPIToken()
        return  self.CAToken


    def GetCurrentSwitches(self):
        logging.debug(f"GetSwitchSUmmary")
        try:
            api_summary_url=self.caurl + self.getswitches
            headers={"Content-Type" : "application/json", "Accept" : "application/json" , "Accept-encoding" : "identity"}
            logging.debug ("Token Headers: " + str(headers))
            Token=self.GetEyeSightToken()
            if (Token):       
                headers['Authorization'] = "Bearer " + Token
                try:
                    httpresponse = requests.get(api_summary_url,headers=headers, verify=False)              
                    if (httpresponse.status_code == 200):
                        logging.debug(f"Switch read summary successfully")
                        rdata=httpresponse.json()
                        time.sleep(int(self.switchapirate))
                        return rdata
                except Exception as e:
                    logging.debug (e)
                    return None
                

        except Exception as e:
            logging.debug ({e})
            return None
    
    

    def UpdateSwitchAPI(self,DelJsonList,AddJsonList):
        logging.debug(f"UpdateSwitchAPI")
        try:
            api_url=self.caurl + self.addswitchesurl
            headers={"Content-Type":"application/json", "Accept": "*/*", "Accept-encoding": "identity"}
            logging.debug ("Token Headers: " + str(headers))
            logging.debug(f"Api URL " + str(api_url))
            logging.debug(f"Add list: " + str(AddJsonList))
            logging.debug(f"Delete list: " + str(DelJsonList))
            logging.debug(f"API Headers: " + str(headers))
            Delsum = sum(map(len, DelJsonList.values()))
            Addsum = sum(map(len, AddJsonList.values()))
            if Delsum > 0 and self.clearswitches == True:
                logging.debug(f"Clear switches allowed")
                Token=self.GetEyeSightToken()
                if (Token):
                    headers['Authorization'] = "Bearer " + Token
                    try:
                        httpresponse = requests.delete(api_url,headers=headers,data=json.dumps(DelJsonList), verify=False)
                        if (httpresponse.status_code == 200):
                            logging.debug(f"Switch delete successfully")
                        else:
                            logging.debug(f"Switch delete failed:")
                            rdata=httpresponse.json()
                            errors=rdata['errors']
                            logging.debug(f"{errors}")
                            httpresponse.raise_for_status()
                    except Exception as e:
                        logging.debug (e)
                # Need to wait 60 second before continuing.
                time.sleep(int(self.switchapirate))
            else:
                if self.clearswitches == False:
                    logging.debug(f"Delete switches disabled")
                else:
                    logging.debug(f"No switch items to delete")
            if Addsum > 0:
                Token=self.GetEyeSightToken()
                if (Token):
                    headers['Authorization'] = "Bearer " + Token
                    try:
                        httpresponse = requests.post(api_url,headers=headers,data=json.dumps(AddJsonList), verify=False)
                        if (httpresponse.status_code == 200):
                            logging.debug(f"Switch updated successfully")
                        else:
                            logging.debug(f"Switch update failed:")
                            rdata=httpresponse.json()
                            errors=rdata['errors']
                            logging.debug(f"{errors}")
                            httpresponse.raise_for_status()
                    except Exception as e:
                        logging.debug(f"{e}")
                        return False
                else:
                    logging.debug ("CounterACT API Token retrieve error")
            else:
                logging.debug(f"No switch items to add")
        except Exception as e:
            logging.debug ({e})
        return True



    def dict_compare(self,d1, d2):
        logging.debug(f"dict_compare")
        d1_keys = set(d1.keys())
        d2_keys = set(d2.keys())
        shared_keys = d1_keys.intersection(d2_keys)
        added = d1_keys - d2_keys
        removed = d2_keys - d1_keys
        modified = {o : (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
        same = set(o for o in shared_keys if d1[o] == d2[o])
        return added, removed, modified, same

# COnvert list to dictonary

    def Convert(self,lst):
        logging.debug(f"Converting")
        res_dct = map(lambda i: (lst[i], lst[i+1]), range(len(lst)-1)[::2])
        return dict(res_dct)

    def stringtolist(self,x):
        logging.debug(f"stringtolist")
        mylist=[]
        for i in range(0,len(x),2):
            mylist.append(x[i])
        return mylist

    def string_to_splitted_array(self,data,delimeters):
        logging.debug(f"string_to_splitted_array")
        #result list
        res = []
        # we will add chars into sub_str until
        # reach a delimeter
        sub_str = ''
        for c in data: #iterate over data char by char
            # if we reached a delimeter, we store the result 
            if c in delimeters: 
                # avoid empty strings
                if len(sub_str)>0:
                    # looks like a valid string.
                    res.append(sub_str)
                    # reset sub_str to start over
                    sub_str = ''
            else:
                # c is not a deilmeter. then it is 
                # part of the string.
                sub_str += c
        # there may not be delimeter at end of data. 
        # if sub_str is not empty, we should att it to list. 
        if len(sub_str)>0:
            res.append(sub_str)
        # result is in res 
        return res

    # Get switch Profile name to use
    def GetSwitchProfile(self,ip,description):
        logging.debug(f"GetSwitchProfile")
        profiledata=ip + "," + description.lower()
        try:
            for profile in self.switch_profiles.split('\n'):
                matchpattern=profile.split('|',1)[0].lower()
                realprofileName=matchdata=profile.split('|',1)[1]
                matchdata=realprofileName.lower()
                match = re.search(matchpattern,profiledata)
                if match:
                    break
        except Exception as e:
            logging.debug(f"Get switch profile error: " + str(e))
        return realprofileName



    def time_random(self):
        return time() - float(str(time()).split('.')[0])

    def gen_random_range(self,min, max):
        return int(self.time_random() * (max - min) + min)


    def GetSwitchManager(self):
        logging.debug(f"GetSwitchManager")
        SwitchManager=self.switch_managers.split(',')
        cnt_len=len(SwitchManager)
#        ref1=self.gen_random_range(1, cnt_len)-1
        ref1=random.randint(1,cnt_len)-1
        return (SwitchManager[ref1])
    


    def PollSwitchData(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
#        return (True)
#        # CONFIGURATION

        logging.debug(f"CiscoDNACApp polling.")
        # Check if we have valid auth token or not before processing.
        if self._inargs.get("connect_ciscodnacapp_authorization_token"):
            # ***** PART 2 - QUERY FOR DEVICES  ***** #
            jwt_token = self._inargs.get("connect_ciscodnacapp_authorization_token")
            network_device_switches_url = self.url + "/dna/intent/api/v1/network-device?family=Switches and Hubs"
            network_device_routers_url = self.url + "/dna/intent/api/v1/network-device?family=Routers"            
            device_headers = {"Content-Type": "application/json" , "Accept" : "application/json" , "x-auth-token" : "" + str(jwt_token) + ""}
            try:
                # Create proxy server
                # acquire_authorization()
                # proxy_server = ciscodnacapp_library.ConnectProxyServer(self._inargs)
                proxy_server = ConnectProxyServer(self._inargs)
                logging.debug(f"Get network url is:" + network_device_switches_url)
                # This will close the session when exiting the block.
                # If use session =, then the session can be reused from the connection pool until close
                with proxy_server.get_requests_session(ProxyProtocol.all, headers=device_headers) as session:
                # Example of check what proxy is set for the session
                    logging.debug(f"Proxies:" + str(proxy_server.proxies))
                    # Make post call to get token, set time out 10 seconds
                    get_response = session.get(network_device_switches_url,timeout=60,verify=self.sslverify)
                    logging.debug(f"Authorize response code for switches:"  + str(get_response.status_code))
                    if 200 == get_response.status_code:
                        logging.debug(f"Authorize response encoding: " + str(get_response.encoding))
                        # response.json() has the return info in json format. Can use response.text for a string.
                        self.switches = get_response.json()
##                        with open('DH.json', 'r') as file:
##                            data = file.read()
##                            self.switches = json.loads(data)

                        self.newresponse.update(self.switches)
                        get_response = session.get(network_device_routers_url,timeout=60,verify=self.sslverify)
                        logging.debug(f"Authorize response code for routers:"  + str(get_response.status_code))
                        if 200 == get_response.status_code:
                            logging.debug(f"Authorize response encoding: " + str(get_response.encoding))
                            self.routers = get_response.json()
                            self.newresponse['response'] += self.routers['response']

                        logging.debug(f"Last response has no items")
                        # Taking data from the switch plugin instead.
                        APIData=self.GetCurrentSwitches() 
                        item = 0
                        self.lastresponse=get_response.json()
                        for IData in APIData['switches']:
                            itemdict={}
                            if  (IData['alerts'] != None and 'Not a switch' not in IData['alerts']):
                                itemdict['family'] = 'Switches and Hubs' 
                                itemdict['type'] = IData['vendor'] 
                                itemdict['description'] = IData['comment']                                                           
                                itemdict['macAddress'] = '11:22:33:44:55:' + str(item + 10)
                                itemdict['lastUpdateTime'] = '1684709551667'
                                itemdict['managementIpAddress']  = IData['managementAddress']
                                itemdict['hostname'] = 'Eyesight switch'
                                itemdict['softwareType'] = '15.1'
                                itemdict['role'] = 'Access'
                                self.lastresponse['response'].append(itemdict)
                                item+=1 

                            
                        logging.debug(f"Current response: " + str(self.newresponse))
                        CAAPIData=""
                        newlist = 0
                        lastlist =0
                        try:
                            newvalue = self.newresponse['response']
                            orgvalue = self.lastresponse['response']
                            for x in orgvalue:
                                Found=0
                                orgip=(x['managementIpAddress'])
                                for i in newvalue:
                                    newip=(i['managementIpAddress'])
                                    if newip == orgip:
                                        Found=1
                                if Found == 0:
                                    logging.debug(f"Adding Del switch to list of switches")
                                    CAAPIData+=("Del,")
                                    CAAPIData+=(x['managementIpAddress'] + ",")
                                    CAAPIData+=(self.GetSwitchManager() + ",")
                                    CAAPIData+=(self.GetSwitchProfile(x['managementIpAddress'],x['role']) + ',')
                                    CAAPIData+=(x['hostname'] + ",")
                                    CAAPIData+=("\n")
                                lastlist += 1    
                            logging.debug(f"Finnished processing delete switch lists")
                            for x in newvalue:
                                Found=0
                                orgip=(x['managementIpAddress'])
                                for i in orgvalue:
                                    newip=(i['managementIpAddress'])
                                    if newip == orgip:
                                        Found=1
                                if Found == 0:
                                    logging.debug(f"Adding switch to list of switches")
                                    CAAPIData+=("Add,")
                                    CAAPIData+=(x['managementIpAddress'] + ",")
                                    CAAPIData+=(self.GetSwitchManager() + ",")
                                    CAAPIData+=(self.GetSwitchProfile(x['managementIpAddress'],x['role']) + ',')
                                    CAAPIData+=(x['hostname'] + ",")
                                    CAAPIData+=("\n")
                                newlist += 1
                            logging.debug(f"Finnished processing " + str(newlist) + "new items, and " + str(lastlist) + " delete items")
                        except Exception as e:
                            logging.debug(f"Possible error processing switch lists at Newlist" + str(newlist) + " lastlist" + str(lastlist) + " " + str(e))

                        if "Add" or "Del" in CAAPIData:
                            FilteredAPIData=""
                            parsing_data="NoProfile"
                            for line in CAAPIData.split('\n'):
                                logging.debug(f"Line : " + str(line))
                                match =  re.search(parsing_data,line)
                                if match == None:
                                    FilteredAPIData+=line + '\n'
                            logging.debug(f"Filtered data: " + str(FilteredAPIData))

                        try:
                            AddJsonData={"switchToAddList":[]}
                            DelJsonData={"switchesToDeleteManagementAddresses":[]}
                            DictAdd={}
                            DictDel={}
                            for Data in FilteredAPIData.split('\n'):
                                match = re.search('Add', Data)
                                if match:
                                    DictAdd={ "comment" : Data.split(',')[4],
                            "connectingAppliance" : Data.split(',')[2],
                            "managementAddress" : Data.split(',')[1],
                            "profileName" :Data.split(',')[3]}
                                    AddJsonData["switchToAddList"].append(DictAdd)
                                    logging.debug(f"Add switches: " + str(AddJsonData))
                                match = re.search('Del', Data)
                                if match:
                                    DelJsonData["switchesToDeleteManagementAddresses"].append(Data.split(',')[1])
                                    logging.debug(f"Delete switches: " + str(DelJsonData))

                            self.lastresponse = self.newresponse
                        
                            if (self.UpdateSwitchAPI(DelJsonData,AddJsonData)) == True:
                                self._outargs["succeeded"] = True
                                self._outargs["result_msg"] = "Successfully processed switch update"
                                return (True)
                            else:
                                self._outargs["succeeded"] = False
                                self._outargs["result_msg"] = "Switch update failed"
                                return (False)

                        except Exception as e:
                            logging.debug(f"Update error: " + str(e))


                    elif 401 == get_response.status_code:
                        logging.debug(f"401 Error")
                        results = get_response.json()
                        logging.debug(f"Results: {results}")
                        return (False)
                    else:
                        self._outargs["error"] = get_response.reason

            except Exception as e:
                self._outargs["error"] = "Could not retrieve endpoints."
                logging.debug(f"Get error: " + str(e))
                return (False)
        else:
            self._outargs["error"] = "Unauthorized"
            return (False)


# Combbins all other classes into 1 object
class CiscoDNACTopClass:
    def __init__(self , inargs , outargs):
        self._inargs = inargs
        self._outargs = outargs
        self.CiscoDNACPoll=CiscoDNACPollClass(self._inargs , self._outargs)
        return
    
    def GetCAAPIToken(self):
        if (self.CiscoDNACPoll.AuthorClass):
            return (self.CiscoDNACPoll.AuthorClass.GetCAAPIToken())
        else:
            return (False)
        
    def GetAuthorClassToken(self):
        if (self.CiscoDNACPoll.AuthorClass):
            return(self.CiscoDNACPoll.AuthorClass.Acquire_Authorization())
        else:
            return (False)
        
    def GetTokenWithUserName(self):
        if (self.CiscoDNACPoll.AuthorClass):
            return(self.CiscoDNACPoll.AuthorClass.GetDNACTokenFromUserNamePassword())
        else:
            return (False)

    def PolSwitchData(self):
        if (self.CiscoDNACPoll):
            return (self.CiscoDNACPoll.PollSwitchData())
        else:
            return (False)
        
    def GetSwitchData(self):
        if (self.CiscoDNACPoll):
            return (self.CiscoDNACPoll.GeturrentSwitches())
        else:
            return (False)     
        




#api_details ={}
#connect_app_name = "myapp"
#subscriber_api_key ="mykey"
#api_details["subscriber_api_key"] = subscriber_api_key
#api_details["lookback"] = "lookback"
#api_details["ssl_verify"] = True

#logging.debug(f"Got app_name {connect_app_name}")
#db_util = PersistUtil(connect_app_name)
#db_util.save("cached", "subscriber_api_key", api_details["subscriber_api_key"])

#db_util.save("param-tests", "params", str(params))

#saved_key = db_util.get("cached", "subscriber_api_key")
#logging.debug(f"api key saved: {saved_key}")

#saved_params = db_util.get("param-tests", "params")
#logging.debug(f"saved parameters {saved_params}")

#db_util.cleanup_table("param-tests")




#logging.basicConfig(level=logging.DEBUG)

#mydb=MyDB('cached')
#itemdict={}
#itemdict['type'] = 'Cisco Dummy Switch'
#itemdict['lastUpdateTime'] = '1684709551666'
#itemdict['managementIpAddress']  = '1.1.1.2'
#itemdict['description'] = 'Dummy switch'
#itemdict['hostname'] = 'Dummy switch 1'
#itemdict['softwareType'] = '15.2'
#itemdict['macAddress'] = '112233445577'
#mydb.SaveDict(itemdict)

#test={}
#test= mydb.GetDict()


#MyCiscoDNAC=CiscoDNACTopClass(params,response)
#AuthorToken = MyCiscoDNAC.GetTokenWithUserName()
#CAAPIToken = MyCiscoDNAC.GetCAAPIToken()
#MyCiscoDNAC.PolSwitchData()
#exit

#Mydata = {'key1' : 'Value1','key2' : 'Value2','key3': 'Value3'}
#logging.basicConfig(level=logging.DEBUG)
#mydb=MyDB('cached')

#RData = mydb.GetDict()
#if RData == None:
#    logging.debug(f"No Data")
#else:
#    logging.debug(f"Data found")

#mydb.SaveDict(Mydata)
#RData = {}
#RData = mydb.GetDict()
#for key, item in RData.items():

#mydb.SaveData('key1','Valuex')
#value = mydb.GetData('key1')
#mydb.Cleanup()
#mydb.Delete('key1')
#mydb.ClearupTable()

