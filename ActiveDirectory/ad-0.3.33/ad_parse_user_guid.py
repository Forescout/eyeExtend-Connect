"""Parse endpoint GUID evidence without a directory connection."""
response = ad_client.run_collector(params, "user", guid_property="script_result.b249e1c035a662f102d2aba7094d9777")
