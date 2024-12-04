from connectproxyserver import ConnectProxyServer, ProxyProtocol

# Given the params dict, determine if the user has consented to the terms and agreements during setup
def check_consent(params):
  if not params.get('connect_manifest_consent_agreements', False):
    logging.info('You must consent to abide by all applicable terms and agreements between your organization and Manifest Cyber. Please reinstall the integration and agree to the terms.')
    return False
  logging.debug('You agreed to abide by all applicable terms and agreements between your organization and Manifest Cyber. Test continuing...')
  return True

# Mapping between SampleApp API response fields to CounterACT properties
manifest_to_ct_props_map = {
  "_id": "connect_manifest_assetid",
  "sbomId": "connect_manifest_sbomid",
  "whenUploaded": "connect_manifest_sbomuploaddate",
  "relationshipToOrg": "connect_manifest_sbom_relationship",
  "coordinates": "connect_manifest_coordinates",
  "riskScore": "connect_manifest_riskscore",
  "countTotal": "connect_manifest_countVulnsTotal",
  "countCritical": "connect_manifest_countVulnsCritical",
  "countHigh": "connect_manifest_countVulnsHigh",
  "countMedium": "connect_manifest_countVulnsMedium",
  "countLow": "connect_manifest_countVulnsLow",
  "countKev": "connect_manifest_countVulnsKev",
  "sbomUrl": "connect_manifest_sbomDownloadUrl",
}

manifest_to_ct_vuln_entry_props_map = {
  "cveId": "connect_manifest_vulnerability_id",
  "cvss2BaseScore": "connect_manifest_vulnerability_cvss2_base_score",
  "cvss2BaseSeverity": "connect_manifest_vulnerability_cvss2_base_severity",
  "cvss3BaseScore": "connect_manifest_vulnerability_cvss3_base_score",
  "cvss3BaseSeverity": "connect_manifest_vulnerability_cvss3_base_severity",
  "epssPercentile": "connect_manifest_vulnerability_id_epss_percentile",
  "epssScore": "connect_manifest_vulnerability_id_epss_score",
  "publishDate": "connect_manifest_vulnerability_id_publishate",
  "recommendedAction": "connect_manifest_vulnerability_id_recommend",
  "priorityScore": "connect_manifest_vulnerability_id_priority",
  "impactedAssets": "connect_manifest_vulnerability_id_impacted_assets",
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
  required_params = ["mfst_firmware", "mfst_model"]
  if all(key in params and params[key] and params[key] != 'Unknown' for key in required_params):
    givenVendor = params.get("mfst_vendor")
    givenModel = params.get("mfst_model")
    givenFirmware = params.get("mfst_firmware")
    
    # Assemble a partial pURL string we'll use for comparisons later
    assetPartialPurl = givenModel + '@' + givenFirmware
  
    # If vendor is present, prepend it to the assetPartialPurl
    if givenVendor and givenVendor != 'Unknown':
      assetPartialPurl = givenVendor + '/' + assetPartialPurl
    
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
          if request_response and request_response['success'] and request_response['queryInfo']['totalReturn'] == 1:
            return_values = request_response['data'][0]
            logging.debug(f"Resolve response text on 0 element: {request_response['data'][0]}")
            for key, value in return_values.items():
              if key in manifest_to_ct_props_map:
                properties[manifest_to_ct_props_map[key]] = value

            # Fetch the single asset - which should include `latestSbom`, from which we'll get the sbomId and whenUploaded fields, and then construct a download URL
            fetch_single_asset_response = session.get(manifest_base_url + "/v1/asset/" + properties["connect_manifest_assetid"], proxies=proxy_server.proxies)

            # Check if the fetch_single_asset_response is successful
            if fetch_single_asset_response and fetch_single_asset_response['success']:
              return_values = fetch_single_asset_response['data'][0]
              logging.debug(f"Resolve response latest sbom: {return_values['latestSbom']}")
              for key, value in return_values['latestSbom'].items():
                # We'll get the sbomId and whenUploaded from the latestSbom object
                if key in manifest_to_ct_props_map:
                  if key == '_id': # Don't overwrite the assetId, point to sbomId
                    properties[manifest_to_ct_props_map['sbomId']] = value
                  elif key == 'dateCreated': # Date asset was first created
                    properties[manifest_to_ct_props_map['whenUploaded']] = value
                  elif key == 'sbomId': # Generate SBOM URL
                    properties[manifest_to_ct_props_map['sbomUrl']] = manifest_base_url + '/v1/sbom/download/' + value + '?redirect=1'
                  elif key == 'countVulnerabilities': # Iterate over vuln counts
                    properties[manifest_to_ct_props_map['countTotal']] = value.get('total', 0)
                    properties[manifest_to_ct_props_map['countCritical']] = value.get('critical', 0)
                    properties[manifest_to_ct_props_map['countHigh']] = value.get('high', 0)
                    properties[manifest_to_ct_props_map['countMedium']] = value.get('medium', 0)
                    properties[manifest_to_ct_props_map['countLow']] = value.get('low', 0)
                    properties[manifest_to_ct_props_map['countKev']] = value.get('isKev', 0)
                  else:
                    properties[manifest_to_ct_props_map[key]] = value
            else:
              logging.debug(f"Unable to resolve response vulns: {fetch_single_asset_response}")
          response["properties"] = properties
        else:
          response["error"] = fetch_assets_list_response.reason
    except Exception as e:
      response["error"] = f"Could not resolve properties: {e}."
  else:
    keys_list = ', '.join(params.keys())
    error_message = f'Manifest: Missing required parameter information. Make sure mfst_firmware & mfst_model are provided from the Cloud Data Exchange module (mfst_vendor also recommended). Params provided: {keys_list}'
    logging.debug(error_message)
    for key, value in params.items():
      logging.debug(f'Key: {key}, Value: {value}')
    response["error"] = error_message
else:
  error_message = f'Manifest: Missing API token or user consent to Manifest terms & agreements not provided.'
  logging.debug(error_message)
  response["error"] = error_message
