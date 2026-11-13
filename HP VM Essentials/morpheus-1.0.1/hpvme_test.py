"""
HP VME Connect App - Test Script
Runs when the operator clicks Test. Logs in, then reports the manager's version
and how many hosts and VMs it can see.
"""

response = {}
managers = hpvme_lib.get_managers(params)
proxies = hpvme_lib.get_proxies_from_params(params)

if not managers:
    response["succeeded"] = False
    response["result_msg"] = "No HP VME manager is configured."
else:
    successes = []
    failures = []
    for url, username, password in managers:
        try:
            client = hpvme_lib.Client(url, username, password, ssl_verify, proxies)
            version = (client.request("GET", "/api/whoami").get("appliance") or {}).get("buildVersion", "unknown")
            hosts, vms, _ = hpvme_lib.fetch_inventory(client)
            successes.append(f"{url}: version {version}, {len(hosts)} host(s), {len(vms)} VM(s)")
        except hpvme_lib.HpvmeError as error:
            logging.error(f"HP VME test failed for {url}: {error}")
            failures.append(f"{url}: {error}")
        except Exception as error:
            logging.exception(error)
            failures.append(f"{url}: unexpected error: {error}")

    # The test passes only if every configured manager works
    response["succeeded"] = not failures
    response["result_msg"] = "\n".join(
        ([f"Connected: {line}" for line in successes]) + ([f"Failed: {line}" for line in failures])
    )
