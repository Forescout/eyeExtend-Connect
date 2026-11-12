"""Resolve only Computer Object from parsed collector evidence and native names."""
response = ad_client.run(params, globals().get("ssl_context"), "computer", guid_property="connect_activedirectory_managed_computer_guid_script_details", property_suffix="object")
