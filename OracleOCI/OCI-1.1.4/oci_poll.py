"""
OCI Connect App - Discovery/Poll Script
Discovers all OCI compute instances across all compartments and subscribed regions.
Returns endpoints with MAC and IP addresses mapped to Forescout core properties.
"""

import requests

# params, response, logging, ssl_verify are pre-injected by the Connect framework

region_param = params.get("connect_oci_region", "")
tenancy_ocid = params.get("connect_oci_tenancy_ocid", "")
user_ocid = params.get("connect_oci_user_ocid", "")
fingerprint = params.get("connect_oci_fingerprint", "")
private_key_pem = params.get("connect_oci_private_key", "")

proxies = oci_lib.get_proxies_from_params(params)

response = {}
endpoints = []

try:
    # -----------------------------------------------------------------------
    # Step 1: Determine target regions
    # -----------------------------------------------------------------------
    target_regions = oci_lib.get_target_regions(
        region_param, tenancy_ocid, user_ocid, fingerprint, private_key_pem,
        verify=ssl_verify, proxies=proxies
    )
    logging.info("OCI Poll: Target regions: {}".format(target_regions))

    # -----------------------------------------------------------------------
    # Step 2: Fetch all compartments recursively (tenancy-wide, use first region)
    # -----------------------------------------------------------------------
    logging.info("OCI Poll: Fetching compartments for tenancy...")
    compartments = oci_lib.list_compartments(
        region=target_regions[0],
        tenancy_ocid=tenancy_ocid,
        user_ocid=user_ocid,
        fingerprint=fingerprint,
        private_key_pem=private_key_pem,
        verify=ssl_verify,
        proxies=proxies
    )

    # Build compartment OCID -> name map
    compartment_map = {tenancy_ocid: "tenancy-root"}
    for comp in compartments:
        compartment_map[comp.get("id", "")] = comp.get("name", "Unknown")

    # Build list of compartment IDs to query (include tenancy root)
    compartment_ids = [tenancy_ocid]
    for comp in compartments:
        comp_id = comp.get("id", "")
        if comp_id:
            compartment_ids.append(comp_id)

    logging.info("OCI Poll: Found {} compartments (including root).".format(
        len(compartment_ids)))

    # -----------------------------------------------------------------------
    # Step 3: List instances across all regions and compartments
    # -----------------------------------------------------------------------
    all_instances = []
    for region in target_regions:
        for comp_id in compartment_ids:
            try:
                instances = oci_lib.list_instances(
                    region=region,
                    compartment_id=comp_id,
                    tenancy_ocid=tenancy_ocid,
                    user_ocid=user_ocid,
                    fingerprint=fingerprint,
                    private_key_pem=private_key_pem,
                    verify=ssl_verify,
                    proxies=proxies
                )
                for inst in instances:
                    # Skip TERMINATED instances (no VNICs or volumes)
                    if inst.get("lifecycleState") == "TERMINATED":
                        continue
                    # Tag with region for downstream lookups
                    inst["_region"] = region
                    all_instances.append(inst)
            except requests.exceptions.HTTPError as e:
                # 404 = empty compartment or no access, skip silently
                if e.response is not None and e.response.status_code == 404:
                    continue
                logging.info("OCI Poll: Error in region {} compartment {}: {}".format(
                    region, comp_id, str(e)))
            except Exception as e:
                logging.info("OCI Poll: Error in region {} compartment {}: {}".format(
                    region, comp_id, str(e)))

    logging.info("OCI Poll: Found {} non-terminated instances.".format(len(all_instances)))

    # -----------------------------------------------------------------------
    # Step 4: For each instance, get VNIC (MAC/IP) and volumes
    # -----------------------------------------------------------------------
    network_name_cache = {}
    image_os_cache = {}

    for instance in all_instances:
        instance_id = instance.get("id", "")
        compartment_id = instance.get("compartmentId", "")
        availability_domain = instance.get("availabilityDomain", "")
        display_name = instance.get("displayName", "")
        inst_region = instance.get("_region", target_regions[0])

        # Get network info (MAC, IP, public IP, hostname, subnet)
        network_info = oci_lib.get_instance_network_info(
            region=inst_region,
            compartment_id=compartment_id,
            instance_id=instance_id,
            tenancy_ocid=tenancy_ocid,
            user_ocid=user_ocid,
            fingerprint=fingerprint,
            private_key_pem=private_key_pem,
            verify=ssl_verify,
            proxies=proxies
        )
        mac_hex = network_info.get("mac")
        private_ip = network_info.get("private_ip")

        # Skip instances with no MAC and no IP (cannot create Forescout endpoint)
        if not mac_hex and not private_ip:
            logging.info("OCI Poll: Skipping instance {} ({}) - no MAC or IP.".format(
                display_name, instance_id))
            continue

        # Get volume info
        boot_volume_size, block_volumes = oci_lib.get_instance_volumes(
            region=inst_region,
            availability_domain=availability_domain,
            compartment_id=compartment_id,
            instance_id=instance_id,
            tenancy_ocid=tenancy_ocid,
            user_ocid=user_ocid,
            fingerprint=fingerprint,
            private_key_pem=private_key_pem,
            verify=ssl_verify,
            proxies=proxies
        )

        # Resolve subnet and VCN names (cached)
        subnet_name, vcn_name = oci_lib.resolve_network_names(
            region=inst_region,
            subnet_id=network_info.get("subnet_id", ""),
            tenancy_ocid=tenancy_ocid,
            user_ocid=user_ocid,
            fingerprint=fingerprint,
            private_key_pem=private_key_pem,
            verify=ssl_verify,
            proxies=proxies,
            cache=network_name_cache
        )
        network_info["subnet_name"] = subnet_name
        network_info["vcn_name"] = vcn_name

        # Resolve image OS name (cached)
        image_os = oci_lib.resolve_image_os(
            region=inst_region,
            instance=instance,
            tenancy_ocid=tenancy_ocid,
            user_ocid=user_ocid,
            fingerprint=fingerprint,
            private_key_pem=private_key_pem,
            verify=ssl_verify,
            proxies=proxies,
            cache=image_os_cache
        )

        # Build properties
        props = oci_lib.build_instance_properties(
            instance, compartment_map, boot_volume_size, block_volumes,
            network_info=network_info, image_os=image_os
        )

        # Set online status
        is_running = instance.get("lifecycleState") == "RUNNING"
        props["online"] = is_running

        # Build endpoint
        endpoint = {"properties": props}
        if mac_hex:
            endpoint["mac"] = mac_hex
        if private_ip:
            endpoint["ip"] = private_ip

        endpoints.append(endpoint)

    logging.info("OCI Poll: Returning {} endpoints.".format(len(endpoints)))

except Exception as e:
    logging.exception(e)
    logging.info("OCI Poll: Fatal error during discovery: {}".format(str(e)))

response["endpoints"] = endpoints
