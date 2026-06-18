"""
Create IT Incident in WayPoint (Refactored Version)
Improved error handling and validation

Copyright © 2023 Forescout Technologies, Inc.
"""
import json
import logging
import urllib.request
import urllib.error

try:
    from config.field_mappings import INCIDENT_FIELDS
    from utils.validators import validate_params, validate_bearer_token, validate_bus_obj_id
    from utils.http_client import WayPointHTTPClient, create_headers
except ImportError:
    INCIDENT_FIELDS = [
        "Service", "Category", "Subcategory", "Description",
        "Priority", "CustomerRecID", "Source", "ShortDescription",
        "ConfigItemDisplayName", "ConfigItemRecID"
    ]
    validate_params = None


def create_incident(params: dict, bearer_token: str, ssl_context) -> dict:
    """
    Create IT incident in WayPoint.
    
    Args:
        params: ForeScout parameters dictionary
        bearer_token: OAuth2 bearer token
        ssl_context: SSL context for HTTPS
        
    Returns:
        Response dictionary with succeeded flag and Incident_ID
    """
    response = {}
    
    try:
        # Validate inputs
        if validate_params:
            validate_params(params, ["connect_WayPoint_base_url"])
            validate_bearer_token(bearer_token)
        
        # Extract configuration
        url_call = params["connect_WayPoint_base_url"].rstrip('/')
        url_content_type = params.get("connect_WayPoint_content_type", "application/json")
        url_accept_type = params.get("connect_WayPoint_accept_type", "application/json")
        
        # Setup headers
        header_info = {
            'Content-Type': url_content_type,
            'Accept': url_accept_type,
            'Authorization': f'{bearer_token}'
        }
        
        # Step 1: Get Incident table metadata
        logging.debug("Getting Incident table metadata")
        incident_metadata = _get_incident_metadata(
            url_call, header_info, ssl_context
        )
        
        incident_busObjID = incident_metadata['busObId']
        incident_Name = incident_metadata['name']
        
        if validate_bus_obj_id:
            validate_bus_obj_id(incident_busObjID)
        
        logging.debug(f"Incident table busObId: {incident_busObjID}")
        
        # Step 2: Get Incident schema
        logging.debug("Getting Incident schema")
        field_definitions = _get_incident_schema(
            url_call, incident_busObjID, header_info, ssl_context
        )
        
        # Step 3: Build field mapping
        field_name_to_id_map = {}
        for field_def in field_definitions:
            field_name = field_def['name']
            field_id = field_def['fieldId']
            if field_name in INCIDENT_FIELDS:
                field_name_to_id_map[field_name] = field_id
        
        logging.debug(f"Mapped {len(field_name_to_id_map)} incident fields")
        
        # Step 4: Build payload
        incident_payload = _build_incident_payload(
            incident_busObjID, field_name_to_id_map, params
        )
        
        # Step 5: Create incident
        logging.debug("Creating incident")
        incident_id = _save_incident(
            url_call, incident_payload, header_info, ssl_context
        )
        
        # Success response
        response["succeeded"] = True
        response["Incident_ID"] = incident_id
        logging.debug(f"Incident created: {incident_id}")
        
    except ValueError as e:
        response["succeeded"] = False
        response["troubleshooting"] = f"Validation error: {str(e)}"
        logging.error(f"Validation error: {str(e)}")
        
    except urllib.error.HTTPError as e:
        response["succeeded"] = False
        response["troubleshooting"] = f"HTTP error {e.code}: {e.reason}"
        logging.error(f"HTTP error: {e.code} - {e.reason}")
        
    except urllib.error.URLError as e:
        response["succeeded"] = False
        response["troubleshooting"] = f"Network error: {str(e)}"
        logging.error(f"Network error: {str(e)}")
        
    except KeyError as e:
        response["succeeded"] = False
        response["troubleshooting"] = f"Missing parameter: {str(e)}"
        logging.error(f"Missing parameter: {str(e)}")
        
    except Exception as e:
        response["succeeded"] = False
        response["troubleshooting"] = f"Unexpected error: {str(e)}"
        logging.exception("Unexpected error during incident creation")
    
    return response


def _get_incident_metadata(url_call: str, headers: dict, ssl_context) -> dict:
    """Get Incident table metadata."""
    tablename = "Incident"
    target_url = f"{url_call}/api/V1/getbusinessobjectsummary/busobname/{tablename}"
    
    req = urllib.request.Request(
        target_url, headers=headers, data=bytes('', 'utf-8'), method='GET'
    )
    resp = urllib.request.urlopen(req, context=ssl_context)
    response_data = json.loads(resp.read())
    
    return response_data[0]


def _get_incident_schema(url_call: str, bus_obj_id: str, headers: dict,
                        ssl_context) -> list:
    """Get Incident table schema."""
    target_url = f"{url_call}/api/V1/getbusinessobjectschema/busobid/{bus_obj_id}"
    
    req = urllib.request.Request(
        target_url, headers=headers, data=bytes('', 'utf-8'), method='GET'
    )
    resp = urllib.request.urlopen(req, context=ssl_context)
    response_data = json.loads(resp.read())
    
    return response_data['fieldDefinitions']


def _build_incident_payload(bus_obj_id: str, field_map: dict, params: dict) -> dict:
    """Build incident payload."""
    incident_fields = []
    
    for field_name, field_id in field_map.items():
        try:
            param_name = f"WayPoint_{field_name}"
            
            if param_name not in params:
                logging.debug(f"Parameter not found: {param_name}")
                continue
            
            field_value = params[param_name]
            
            incident_field = {
                "fieldId": field_id,
                "name": field_name,
                "value": field_value,
                "dirty": True
            }
            incident_fields.append(incident_field)
            
        except KeyError:
            logging.debug(f"Parameter not found: {param_name}")
            continue
        except Exception as e:
            logging.warning(f"Error processing field {field_name}: {str(e)}")
            continue
    
    payload = {
        "busObId": bus_obj_id,
        "fields": incident_fields,
        "persist": True
    }
    
    return payload


def _save_incident(url_call: str, payload: dict, headers: dict, ssl_context) -> str:
    """Save incident to WayPoint."""
    target_url = f"{url_call}/api/V1/savebusinessobject"
    payload_data = json.dumps(payload)
    
    logging.debug(f"Incident payload size: {len(payload['fields'])} fields")
    
    req = urllib.request.Request(
        target_url, headers=headers,
        data=bytes(payload_data, 'utf-8'), method='POST'
    )
    resp = urllib.request.urlopen(req, context=ssl_context)
    response_data = json.loads(resp.read())
    status_code = resp.getcode()
    
    if status_code != 200:
        raise RuntimeError(f"Incident creation failed with status: {status_code}")
    
    return response_data['busObPublicId']


# Main execution block for ForeScout
try:
    bearer_token = params["connect_authorization_token"]
    response = create_incident(params, bearer_token, ssl_context)
    
except Exception as e:
    response = {
        "succeeded": False,
        "troubleshooting": f"Failed to create incident: {str(e)}"
    }
    logging.exception("Incident creation failed")

logging.debug(f"Incident creation result: {response}")
