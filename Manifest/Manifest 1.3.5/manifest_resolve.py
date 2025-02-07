from connectproxyserver import ConnectProxyServer, ProxyProtocol

# Given the params dict, determine if the user has consented to the terms and agreements during setup
def check_consent(params):
  if not params.get('connect_manifest_consent_agreements', False):
    logging.info('You must consent to abide by all applicable terms and agreements between your organization and Manifest Cyber. Please reinstall the integration and agree to the terms.')
    return False
  logging.debug('You agreed to abide by all applicable terms and agreements between your organization and Manifest Cyber. Continuing...')
  return True

# Mapping between SampleApp API response fields to CounterACT properties
manifest_to_ct_props_map = {
  "_id": "connect_manifest_assetid",
  "assetUrl": "connect_manifest_manifesturl",
  "sbomId": "connect_manifest_sbomid",
  "sbomUrl": "connect_manifest_sbomurl",
  "whenUploaded": "connect_manifest_sbomuploaddate",
  "relationshipToOrg": "connect_manifest_sbom_relationship",
  "coordinates": "connect_manifest_coordinates",
  "riskScore": "connect_manifest_riskscore",
  "countTotal": "connect_manifest_countvulnstotal",
  "countCritical": "connect_manifest_countvulnscritical",
  "countHigh": "connect_manifest_countvulnshigh",
  "countMedium": "connect_manifest_countvulnsmedium",
  "countLow": "connect_manifest_countvulnslow",
  "countKev": "connect_manifest_countvulnskev",
  "countVulnerabilities": "--", # This is a placeholder for the nested vuln counts
  "dateCreated": "--", # This is a placeholder for whenUploaded
}

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
manifest_base_url = params.get('connect_manifest_url')
manifest_api_token = params.get('connect_manifest_apitoken')

response = {}
logging.debug("Manifest resolve started...")

if manifest_api_token and check_consent(params):
  # Set headers for requests
  device_headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + str(manifest_api_token)}
  # For properties and actions defined in the 'property.conf' file, CounterACT properties can be added as dependencies.
  # These values will be found in the params dictionary if CounterACT was able to resolve the properties.
  # If not, they will not be found in the params dictionary.
  # vendor, firmware is intentionally not required.
  required_params = ['model_classification', 'firmware_classification']
  if all(key in params and params[key] and params[key] != 'Unknown' for key in required_params):
    givenVendor = params.get("vendor_classification")
    # givenVendor = 'Unknown'
    givenModel = params.get("model_classification")
    # givenModel = '7.20.1'
    givenFirmware = params.get("firmware_classification")
    # givenFirmware = 'm2025le_firmware'
    
    logging.debug(f'vendor is "{givenVendor}", firmware is "{givenFirmware}", model is "{givenModel}"')
    
  # Assemble asset list fetch URL
    fetch_assets_url = manifest_base_url + "/v1/assets/" + urllib.parse.quote(
    '?limit=10&filters=[{ "field": "textSearch", "value": ["'+ givenModel + '", "'+ givenFirmware + '"] }, { "field": "assetActive", "value": "true" }]',
    safe='?&='
  )
    
    logging.debug(f"asset fetch url is: {fetch_assets_url}")

    try:
      # Create proxy server
      proxy_server = ConnectProxyServer(params)
      # Pass to use what HTTPS or HTTP or both in the protocol, pass down the ssl_verify
      with proxy_server.get_requests_session(ProxyProtocol.all, headers=device_headers, verify=ssl_verify) as session:
        # Make any requests we need to make
        # Fetch assets list
        fetch_assets_list_response = session.get(fetch_assets_url, proxies=proxy_server.proxies)
        logging.debug(f"Fetch assets list response code: {fetch_assets_list_response.status_code}")
        if 200 == fetch_assets_list_response.status_code:
          logging.debug(f"Fetch assets list response text: {fetch_assets_list_response.text}")
          request_response = json.loads(fetch_assets_list_response.text)
	
          # All responses from scripts must contain the JSON object 'response'. Host property resolve scripts will 
          # need to populate a 'properties' JSON object within the JSON object 'response'. The 'properties' object will 
          # be a key, value mapping between the CounterACT property name and the value of the property

          properties = {}
          resolvedAssetId = ''

          if request_response and request_response['success'] and request_response['queryInfo']['totalReturn'] == 1:
            return_values = request_response['data'][0]
            logging.debug(f"Resolve response text on 0 element: {request_response['data'][0]}")
            for key, value in return_values.items():
              if key in manifest_to_ct_props_map:
                if key == '_id': # Set our asset ID to use.
                  resolvedAssetId = value
                  properties[manifest_to_ct_props_map[key]] = value
                  properties[manifest_to_ct_props_map['assetUrl']] = manifest_base_url + '/v1/asset/' + value + '?redirect=1'
                elif key == 'sbomId':
                  properties[manifest_to_ct_props_map['sbomId']] = value
                  properties[manifest_to_ct_props_map['sbomUrl']] = manifest_base_url + '/v1/sbom/download/' + value + '?redirect=1'
                elif key == 'dateCreated': # Date asset was first created
                    properties[manifest_to_ct_props_map['whenUploaded']] = value
                elif key == 'countVulnerabilities': # Iterate over vuln counts
                    logging.debug(f"Iterating over countVulnerabilities")

                    vulnCounts = value
                    for key in vulnCounts:
                      if key == 'total':
                        logging.debug(f"Setting MFST property with key: {key}, to value: {vulnCounts[key]}")
                        properties[manifest_to_ct_props_map['countTotal']] = vulnCounts[key]
                      elif key == 'critical':
                        logging.debug(f"Setting MFST property with key: {key}, to value: {vulnCounts[key]}")
                        properties[manifest_to_ct_props_map['countCritical']] = vulnCounts[key]
                      elif key == 'high':
                        logging.debug(f"Setting MFST property with key: {key}, to value: {vulnCounts[key]}")
                        properties[manifest_to_ct_props_map['countHigh']] = vulnCounts[key]
                      elif key == 'medium':
                        logging.debug(f"Setting MFST property with key: {key}, to value: {vulnCounts[key]}")
                        properties[manifest_to_ct_props_map['countMedium']] = vulnCounts[key]
                      elif key == 'low':
                        logging.debug(f"Setting MFST property with key: {key}, to value: {vulnCounts[key]}")
                        properties[manifest_to_ct_props_map['countLow']] = vulnCounts[key]
                      elif key == 'kev':
                        logging.debug(f"Setting MFST property with key: {key}, to value: {vulnCounts[key]}")
                        properties[manifest_to_ct_props_map['countKev']] = vulnCounts[key]
                else:
                  logging.debug(f"Setting MFST property with key: {key}, to value: {value}")
                  properties[manifest_to_ct_props_map[key]] = value
            logging.debug(f"Finished looping over response values. Resolved asset ID: {resolvedAssetId}")
          else:
            logging.debug(f"Failed to resolve asset list: {request_response}")
            response["error"] = "Failed to resolve asset list."
          
          response["properties"] = properties
        else:
          response["error"] = fetch_assets_list_response.reason
    except Exception as e:
      response["error"] = f"Could not resolve properties: {e}."
  else:
    keys_list = ', '.join(params.keys())
    error_message = f'Manifest: Missing required parameter information. Make sure model_classification & firmware_classification properties are available for this device. Params provided: {keys_list}'
    response["error"] = error_message
else:
  error_message = f'Manifest: Missing API token or user consent to Manifest terms & agreements not provided.'
  logging.debug(error_message)
  response["error"] = error_message
