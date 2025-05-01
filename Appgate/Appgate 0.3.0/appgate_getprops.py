###############################################################################
# Resovle additional properties. Requires username, IdP and device ID, which  #
# we can initially get from syslog messages, otherwise it's useless.          #
# Use polling instead in case syslog processing is not set up.                #
###############################################################################

# Get target user
user = params['connect_appgatesdp_user']
idp = params['connect_appgatesdp_idp']
deviceId = params['connect_appgatesdp_id']

# Initialize API object with app options
ag = appgate_api.appgate_api(params, ssl_verify)
if (params["connect_authorization_token"]):
    session = { 'deviceId': deviceId,'username': user,'providerName': idp }
    details = ag.get_session_details(session)
    if details:
        response = {}
        properties = {}
        properties["connect_appgatesdp_sites"] = ""
        for property in details:
            if not "ip" in response:
                response["ip"] = details[property]['systemClaims']['tunIPv4']
                properties["connect_appgatesdp_extip"] = details[property]['systemClaims']['clientSrcIP']
                properties["connect_appgatesdp_hostname"] = details[property]['deviceClaims']['os']['hostname']
                properties["connect_appgatesdp_country"] = details[property]['systemClaims']['geoIp']['countryCode']
                properties["connect_appgatesdp_isdomain"] = details[property]['deviceClaims']['isDomain']
                properties["connect_appgatesdp_isuseradmin"] = details[property]['deviceClaims']['isUserAdmin']
                properties["connect_appgatesdp_isfwenabled"] = details[property]['deviceClaims']['isFirewallEnabled']
                properties["connect_appgatesdp_os"] = details[property]['deviceClaims']['os']['name']
            properties["connect_appgatesdp_sites"] += details[property]['site'] + '\n'
        properties["connect_appgatesdp_sites"] = properties["connect_appgatesdp_sites"][:-1]
        response["properties"] = properties
    logging.debug(response)
        