"""
HP VME Connect App - Undo Stop VM (Graceful)
Restore the power state recorded before Stop VM.
"""

response = {}
try:
    response = hpvme_lib.restore_power_state(params, ssl_verify, "stop")
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Undo Stop VM (Graceful) failed: " + str(response.get("troubleshooting")))
