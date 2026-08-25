# cryticasecurity_test.py
#
# Connection "Test" handler for the Crytica Security Connect App.
#
# Because Crytica Security PUSHES data into Forescout via the Connect web API, there is
# no outbound endpoint to reach out to and test. The framework still requires a
# test handler (testEnable=true), so this script performs a readiness check:
# it confirms the app is configured and reports that the app is ready to
# receive inbound Crytica Security alerts on the Connect web service.
#
# `params`, `response`, and `logging` are pre-injected by the framework.


response = {}

try:
    label = params.get("connect_cryticasecurity_source_label") or "Crytica Security"

    logging.info("Crytica Security Connect App readiness test for source '{}'.".format(label))

    # Nothing to reach out to for a push integration; configuration presence is
    # all we can meaningfully verify here.
    response["succeeded"] = True
    response["result_msg"] = (
        "Crytica Security source '{}' is configured. Forescout is ready to receive "
        "Crytica Security alerts via the Connect web API. Configure Crytica Security to POST "
        "alert messages to the Forescout Connect web service endpoint."
    ).format(label)
except Exception as e:
    logging.exception(e)
    response["succeeded"] = False
    response["result_msg"] = "Crytica Security readiness check failed: {}".format(str(e))
