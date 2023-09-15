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
import urllib.request


def get_proxy_dict(proxy_basic_auth_ip, proxy_port, proxy_username, proxy_password):
	"""
	Generates the proxy dictionary object to be used in the handle_proxy_configuration() function, and as the 'proxies' argument in requests library API call
	:return: proxy dictionary for both http and https connections
	"""
	logging.debug("PROXY IS ENABLED --> Generating proxy dictionary...")

	logging.debug("Proxy Basic Auth IP: " + proxy_basic_auth_ip)
	logging.debug("Proxy Port: " + proxy_port)
	logging.debug("Proxy Username: " + proxy_username)

	if proxy_username is None or proxy_password is None: 
		proxy_dict = {
		    "http": "http://{}:{}".format(proxy_basic_auth_ip, proxy_port),
		    "https": "https://{}:{}".format(proxy_basic_auth_ip, proxy_port)
		}
	else:
		proxy_dict = {
		    "http": "http://{}:{}@{}:{}".format(proxy_username, proxy_password, proxy_basic_auth_ip, proxy_port),
		    "https": "https://{}:{}@{}:{}".format(proxy_username, proxy_password, proxy_basic_auth_ip, proxy_port)
		}

	#logging.debug("PROXY HTTP URL: {}".format(proxy_dict.get("http")))
	#logging.debug("PROXY HTTPS URL: {}".format(proxy_dict.get("https")))
	return(proxy_dict)


def handle_proxy_configuration(proxy_enabled, proxy_basic_auth_ip, proxy_port, proxy_username, proxy_password, ssl_context):
	"""
	Handles the proxy server in the case that proxy was enabled by the user
	:return: opener that handles both proxy and no proxy ONLY for the urllib library
	"""
	logging.debug("Proxy Enabled: " + proxy_enabled)

	# creating the https handler object
	https_handler = urllib.request.HTTPSHandler(context=ssl_context)

	# with proxy handler
	if proxy_enabled == "true":	
		# get proxy_dict
		proxy_dict = get_proxy_dict(proxy_basic_auth_ip, proxy_port, proxy_username, proxy_password)
		proxy_handler = urllib.request.ProxyHandler(proxy_dict)
		opener = urllib.request.build_opener(proxy_handler, https_handler)
		logging.debug("Opener object with Proxy support ENABLED")
	else:
		# without proxy handler
		opener = urllib.request.build_opener(https_handler)
		logging.debug("Opener object with Proxy DISABLED")
	return(opener)
