"""
HP VME Connect App - Suspend VM Action
Suspend the VM, keeping its memory state, without shutting down the guest OS.
"""

response = {}
try:
    response = hpvme_lib.run_instance_action(params, ssl_verify, "suspend")
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Suspend VM Action failed: " + str(response.get("troubleshooting")))
