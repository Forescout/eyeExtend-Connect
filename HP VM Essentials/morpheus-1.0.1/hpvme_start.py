"""
HP VME Connect App - Start VM Action
Start a stopped or suspended VM (also resumes a suspended VM).
"""

response = {}
try:
    response = hpvme_lib.run_instance_action(params, ssl_verify, "start", {"server": "true"}, disruptive=False)
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Start VM Action failed: " + str(response.get("troubleshooting")))
