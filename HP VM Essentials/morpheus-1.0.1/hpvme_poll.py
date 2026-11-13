"""
HP VME Connect App - Poll/Discovery Script
Discovers hypervisor hosts and VMs from each configured manager.

VMs are returned once per NIC, identified by MAC and IP. Each host is returned
once, identified by the NIC holding its management IP. Forescout's online status
follows the power state, so stopped and suspended VMs show as offline.

Every endpoint records its server ID and owning manager. Resolve and action
scripts use those, because server IDs are only unique within one manager.
"""

response = {}
endpoints = []
errors = []  # reported only if discovery found nothing at all
proxies = hpvme_lib.get_proxies_from_params(params)


for url, username, password in hpvme_lib.get_managers(params):
    try:
        client = hpvme_lib.Client(url, username, password, ssl_verify, proxies)
        hosts, vms, instance_by_server_id = hpvme_lib.fetch_inventory(client)
        logging.info(f"HP VME poll: {url} returned {len(hosts)} host(s) and {len(vms)} VM(s)")

        # Count VMs per host from the list already in hand
        vm_counts = {}
        for vm in vms:
            parent_id = (vm.get("parentServer") or {}).get("id")
            vm_counts[parent_id] = vm_counts.get(parent_id, 0) + 1

        for vm in vms:
            properties = hpvme_lib.vm_properties(vm, instance_by_server_id.get(str(vm.get("id"))))
            properties["connect_hpvme_controller_ip"] = url
            properties["connect_hpvme_server_id"] = vm.get("id")
            properties["online"] = vm.get("powerState") == "on"
            identities = hpvme_lib.vm_identities(vm)
            if not identities:
                logging.warning(f"HP VME poll: skipping VM {vm.get('name')}: no MAC or IP")
            endpoints.extend(hpvme_lib.make_endpoints(identities, properties))

        for host in hosts:
            properties = hpvme_lib.host_properties(host, vm_counts.get(host.get("id"), 0))
            properties["connect_hpvme_controller_ip"] = url
            properties["connect_hpvme_server_id"] = host.get("id")
            properties["online"] = host.get("powerState") == "on"
            identities = hpvme_lib.host_identities(host)
            if not identities:
                logging.warning(f"HP VME poll: skipping host {host.get('name')}: no MAC or IP")
            endpoints.extend(hpvme_lib.make_endpoints(identities, properties))

    except hpvme_lib.HpvmeError as error:
        logging.error(f"HP VME poll failed for {url}: {error}")
        errors.append(f"{url}: {error}")
    except Exception as error:
        logging.exception(error)
        errors.append(f"{url}: unexpected error: {error}")

logging.info(f"HP VME poll: returning {len(endpoints)} endpoint(s)")
response["endpoints"] = endpoints

# One unreachable manager must not discard endpoints found on the others
if errors and not endpoints:
    response["error"] = "HP VME poll failed: " + "; ".join(errors)
