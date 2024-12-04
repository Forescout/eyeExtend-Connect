import logging
import json
import urllib.request
import ssl

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
