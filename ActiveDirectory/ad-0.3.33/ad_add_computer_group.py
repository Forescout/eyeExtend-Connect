"""Change a direct membership using an exact group DN."""
response = ad_client.run(params, globals().get("ssl_context"), "computer", "add", guid_property="script_result.b249e1c035a662f102d2aba7094d9777")
