"""
HP VME Connect App - Lock VM Action
Lock the VM against deletion. An operator must unlock it in HP VME.
"""

response = {}
try:
    response = hpvme_lib.lock_instance(params, ssl_verify)
except Exception as error:
    logging.exception(error)
    response = {"succeeded": False, "troubleshooting": f"Unexpected error: {error}"}
if not response.get("succeeded"):
    logging.error("HP VME Lock VM Action failed: " + str(response.get("troubleshooting")))
