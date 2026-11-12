"""Undo only the membership change recorded by this successful action."""
response = ad_client.run(params, globals().get("ssl_context"), "computer", "add", cancel=True)
