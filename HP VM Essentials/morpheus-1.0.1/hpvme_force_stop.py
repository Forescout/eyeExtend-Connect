"""
HP VME Connect App - Force Power Off VM Action
Immediately power off the VM without a guest shutdown. Unsaved data in the VM can be lost.
"""

response = {}
try:
    response = hpvme_lib.run_instance_action(params, ssl_verify, "stop", {"server": "true", "force": "true"})
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Force Power Off VM Action failed: " + str(response.get("troubleshooting")))
