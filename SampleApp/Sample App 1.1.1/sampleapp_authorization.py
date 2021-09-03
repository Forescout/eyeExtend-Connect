import jwt  # PyJWT version 1.6.1 as of the time of authoring
import uuid
from datetime import datetime, timedelta
from connectproxyserver import ConnectProxyServer, ProxyProtocol

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = params.get("connect_sampleapp_url")  # Server URL
tenant = params.get("connect_sampleapp_tenant_id")  # Tenant ID
app = params.get("connect_sampleapp_application_id")  # Application ID
secret = params.get("connect_sampleapp_application_secret")  # Application Secret

# ***** START - AUTH API CONFIGURATION ***** #
timeout = 1800  # 30 minutes from now
now = datetime.utcnow()
timeout_datetime = now + timedelta(seconds=timeout)
epoch_time = int((now - datetime(1970, 1, 1)).total_seconds())
epoch_timeout = int((timeout_datetime - datetime(1970, 1, 1)).total_seconds())
jti_val = str(uuid.uuid4())
claims = {
    "exp": epoch_timeout,
    "iat": epoch_time,
    "iss": "http://cylance.com",
    "sub": app,
    "tid": tenant,
    "jti": jti_val,
}

encoded = jwt.encode(claims, secret, algorithm='HS256')
payload = {"auth_token": encoded.decode("utf-8")}
headers = {"Content-Type": "application/json; charset=utf-8"}
response = {"token": ""}
token_url = url + "/auth/v2/token"
logging.debug("SampleApp auth.")
try:
    proxy_server = ConnectProxyServer(params)
    logging.debug(f"Get token url is: {token_url}")
    # This will close the session when exiting the block.
    # If use session =, then the session can be reused from the connection pool until close
    with proxy_server.get_requests_session(ProxyProtocol.all, headers=headers, verify=ssl_verify) as session:
        # Example of check what proxy is set for the session
        logging.debug(f"Proxies: {proxy_server.proxies}")
        # Make post call to get token, set time out 10 seconds
        post_response = session.post(token_url, json=payload, timeout=10)

        # Can also write as the following as example
        # session = proxy_server.get_requests_session(ProxyProtocol.http)
        # session.headers = headers
        # post_response = session.post(token_url, json=payload, verify=ssl_verify)

        # # Use urlopen example
        # proxy_server = ConnectProxyServer(params)
        # # Pass to use what HTTPS or HTTP or both in the protocol, pass down the ssl_context
        # opener = proxy_server.get_urllib_request_opener(ProxyProtocol.https, ssl_context)
        # auth_request = urllib.request.Request(token_url, headers=headers,
        # data=bytes(json.dumps(payload), encoding="utf-8"))
        # # Use opener.open to get the request ( you can use urlopen as well, look at resolve script
        # auth_response = urllib.request.urlopen(auth_request)
        # post_response = json.loads(auth_response.read().decode("utf-8"))
        # logging.debug("Response json: {}".format(json.dumps(post_response)))
        # jwt_token = post_response.get('access_token')  # access_token to be passed to GET request
        # response["token"] = jwt_token
        logging.debug(f"Authorize response code: {post_response.status_code}")
        if 200 == post_response.status_code:
            logging.debug(f"Authorize response encoding: {post_response.encoding}")
            # response.json() has the return info in json format. Can use response.text for a string.
            response["token"] = post_response.json().get('access_token')
        else:
            response["error"] = post_response.reason
        #
        # one_proxy_server = ConnectProxyServer(params)
        # proxies = one_proxy_server.get_proxies(ProxyProtocol.all)
        # if one_proxy_server.is_enabled:
        #     res = requests.post(token_url, proxies=proxies, headers=headers, json=payload, verify=ssl_verify)
        # else:
        #     res = requests.post(token_url, proxies=None, headers=headers, json=payload, verify=ssl_verify)
        #
        # logging.debug(f"No lib call. Get response {res.text}")

except Exception as e:
    logging.debug(f"Authorize failed error: {str(e)}")
    response["error"] = f"Failed to get token: {str(e)}"
