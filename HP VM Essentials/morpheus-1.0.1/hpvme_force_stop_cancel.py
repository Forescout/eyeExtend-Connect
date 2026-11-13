"""
HP VME Connect App - Undo Force Power Off VM
Restore the power state recorded before Force Power Off VM.
"""

response = {}
try:
    response = hpvme_lib.restore_power_state(params, ssl_verify, "stop")
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Undo Force Power Off VM failed: " + str(response.get("troubleshooting")))
