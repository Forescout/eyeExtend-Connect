"""
HP VME Connect App - Undo Start VM
Restore the power state recorded before Start VM.
"""

response = {}
try:
    response = hpvme_lib.restore_power_state(params, ssl_verify, "start")
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Undo Start VM failed: " + str(response.get("troubleshooting")))
