"""Read live Computer Groups using the matched Object GUID."""
response = ad_client.run(params, globals().get("ssl_context"), "computer", object_property="connect_activedirectory_computer_object", property_suffix="group_details")
