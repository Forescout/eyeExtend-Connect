"""
HP VME Connect App - Forensic Snapshot Action
Request a point-in-time snapshot of the VM.
"""

response = {}
try:
    response = hpvme_lib.create_snapshot(params, ssl_verify)
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Forensic Snapshot Action failed: " + str(response.get("troubleshooting")))
