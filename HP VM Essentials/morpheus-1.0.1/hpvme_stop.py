"""
HP VME Connect App - Stop VM (Graceful) Action
Gracefully shut down the VM. If the guest does not stop within five minutes, the VM stays running.
"""

response = {}
try:
    response = hpvme_lib.run_instance_action(params, ssl_verify, "stop", {"server": "true"})
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Stop VM (Graceful) Action failed: " + str(response.get("troubleshooting")))
