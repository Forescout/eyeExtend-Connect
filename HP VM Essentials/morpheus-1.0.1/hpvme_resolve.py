"""
HP VME Connect App - Resolve Script
Refreshes properties for one endpoint that discovery has already identified.

It looks the endpoint up by its stored server ID. Endpoints that discovery never
found have no server ID, so they cost no API calls, however many endpoints
Forescout sees on the network.
"""

response = {}
server_id = params.get("connect_hpvme_server_id")

if server_id in (None, ""):
    response["error"] = "Endpoint has not been discovered by HP VME."
else:
    try:
        client, _ = hpvme_lib.connect_for_action(params, ssl_verify)
        server = client.get_server(server_id)
        kind = hpvme_lib.server_format(server)

        if kind == hpvme_lib.FORMAT_HOST:
            count = client.request("GET", "/api/servers", query={"parentServerId": server_id, "max": 1})
            vm_count = (count.get("meta") or {}).get("total", 0)
            response["properties"] = hpvme_lib.host_properties(server, vm_count)
        elif kind == hpvme_lib.FORMAT_VM:
            instance = hpvme_lib.get_instance_for_server(client, server)
            response["properties"] = hpvme_lib.vm_properties(server, instance)
        else:
            response["error"] = f"Unsupported HP VME server type '{kind}'."

    except hpvme_lib.HpvmeError as error:
        logging.error(f"HP VME resolve failed for server {server_id}: {error}")
        response["error"] = str(error)
    except Exception as error:
        logging.exception(error)
        response["error"] = f"Unexpected error during HP VME resolve: {error}"
