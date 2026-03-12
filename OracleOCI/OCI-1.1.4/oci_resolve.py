"""
OCI Connect App - Resolve Script
Resolves OCI compute instance properties for a specific Forescout host.
Matches the host by MAC address or IP address against OCI instances across
all subscribed regions.
"""

import requests

# params, response, logging, ssl_verify are pre-injected by the Connect framework

region_param = params.get("connect_oci_region", "")
tenancy_ocid = params.get("connect_oci_tenancy_ocid", "")
user_ocid = params.get("connect_oci_user_ocid", "")
fingerprint = params.get("connect_oci_fingerprint", "")
private_key_pem = params.get("connect_oci_private_key", "")

# Host identifiers from Forescout
host_mac = params.get("mac", "")
host_ip = params.get("ip", "")

proxies = oci_lib.get_proxies_from_params(params)

response = {}
properties = {}

try:
    # Normalize host MAC for comparison (12-char uppercase hex, no separators)
    host_mac_normalized = ""
    if host_mac:
        host_mac_normalized = host_mac.replace(":", "").replace("-", "").upper()

    # -----------------------------------------------------------------------
    # Step 1: Determine target regions
    # -----------------------------------------------------------------------
    target_regions = oci_lib.get_target_regions(
        region_param, tenancy_ocid, user_ocid, fingerprint, private_key_pem,
        verify=ssl_verify, proxies=proxies
    )

    # -----------------------------------------------------------------------
    # Step 2: Fetch all compartments (tenancy-wide, use first region)
    # -----------------------------------------------------------------------
    compartments = oci_lib.list_compartments(
        region=target_regions[0],
        tenancy_ocid=tenancy_ocid,
        user_ocid=user_ocid,
        fingerprint=fingerprint,
        private_key_pem=private_key_pem,
        verify=ssl_verify,
        proxies=proxies
    )

    compartment_map = {tenancy_ocid: "tenancy-root"}
    for comp in compartments:
        compartment_map[comp.get("id", "")] = comp.get("name", "Unknown")

    compartment_ids = [tenancy_ocid]
    for comp in compartments:
        comp_id = comp.get("id", "")
        if comp_id:
            compartment_ids.append(comp_id)

    # -----------------------------------------------------------------------
    # Step 3: Search for matching instance across regions and compartments
    # -----------------------------------------------------------------------
    matched_instance = None
    matched_network_info = None
    matched_region = None

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
            except Exception:
                continue

            for inst in instances:
                if inst.get("lifecycleState") == "TERMINATED":
                    continue

                instance_id = inst.get("id", "")
                inst_compartment = inst.get("compartmentId", "")

                # Get VNIC info for this instance
                network_info = oci_lib.get_instance_network_info(
                    region=region,
                    compartment_id=inst_compartment,
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

                # Match by MAC (preferred)
                if host_mac_normalized and mac_hex:
                    if mac_hex.upper() == host_mac_normalized:
                        matched_instance = inst
                        matched_network_info = network_info
                        matched_region = region
                        break

                # Match by IP
                if host_ip and private_ip:
                    if private_ip == host_ip:
                        matched_instance = inst
                        matched_network_info = network_info
                        matched_region = region
                        break

            if matched_instance:
                break
        if matched_instance:
            break

    # -----------------------------------------------------------------------
    # Step 4: Build properties for matched instance
    # -----------------------------------------------------------------------
    if matched_instance:
        availability_domain = matched_instance.get("availabilityDomain", "")
        compartment_id = matched_instance.get("compartmentId", "")
        instance_id = matched_instance.get("id", "")

        # Get volume info
        boot_volume_size, block_volumes = oci_lib.get_instance_volumes(
            region=matched_region,
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

        # Resolve subnet and VCN names
        subnet_name, vcn_name = oci_lib.resolve_network_names(
            region=matched_region,
            subnet_id=matched_network_info.get("subnet_id", ""),
            tenancy_ocid=tenancy_ocid,
            user_ocid=user_ocid,
            fingerprint=fingerprint,
            private_key_pem=private_key_pem,
            verify=ssl_verify,
            proxies=proxies
        )
        matched_network_info["subnet_name"] = subnet_name
        matched_network_info["vcn_name"] = vcn_name

        # Resolve image OS name
        image_os = oci_lib.resolve_image_os(
            region=matched_region,
            instance=matched_instance,
            tenancy_ocid=tenancy_ocid,
            user_ocid=user_ocid,
            fingerprint=fingerprint,
            private_key_pem=private_key_pem,
            verify=ssl_verify,
            proxies=proxies
        )

        properties = oci_lib.build_instance_properties(
            matched_instance, compartment_map, boot_volume_size, block_volumes,
            network_info=matched_network_info, image_os=image_os
        )

        logging.info("OCI Resolve: Matched instance {} ({}) in region {}.".format(
            matched_instance.get("displayName", ""), instance_id, matched_region))
    else:
        logging.info("OCI Resolve: No matching instance found for MAC={} IP={}.".format(
            host_mac, host_ip))
        response["error"] = "No OCI instance found matching MAC={} IP={}".format(
            host_mac, host_ip)

except Exception as e:
    logging.exception(e)
    response["error"] = "Error resolving OCI instance: {}".format(str(e))

response["properties"] = properties
