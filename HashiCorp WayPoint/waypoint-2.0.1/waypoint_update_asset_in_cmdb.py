"""
Update asset in WayPoint staging table (Refactored Version)
Wrapper for waypoint_cmdb_operations.save_asset_to_staging()

Copyright © 2023 Forescout Technologies, Inc.
"""
import logging

try:
    from waypoint_cmdb_operations import save_asset_to_staging
    
    # Extract the token
    bearer_token = params["connect_authorization_token"]
    
    # Call unified function
    response = save_asset_to_staging(params, bearer_token, ssl_context, operation="update")
    
except Exception as e:
    response = {
        "succeeded": False,
        "troubleshooting": f"Failed to update asset: {str(e)}"
    }
    logging.exception("Failed to update asset")

logging.debug(f"Update asset result: {response}")
