"""Test bind, TLS validation, and the configured AD naming context."""
response = ad_client.run(params, globals().get("ssl_context"))
