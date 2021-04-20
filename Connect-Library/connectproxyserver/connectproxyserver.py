"""
Copyright © 2021 Forescout Technologies, Inc.

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
import requests
import urllib.request
from requests.auth import HTTPProxyAuth
from enum import Enum


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
    def __init__(self, params):
        is_proxy_enabled = params.get("connect_proxy_enable")
        logging.debug("Proxy enabled status: " + str(is_proxy_enabled))
        if is_proxy_enabled == "true":  # Cover the case is_proxy_enable is None, it is not equal to "true"
            #: A boolean to indicate if the proxy server is enabled
            self.is_enabled = True
        else:
            self.is_enabled = False
        if self.is_enabled:
            #: Proxy server ip. None if proxy server is not enabled.
            # Required if proxy server is enabled, otherwise, a ValueError is
            # raised
            self.ip = params.get("connect_proxy_ip")
            if not self.ip:
                raise ValueError("Proxy IP is empty or null.")
            #: Proxy server port. None if proxy server is not enabled.
            # Required if proxy server is enabled, otherwise, a ValueError is
            # raised
            self.port = params.get("connect_proxy_port")
            if not self.port:
                raise ValueError("Proxy port is empty or null.")

            # Username and password can be null
            #: Proxy server username. (Optional), None if proxy server is not enabled.
            self.username = params.get("connect_proxy_username")
            #: Proxy server password. (Optional), None if proxy server is not enabled.
            self.password = params.get("connect_proxy_password")
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
            logging.debug("Clear connection pool.")
            session.mount("https://", adapter)
            session.mount("http://", adapter)

    @staticmethod
    def set_default_connection_pool():
        """ Default connection pool setting """
        with requests.Session() as session:
            logging.debug("Set default connection pool.")
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
                verify=ssl_verify) as session:
                post_response = session.post(token_url, json=payload)
                delete_response = session.delete(delete_user_url)

            session will be closed on exiting the with block

            - Use session with SSL context in post request (which accepts everything requests.request accepts)

            proxy_server = ConnectProxyServer(params)

            session =proxy_server.get_requests_session(ProxyProtocol.https,headers=device_headers, verify=ssl_verify)

            add_response = session.post(add_user_url, json=json_body)

            get_response = session.get(get_user_url)

            proxy_server = ConnectProxyServer(params)

            session = proxy_server.get_requests_session(ProxyProtocol.https)

            add_response = session.post(add_user_url, json=json_body, verify=ssl_verify, headers=headers)

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
