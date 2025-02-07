'''
Copyright © 2020 Forescout Technologies, Inc.

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
'''

import logging
import base64
import jwt
import hashlib
import time
import json
import ssl
import urllib.request

def check_consent(params):
    if not params.get('connect_manifest_consent_agreements', False):
        logging.info('You must consent to abide by all applicable terms and agreements between your organization and Manifest Cyber. Please reinstall the integration and agree to the terms.')
        return False
    logging.debug('You agreed to abide by all applicable terms and agreements between your organization and Manifest Cyber. Test continuing...')
    return True

def perform_request(url, headers, ssl_context, method='GET'):
    request = urllib.request.Request(url, method=method, headers=headers)
    try:
        response = urllib.request.urlopen(request, context=ssl_context)
        # Check the content type of the response
        content_type = response.headers.get('Content-Type', '')
        content = response.read()

        if 'application/json' in content_type:
            if content:  # Check if the response body is not empty
                return json.loads(content)
            else:
                return {"error": "Empty response", "status": response.status}
        elif 'text/plain' in content_type:
            return content.decode('utf-8')  # Decode bytes to string if plain text
        else:
            logging.warning(f'Unexpected content type: {content_type}')
            return {"error": "Unexpected content type", "status": response.status, "content": content.decode('utf-8')}

    except urllib.error.HTTPError as e:
        content = e.read().decode()
        return {"error": content or "Unknown error", "status": e.code}
    except urllib.error.URLError as e:
        raise Exception(f"URL Error: {e.reason}")


manifest_to_ct_props_map = {
  "assetId": "connect_manifest_assetid",
  "sbomId": "connect_manifest_sbomid",
  "relationship": "connect_manifest_sbom_relationship",
  "coordinates": "connect_manifest_coordinates",
}

response = {}
properties = {}

logging.info("Got the following params:")
for key, value in params.items():
  logging.info(f"{key}: {value}")

manifest_base_url = params.get('connect_manifest_url')
manifest_api_token = params.get('connect_manifest_apitoken')

ssl_context = ssl.create_default_context()
headers = {'Authorization': f'Bearer {manifest_api_token}'}

if not check_consent(params):
  response['succeeded'] = False
  response['result_msg'] = 'Consent not provided.'
  logging.info('Consent to Manifest terms & agreements not provided.')

# We know this likely won't work yet, the "firmware" requirement is a placeholder
# We need the "Cloud Data Exchange Firmware", "Cloud Data Exchange Model", and "Cloud Data Exchange Vendor" from FS Cloud Data Exchange module - but we don't yet know what keys to look for.
required_params = ["mfst_firmware", "mfst_model", "mfst_vendor"]
if all(key in params and params[key] and params[key] != 'Unknown' for key in required_params):
  firmware = params.get('mfst_firmware').lower()
  model = params.get('mfst_model').lower()
  vendor = params.get('mfst_vendor').lower()

  # Assemble our query string
  assets_list_query_string = urllib.parse.quote(
      '?limit=10&filters=[{ "field": "textSearch", "value": "' +  model + '@' + firmware + '" }, { "field": "assetActive", "value": "true" }]',
      safe='?&='
  )

  try:
      asset_list_check = perform_request(manifest_base_url + '/v1/assets' + assets_list_query_string, headers, ssl_context)
      logging.debug('Asset list returned successfully (still need to check result accuracy).')
  except Exception as e:
      # Ran into an error (likely expired token, etc) while attempting to fetch assets.
      # Note to user.
      response['succeeded'] = False
      response_message = f'Manifest: Unexpected error while attempting to fetch assets! Error: {e}'
      response['result_msg'] = response_message
      logging.debug(response_message)
  else:
      if asset_list_check['success'] and asset_list_check['queryInfo']['totalReturn'] == 1:
          package_url_no_version = 'pkg:cpe/' + vendor + '/' + model
          # if asset_list_check['data'][0]['packageUrlNoVersion'] != package_url_no_version:
          #   # We got a single result, but the packageUrlNoVersion doesn't match what we expected
          #   # For now, we consider this an error. Note to user.
          #   response['succeeded'] = False
          #   response_message = f'Manifest: Properties retrieved for entity {vendor}/{model}@{firmware}, but got a potentially mismatched response with: {asset_list_check["data"][0]}'
          #   response['result_msg'] = response_message
          #   logging.debug(response_message)
          # else:
          logging.debug('Received single asset from Manifest, continuing to assign data to CT properties')
          return_values = asset_list_check["data"][0]

          for key, value in return_values.items():
            if key in manifest_to_ct_props_map:
              properties[manifest_to_ct_props_map[key]] = value

          # Add properties and mark as succeeded
          response["properties"] = properties
          response['succeeded'] = True

          keys_list = ', '.join(response["properties"].keys())
          logging.debug(f'Setting properties for entity {vendor}/{model}@{firmware} with: {keys_list}')
          # logging.debug(f'Manifest: Properties retrieved for entity {vendor}/{model}@{firmware}, got JSON response with: {asset_list_check["data"][0]["packageUrlNoVersion"]}')
      else:
        # We got either zero or multiple results, which isn't expected.
        # For now, we consider this an error. Note to user.
        response['succeeded'] = False
        response_message = f'Manifest: Expected 1 asset to be returned, but got {asset_list_check["queryInfo"]["totalReturn"]}.'
        response['result_msg'] = response_message
        logging.debug(response_message)

else:
  response['succeeded'] = False
  # Short-term: Make sure the keys we need are provided from the Cloud Data Exchange module.
  keys_list = ', '.join(params.keys())
  response_message = f'Manifest: Missing required parameter information. Make sure mfst_firmware, mfst_vendor, & mfst_model are provided from the Cloud Data Exchange module. Params provided: {keys_list}'
  response['result_msg'] = response_message
  logging.debug(response_message)
