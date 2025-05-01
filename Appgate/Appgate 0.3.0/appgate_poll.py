###############################################################################
# Get a list of active sessions from Controller and details for each session. #
# TODO: resolve more session properties.                                      #
###############################################################################

# Prepare response dictionary
response = {}
endpoints = []

# Initialize API object with app options
ag = appgate_api.appgate_api(params, ssl_verify)

# If we have auth token, start polling
if (params["connect_authorization_token"]):
    r = ag.get_sessions()
    if r:
        for sessions_for_dn in range(0, len(r)):
            details = ag.get_session_details(r[sessions_for_dn])
            if details:
                endpoint = {}
                properties = {}
                properties["connect_appgatesdp_sites"] = ""
                for property in details:
                    if not "ip" in endpoint:
                        endpoint["ip"] = details[property]['systemClaims']['tunIPv4']
                        properties["connect_appgatesdp_extip"] = details[property]['systemClaims']['clientSrcIP']
                        properties["connect_appgatesdp_id"] = ''.join(r[sessions_for_dn]['deviceId'].split('-'))
                        properties["connect_appgatesdp_user"] = r[sessions_for_dn]['username']
                        properties["connect_appgatesdp_idp"] = r[sessions_for_dn]['providerName']
                        properties["connect_appgatesdp_hostname"] = r[sessions_for_dn]['hostname']
                        properties["connect_appgatesdp_country"] = details[property]['systemClaims']['geoIp']['countryCode']
                        properties["connect_appgatesdp_isdomain"] = details[property]['deviceClaims']['isDomain']
                        properties["connect_appgatesdp_isuseradmin"] = details[property]['deviceClaims']['isUserAdmin']
                        properties["connect_appgatesdp_isfwenabled"] = details[property]['deviceClaims']['isFirewallEnabled']
                        properties["connect_appgatesdp_os"] = details[property]['deviceClaims']['os']['name']
                    properties["connect_appgatesdp_sites"] += details[property]['site'] + '\n'
                properties["connect_appgatesdp_sites"] = properties["connect_appgatesdp_sites"][:-1]
                endpoint["properties"] = properties
                endpoints.append(endpoint)
            response['endpoints'] = endpoints
            logging.debug(response)
        