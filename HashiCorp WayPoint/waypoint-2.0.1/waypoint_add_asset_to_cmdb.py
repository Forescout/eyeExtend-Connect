"""
Add asset to WayPoint CMDB staging table (Refactored Version)
Wrapper for Waypoint_cmdb_operations.save_asset_to_staging()

Copyright © 2023 Forescout Technologies, Inc.
"""
import logging

try:
    from waypoint_add_asset_to_cmdb_old_cmdb_operations import save_asset_to_staging
    
    # Extract the token
    bearer_token = params["connect_authorization_token"]
    
    # Call unified function
    response = save_asset_to_staging(params, bearer_token, ssl_context, operation="add")
    
except Exception as e:
    response = {
        "succeeded": False,
        "troubleshooting": f"Failed to add asset: {str(e)}"
    }
    logging.exception("Failed to add asset")

logging.debug(f"Add asset result: {response}")
