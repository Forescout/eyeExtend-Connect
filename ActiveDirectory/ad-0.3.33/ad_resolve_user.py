"""Resolve only User Object from parsed collector evidence and native names."""
response = ad_client.run(params, globals().get("ssl_context"), "user", guid_property="connect_activedirectory_managed_user_guid_script_details", property_suffix="object")
