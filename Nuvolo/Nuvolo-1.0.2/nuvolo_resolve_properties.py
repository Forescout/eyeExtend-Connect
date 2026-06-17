"""
Nuvolo Custom Properties Resolver

This script resolves custom Nuvolo properties from base Forescout properties as a workaround
for property dependency resolution issues where some properties are not passed from the managing 
appliance to action scripts.

Workaround Pattern:
- Custom properties are defined with dependencies on base properties
- This resolver script fetches values from base properties via hostinfo calls
- The resolved values are exposed as custom Nuvolo properties
- Action scripts use these custom properties for reliable value retrieval

Custom Properties Resolved:
- connect_nuvolo_host_mac: Resolves from mac
    * Handles string or array formats
  * Strips brackets and quotes for clean MAC address value
  
- connect_nuvolo_host_role: Resolves from otsm_details_role
  * Provides device role (e.g., "OT Workstation", "Server", "Laptop")

Response Format:
{
    "properties": {
        "connect_nuvolo_host_mac": "08:92:04:c0:8b:ee",
        "connect_nuvolo_host_role": "OT Workstation"
    }
}
"""

properties = {}

# Resolve MAC address - support both scalar and array forms
mac_address = params.get("mac", "")
if mac_address:
    # If it's a list, get the first element
    if isinstance(mac_address, list) and len(mac_address) > 0:
        mac_address = mac_address[0]
    # Convert to string and strip any quotes or brackets
    mac_str = str(mac_address).strip('[]"\'').strip()
    # Only include if not empty and not "unknown"
    if mac_str and mac_str.lower() != "unknown":
        properties["connect_nuvolo_host_mac"] = mac_str

# Resolve role
role = params.get("otsm_details_role", "")
if role:
    role_str = str(role).strip()
    # Only include if not "unknown"
    if role_str and role_str.lower() != "unknown":
        properties["connect_nuvolo_host_role"] = role_str

response = {}
if properties:
    response["properties"] = properties
