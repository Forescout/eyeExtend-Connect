"""
HP VME Connect App - Restart VM Action
Restart the VM.
"""

response = {}
try:
    response = hpvme_lib.run_instance_action(params, ssl_verify, "restart", {"server": "true"})
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Restart VM Action failed: " + str(response.get("troubleshooting")))
