"""
HP VME Connect App - Undo Add or Remove Tag
Put the tag back to how it was before the action.
"""

response = {}
try:
    response = hpvme_lib.restore_tag(params, ssl_verify)
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Undo Add or Remove Tag failed: " + str(response.get("troubleshooting")))
