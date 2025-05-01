from requests import Request, Session, exceptions
import logging

class appgate_api:
    
###########################################################################
# Main class to handle communications with an Appgate SDP controller.     #
# Input parameters:                                                       #
# params : dictionary containing app settings defined in system.conf      #
# verify : SSL verification option, defined by "certification validation" #
# switch in app configuration. For this specific app, it can be either    #
# False, or contain path to CA certs directory.                           #
###########################################################################

    def __init__ (self,params={}, verify=True):
        
        self.controller = params.get("connect_appgatesdp_fqdn")
        self.name = params.get("connect_appgatesdp_apiuser")
        self.idp = params.get("connect_appgatesdp_apiidp")
        self.password = params.get("connect_appgatesdp_apipass")
        self.token = params.get('connect_authorization_token')
        self.ssl_verify = verify
        self.api_version = params.get('connect_appgatesdp_apiver')
        self.headers = { "Content-Type": "Application/json", "Accept": "application/vnd.appgate.peer-v" + self.api_version + "+json" }
        self.deviceId = params.get("connect_appgatesdp_uuid")
    
    def call (self,url,method,data=''):
        
    ###########################################################################
    # Handles HTTP requests. SSL verification option taken from attributes.   #
    # Input parameters:                                                       #
    # url : url to send requests to, including schema.                        #
    # method : HTTP mathod                                                    #
    # data : data to send. Optional.                                          #
    # Returns full response upon successful call, False otherwise.            #
    ###########################################################################

        headers = self.headers
        if self.token:
            headers['Authorization'] = self.token
        with Session() as s:
            s.verify = self.ssl_verify
            req = Request(method, url, json=data, headers=headers)
            p = req.prepare()
            try:
                r = s.send(p)
                return r
            except Exception as e:
                logging.debug(f'Exception occured upon making HTTP request: {e}')
        return False
    
    def login (self):
        
    ###########################################################################
    # Fetch API token.                                                        #
    # Takes input parmeters from class attributes.                            #
    # Retuns dictionary with HTTP status code and API token upon successful   #
    # HTTP request, otherwise returns False                                   #
    ###########################################################################

        url = self.controller + '/admin/login'
        data = { "providerName": self.idp, "username": self.name, "password": self.password, "deviceId": self.deviceId }
        r = self.call(url,'post',data)
        if r:
            data = r.json()
            if r.status_code == 200:
                self.token = 'Bearer ' + data['token']
            return { 'status_code': r.status_code, 'token': self.token }
        return False
    
    def get_sessions (self,query=''):
        
    ###########################################################################
    # Retrieve list of active sessions.                                       #
    # Takes mandatory input parmeters from attributes. Can take an additional #
    # 'query' argument to filter output. Never used in this app though.       #
    # Retuns JSON object with active sessions upon success, False otherwise.  #
    # TODO: return other HTTP status codes, maybe.                            #
    ###########################################################################

        if query:
            query = '?query=' + query
        url = self.controller + '/admin/stats/active-sessions/dn' + query
        r = self.call(url,'get')
        if r.status_code == 200:
            return r.json()['data']
        logging.debug('Got code ' + r.status_code + 'while getting sessions. Response: ' + r.json())
        return False
        
    def get_session_details (self, session):
        
    ###########################################################################
    # Retrieve details for a specific session.                                #
    # Takes dictionary with following session parameters as input:            #
    # 'deviceId' : Device ID.                                                 #
    # 'username' : User logged in on the device.                              #
    # 'providerName' : IdP used for user login.                               #
    # Retuns JSON object with active sessions upon success, False otherwise.  #
    # TODO: return other HTTP status codes, maybe.                            #
    ###########################################################################

        dn = 'CN=' + ''.join(session['deviceId'].split('-')) + ',CN=' + session['username'] + ',OU=' + session['providerName']
        url = self.controller + '/admin/session-info/' + dn
        r = self.call(url,'get')
        if r.status_code == 200:
            return r.json()['data']
        logging.debug('Got code ' + r.status_code + 'while getting session details. Response: ' + r.json())
        return False

    def blacklist_user (self,user,provider,reason):

    ###########################################################################
    # Blacklists a user (ALL their sessions, not some spesific one)           #
    # Input parameters:                                                       #
    # user : User to blacklist.                                               #
    # provider : IdP for the user.                                            #
    # reason : reason for blacklisting. Also mandatory.                       #
    # Retuns HTTP request status code, if any. False otherwise.               #
    ###########################################################################

        dn = 'CN=' + user + ',OU=' + provider
        url = self.controller + '/admin/blacklist'
        logging.debug(url)
        data = { "userDistinguishedName": dn, "username": user, "providerName": provider, "reason": reason }
        logging.debug(data)
        r = self.call(url,'post',data)
        logging.debug(r.text)
        if r:
            logging.debug(r.text)
            return r.status_code
        return False

    def unblacklist_user (self,user,provider):

    ###########################################################################
    # Removes user from blacklist                                             #
    # Input parameters:                                                       #
    # user : User to blacklist.                                               #
    # provider : IdP for the user.                                            #
    # Retuns HTTP request status code, if any. False otherwise.               #
    ###########################################################################

        url = self.controller + '/admin/blacklist/CN=' + user + ',OU=' + provider
        r = self.call(url,'delete')
        if r:
            return r.status_code
        return False
        
    def revoke_tokens (self,user=None,provider=None,device=None,reason=''):

    ###########################################################################
    # Revoke tokens for the specified sessions.                               #
    # Input parameters:                                                       #
    # user : User to blacklist.                                               #
    # provider : IdP for the user.                                            #
    # Retuns HTTP request status code, if any. False otherwise.               #
    ###########################################################################

        url = self.controller + '/admin/on-boarded-devices/revoke-tokens/'
        dn = ''
        if device:  
            dn += 'CN=' + ''.join(device.split('-')) + ','
        if user:
            dn += 'CN=' + user + ','
        if provider:
            dn += 'OU=' + provider
        logging.debug(url)
        data = { 'distinguishedNameFilter': dn, 'revocationReason': reason }
        logging.debug(data)
        r = self.call(url,'post',data)
        if r.status_code == 200:
            return r.status_code
        logging.error('Got error ' + str(r.status_code) + ' while trying to revoke tokens for user. Message: ' + r.text)
        return False