"""
HP VME Connect App - Add or Remove Tag Action
Add or remove one tag on the VM.
"""

response = {}
try:
    response = hpvme_lib.change_tag(params, ssl_verify)
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Add or Remove Tag Action failed: " + str(response.get("troubleshooting")))
