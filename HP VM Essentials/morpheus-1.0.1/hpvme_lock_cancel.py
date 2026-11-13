"""
HP VME Connect App - Undo Lock VM
Legacy undo entry point. Automatic unlock is refused; an operator must unlock.
"""

response = {}
try:
    response = hpvme_lib.unlock_instance(params, ssl_verify)
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Undo Lock VM failed: " + str(response.get("troubleshooting")))
