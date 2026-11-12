"""Read live User Groups using the matched Object GUID."""
response = ad_client.run(params, globals().get("ssl_context"), "user", object_property="connect_activedirectory_user_object", property_suffix="group_details")
