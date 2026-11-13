"""
HP VME Connect App - Undo Suspend VM
Restore the power state recorded before Suspend VM.
"""

response = {}
try:
    response = hpvme_lib.restore_power_state(params, ssl_verify, "suspend")
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Undo Suspend VM failed: " + str(response.get("troubleshooting")))
