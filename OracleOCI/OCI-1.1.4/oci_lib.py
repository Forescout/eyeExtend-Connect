"""
OCI Connect App - Shared Library
Provides helper functions for Oracle Cloud Infrastructure API communication.
Implements OCI HTTP Signature authentication using the cryptography library.
Library files cannot access params directly - all values must be passed as arguments.
"""

import logging
import requests
import hashlib
import base64
import re
import math
from datetime import datetime, timezone
from urllib.parse import urlparse, urlencode
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


# ---------------------------------------------------------------------------
# Proxy helpers
# ---------------------------------------------------------------------------

def build_proxies(proxy_enable, proxy_ip, proxy_port, proxy_user="", proxy_pass=""):
    """Build a proxies dict for the requests library from Connect proxy settings."""
    if proxy_enable != "true":
        return None
    if proxy_user:
        proxy_url = "http://{}:{}@{}:{}".format(proxy_user, proxy_pass, proxy_ip, proxy_port)
    else:
        proxy_url = "http://{}:{}".format(proxy_ip, proxy_port)
    return {"http": proxy_url, "https": proxy_url}


def get_proxies_from_params(params):
    """Extract proxy settings from params and build a proxies dict."""
    return build_proxies(
        params.get("connect_proxy_enable", ""),
        params.get("connect_proxy_ip", ""),
        params.get("connect_proxy_port", ""),
        params.get("connect_proxy_username", ""),
        params.get("connect_proxy_password", "")
    )


# ---------------------------------------------------------------------------
# OCI API Signing
# ---------------------------------------------------------------------------

def _load_private_key(private_key_pem):
    """Load an RSA private key from a PEM string.

    Handles PEM content that may have literal backslash-n instead of real newlines
    (common when pasting into UI fields).
    """
    pem_str = private_key_pem.strip()
    if "\\n" in pem_str:
        pem_str = pem_str.replace("\\n", "\n")
    pem_bytes = pem_str.encode("utf-8")
    return serialization.load_pem_private_key(pem_bytes, password=None)


def _sign_request(method, url, headers, tenancy_ocid, user_ocid, fingerprint,
                  private_key_pem, body=None):
    """Sign an OCI REST API request using HTTP Signature authentication.

    Modifies the headers dict in-place, adding Date, host, Authorization, and
    for POST/PUT/PATCH: content-type, content-length, x-content-sha256.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        url: Full URL including query string
        headers: dict of headers (modified in-place)
        tenancy_ocid: OCI tenancy OCID
        user_ocid: OCI user OCID
        fingerprint: API key fingerprint
        private_key_pem: PEM-encoded private key string
        body: Request body string for POST/PUT (None for GET/DELETE)

    Returns:
        Modified headers dict with Authorization header added
    """
    parsed = urlparse(url)
    host = parsed.hostname
    path = parsed.path
    if parsed.query:
        path = path + "?" + parsed.query
    request_target = "{} {}".format(method.lower(), path)

    # Set date header (RFC 7231 format)
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
    headers["date"] = date_str
    headers["host"] = host

    # Determine which headers to sign
    if method.upper() in ("POST", "PUT", "PATCH"):
        body_str = body or ""
        body_bytes = body_str.encode("utf-8") if isinstance(body_str, str) else body_str
        body_hash = hashlib.sha256(body_bytes).digest()
        body_hash_b64 = base64.b64encode(body_hash).decode("utf-8")

        headers["content-type"] = "application/json"
        headers["content-length"] = str(len(body_bytes))
        headers["x-content-sha256"] = body_hash_b64

        signing_headers = [
            "date", "(request-target)", "host",
            "content-type", "content-length", "x-content-sha256"
        ]
    else:
        signing_headers = ["date", "(request-target)", "host"]

    # Build the signing string
    signing_parts = []
    for h in signing_headers:
        if h == "(request-target)":
            signing_parts.append("(request-target): {}".format(request_target))
        else:
            signing_parts.append("{}: {}".format(h, headers[h]))
    signing_string = "\n".join(signing_parts)

    # Sign with RSA-SHA256
    private_key = _load_private_key(private_key_pem)
    signature_bytes = private_key.sign(
        signing_string.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")

    # Build Authorization header
    key_id = "{}/{}/{}".format(tenancy_ocid, user_ocid, fingerprint)
    headers_str = " ".join(signing_headers)
    auth_header = (
        'Signature version="1",'
        'keyId="{}",'
        'algorithm="rsa-sha256",'
        'headers="{}",'
        'signature="{}"'
    ).format(key_id, headers_str, signature_b64)
    headers["Authorization"] = auth_header

    return headers


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def oci_request(method, region, service_endpoint, path,
                tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                verify=True, proxies=None, query_params=None, body=None):
    """Make an authenticated request to the OCI REST API.

    Args:
        method: HTTP method
        region: OCI region (e.g. us-ashburn-1)
        service_endpoint: Base domain template (e.g. iaas.{region}.oraclecloud.com)
        path: API path (e.g. /20160918/instances)
        tenancy_ocid, user_ocid, fingerprint, private_key_pem: Auth credentials
        verify: SSL verification
        proxies: Proxy dict
        query_params: Dict of query parameters
        body: JSON body dict for POST/PUT (will be serialized)

    Returns:
        requests.Response object
    """
    base_url = "https://{}".format(service_endpoint.format(region=region))
    url = "{}{}".format(base_url, path)

    if query_params:
        qs = urlencode(query_params)
        url = "{}?{}".format(url, qs)

    headers = {}
    body_str = None
    if body is not None:
        import json as json_mod
        body_str = json_mod.dumps(body)

    _sign_request(method, url, headers, tenancy_ocid, user_ocid,
                  fingerprint, private_key_pem, body=body_str)

    resp = requests.request(method.upper(), url, headers=headers,
                            verify=verify, proxies=proxies, data=body_str)
    resp.raise_for_status()
    return resp


def oci_paginated_get(region, service_endpoint, path, query_params,
                      tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                      verify=True, proxies=None):
    """Fetch all pages from a paginated OCI list endpoint.

    OCI pagination: response header 'opc-next-page' contains the next page token.
    Pass as 'page' query parameter in the next request.

    Returns:
        list of all items across all pages
    """
    all_items = []
    params = dict(query_params) if query_params else {}

    while True:
        resp = oci_request("GET", region, service_endpoint, path,
                           tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                           verify=verify, proxies=proxies, query_params=params)
        data = resp.json()
        if isinstance(data, list):
            all_items.extend(data)

        next_page = resp.headers.get("opc-next-page")
        if not next_page:
            break
        params["page"] = next_page

    return all_items


# ---------------------------------------------------------------------------
# Identity API wrappers
# ---------------------------------------------------------------------------

IDENTITY_ENDPOINT = "identity.{region}.oraclecloud.com"
IAAS_ENDPOINT = "iaas.{region}.oraclecloud.com"


def list_region_subscriptions(region, tenancy_ocid, user_ocid, fingerprint,
                              private_key_pem, verify=True, proxies=None):
    """List all subscribed regions for the tenancy.

    Returns:
        list of region subscription dicts with keys: regionKey, regionName,
        status, isHomeRegion
    """
    resp = oci_request("GET", region, IDENTITY_ENDPOINT,
                       "/20160918/tenancies/{}/regionSubscriptions".format(tenancy_ocid),
                       tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                       verify=verify, proxies=proxies)
    return resp.json()


def get_target_regions(region_param, tenancy_ocid, user_ocid, fingerprint,
                       private_key_pem, verify=True, proxies=None):
    """Determine target regions from user config or auto-discovery.

    Args:
        region_param: Region string from system.conf, or empty for auto-discovery

    Returns:
        list of region name strings (e.g. ["us-ashburn-1", "eu-frankfurt-1"])
    """
    if region_param and region_param.strip():
        return [region_param.strip()]

    # Auto-discover: need a bootstrap region for the Identity API call
    # Use us-ashburn-1 as default bootstrap (OCI Identity is global)
    bootstrap = "us-ashburn-1"
    subscriptions = list_region_subscriptions(
        bootstrap, tenancy_ocid, user_ocid, fingerprint, private_key_pem,
        verify=verify, proxies=proxies
    )
    regions = []
    for sub in subscriptions:
        if sub.get("status") == "READY":
            name = sub.get("regionName", "")
            if name:
                regions.append(name)
    if not regions:
        raise Exception("No subscribed OCI regions found.")
    return regions


def list_compartments(region, tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                      verify=True, proxies=None):
    """List all compartments recursively in the tenancy.

    Uses compartmentIdInSubtree=true and accessLevel=ACCESSIBLE to get
    the full compartment hierarchy in a single paginated call.

    Returns:
        list of compartment dicts (does NOT include the root/tenancy compartment)
    """
    query_params = {
        "compartmentId": tenancy_ocid,
        "compartmentIdInSubtree": "true",
        "accessLevel": "ACCESSIBLE",
        "lifecycleState": "ACTIVE"
    }
    return oci_paginated_get(
        region, IDENTITY_ENDPOINT, "/20160918/compartments",
        query_params, tenancy_ocid, user_ocid, fingerprint, private_key_pem,
        verify=verify, proxies=proxies
    )


# ---------------------------------------------------------------------------
# Compute API wrappers
# ---------------------------------------------------------------------------

def list_instances(region, compartment_id, tenancy_ocid, user_ocid, fingerprint,
                   private_key_pem, verify=True, proxies=None):
    """List all compute instances in a compartment."""
    query_params = {"compartmentId": compartment_id}
    return oci_paginated_get(
        region, IAAS_ENDPOINT, "/20160918/instances",
        query_params, tenancy_ocid, user_ocid, fingerprint, private_key_pem,
        verify=verify, proxies=proxies
    )


def get_instance(region, instance_id, tenancy_ocid, user_ocid, fingerprint,
                 private_key_pem, verify=True, proxies=None):
    """Get details for a single compute instance."""
    resp = oci_request("GET", region, IAAS_ENDPOINT,
                       "/20160918/instances/{}".format(instance_id),
                       tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                       verify=verify, proxies=proxies)
    return resp.json()


def get_image(region, image_id, tenancy_ocid, user_ocid, fingerprint,
              private_key_pem, verify=True, proxies=None):
    """Get image details (operatingSystem, operatingSystemVersion)."""
    resp = oci_request("GET", region, IAAS_ENDPOINT,
                       "/20160918/images/{}".format(image_id),
                       tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                       verify=verify, proxies=proxies)
    return resp.json()


def resolve_image_os(region, instance, tenancy_ocid, user_ocid, fingerprint,
                     private_key_pem, verify=True, proxies=None, cache=None):
    """Resolve the OS name for an instance by looking up its source image.

    Uses cache to avoid redundant lookups (many instances share the same image).

    Args:
        instance: OCI instance dict from the API
        cache: Optional dict mapping image_id -> os_string

    Returns:
        String like "Canonical Ubuntu 24.04" or "" on failure
    """
    source_details = instance.get("sourceDetails") or {}
    image_id = source_details.get("imageId", "")
    if not image_id:
        return ""

    if cache is not None and image_id in cache:
        return cache[image_id]

    os_string = ""
    try:
        img = get_image(region, image_id, tenancy_ocid, user_ocid,
                        fingerprint, private_key_pem, verify=verify, proxies=proxies)
        os_name = img.get("operatingSystem", "")
        os_version = img.get("operatingSystemVersion", "")
        if os_name and os_version:
            os_string = "{} {}".format(os_name, os_version)
        elif os_name:
            os_string = os_name
        else:
            os_string = img.get("displayName", "")
    except Exception as e:
        logging.warning("OCI resolve_image_os: failed for image {}: {}".format(
            image_id, str(e)))

    if cache is not None:
        cache[image_id] = os_string

    return os_string


# ---------------------------------------------------------------------------
# Networking API wrappers (VNICs)
# ---------------------------------------------------------------------------

def list_vnic_attachments(region, compartment_id, instance_id,
                          tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                          verify=True, proxies=None):
    """List VNIC attachments for an instance."""
    query_params = {
        "compartmentId": compartment_id,
        "instanceId": instance_id
    }
    return oci_paginated_get(
        region, IAAS_ENDPOINT, "/20160918/vnicAttachments",
        query_params, tenancy_ocid, user_ocid, fingerprint, private_key_pem,
        verify=verify, proxies=proxies
    )


def get_vnic(region, vnic_id, tenancy_ocid, user_ocid, fingerprint,
             private_key_pem, verify=True, proxies=None):
    """Get VNIC details (MAC address, private IP, public IP)."""
    resp = oci_request("GET", region, IAAS_ENDPOINT,
                       "/20160918/vnics/{}".format(vnic_id),
                       tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                       verify=verify, proxies=proxies)
    return resp.json()


# ---------------------------------------------------------------------------
# Networking API wrappers (Subnets, VCNs)
# ---------------------------------------------------------------------------

def get_subnet(region, subnet_id, tenancy_ocid, user_ocid, fingerprint,
               private_key_pem, verify=True, proxies=None):
    """Get subnet details (displayName, vcnId)."""
    resp = oci_request("GET", region, IAAS_ENDPOINT,
                       "/20160918/subnets/{}".format(subnet_id),
                       tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                       verify=verify, proxies=proxies)
    return resp.json()


def get_vcn(region, vcn_id, tenancy_ocid, user_ocid, fingerprint,
            private_key_pem, verify=True, proxies=None):
    """Get VCN details (displayName)."""
    resp = oci_request("GET", region, IAAS_ENDPOINT,
                       "/20160918/vcns/{}".format(vcn_id),
                       tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                       verify=verify, proxies=proxies)
    return resp.json()


# ---------------------------------------------------------------------------
# Block Storage API wrappers
# ---------------------------------------------------------------------------

def list_boot_volume_attachments(region, availability_domain, compartment_id,
                                 instance_id, tenancy_ocid, user_ocid, fingerprint,
                                 private_key_pem, verify=True, proxies=None):
    """List boot volume attachments for an instance."""
    query_params = {
        "availabilityDomain": availability_domain,
        "compartmentId": compartment_id,
        "instanceId": instance_id
    }
    return oci_paginated_get(
        region, IAAS_ENDPOINT, "/20160918/bootVolumeAttachments",
        query_params, tenancy_ocid, user_ocid, fingerprint, private_key_pem,
        verify=verify, proxies=proxies
    )


def get_boot_volume(region, boot_volume_id, tenancy_ocid, user_ocid, fingerprint,
                    private_key_pem, verify=True, proxies=None):
    """Get boot volume details (sizeInGBs)."""
    resp = oci_request("GET", region, IAAS_ENDPOINT,
                       "/20160918/bootVolumes/{}".format(boot_volume_id),
                       tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                       verify=verify, proxies=proxies)
    return resp.json()


def list_volume_attachments(region, compartment_id, instance_id,
                            tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                            verify=True, proxies=None):
    """List block volume attachments for an instance."""
    query_params = {
        "compartmentId": compartment_id,
        "instanceId": instance_id
    }
    return oci_paginated_get(
        region, IAAS_ENDPOINT, "/20160918/volumeAttachments",
        query_params, tenancy_ocid, user_ocid, fingerprint, private_key_pem,
        verify=verify, proxies=proxies
    )


def get_volume(region, volume_id, tenancy_ocid, user_ocid, fingerprint,
               private_key_pem, verify=True, proxies=None):
    """Get block volume details (displayName, sizeInGBs)."""
    resp = oci_request("GET", region, IAAS_ENDPOINT,
                       "/20160918/volumes/{}".format(volume_id),
                       tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                       verify=verify, proxies=proxies)
    return resp.json()


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def format_mac(mac_str):
    """Convert OCI MAC format (XX:XX:XX:XX:XX:XX) to Forescout format (12-char hex).

    OCI returns MAC addresses like '00:00:17:02:F4:88'.
    Forescout expects '00001702F488' (12-char uppercase hex, no separators).
    """
    if not mac_str:
        return None
    return mac_str.replace(":", "").replace("-", "").upper()


def format_mac_colon(mac_hex):
    """Convert 12-char hex MAC to colon-separated format for display.

    '00001702F488' -> '00:00:17:02:F4:88'
    """
    if not mac_hex or len(mac_hex) != 12:
        return mac_hex
    return ":".join(mac_hex[i:i+2] for i in range(0, 12, 2))


def iso_to_epoch(iso_str):
    """Convert OCI ISO 8601 timestamp to epoch seconds for Forescout date properties.

    OCI format: '2023-10-15T10:30:00.000Z' or '2023-10-15T10:30:00.000+00:00'
    """
    if not iso_str:
        return 0
    # Handle both Z suffix and +00:00 timezone formats
    iso_str = iso_str.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso_str)
        return math.floor(dt.timestamp())
    except (ValueError, AttributeError):
        return 0


def test_connection(region, tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                    verify=True, proxies=None):
    """Test OCI connectivity by listing instances with limit=1.

    Returns the requests.Response to verify auth works.
    """
    query_params = {
        "compartmentId": tenancy_ocid,
        "limit": "1"
    }
    return oci_request("GET", region, IAAS_ENDPOINT, "/20160918/instances",
                       tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                       verify=verify, proxies=proxies, query_params=query_params)


def resolve_network_names(region, subnet_id, tenancy_ocid, user_ocid, fingerprint,
                          private_key_pem, verify=True, proxies=None, cache=None):
    """Resolve subnet and VCN display names from a subnet OCID.

    Uses cache to avoid redundant lookups (many instances share the same subnet/VCN).

    Args:
        cache: Optional dict for caching. Key: subnet_id, Value: (subnet_name, vcn_name)

    Returns:
        tuple (subnet_name, vcn_name) or fallback to OCIDs on failure
    """
    if not subnet_id:
        return "", ""

    if cache is not None and subnet_id in cache:
        return cache[subnet_id]

    subnet_name = subnet_id
    vcn_name = ""

    try:
        subnet = get_subnet(region, subnet_id, tenancy_ocid, user_ocid,
                            fingerprint, private_key_pem, verify=verify, proxies=proxies)
        subnet_name = subnet.get("displayName", subnet_id)
        vcn_id = subnet.get("vcnId", "")

        if vcn_id:
            try:
                vcn = get_vcn(region, vcn_id, tenancy_ocid, user_ocid,
                              fingerprint, private_key_pem, verify=verify, proxies=proxies)
                vcn_name = vcn.get("displayName", vcn_id)
            except Exception:
                vcn_name = vcn_id
    except Exception:
        pass

    result = (subnet_name, vcn_name)
    if cache is not None:
        cache[subnet_id] = result

    return result


def build_instance_properties(instance, compartment_map, boot_volume_size, block_volumes,
                              network_info=None, image_os=""):
    """Build the Forescout properties dict for an OCI compute instance.

    Args:
        instance: OCI instance dict from the API
        compartment_map: dict mapping compartment OCID -> name
        boot_volume_size: Boot volume size in GB (int) or 0
        block_volumes: list of dicts [{"name": ..., "size_gb": ...}, ...]
        network_info: Optional dict with keys: private_ip, public_ip, hostname,
                      subnet_name, vcn_name
        image_os: Resolved OS string (e.g. "Canonical Ubuntu 24.04")

    Returns:
        dict of Forescout property tags -> values
    """
    shape_config = instance.get("shapeConfig") or {}
    freeform_tags = instance.get("freeformTags") or {}

    # Stringify freeform tags
    import json as json_mod
    tags_str = json_mod.dumps(freeform_tags) if freeform_tags else ""

    props = {
        "connect_oci_instance_name": instance.get("displayName", ""),
        "connect_oci_instance_ocid": instance.get("id", ""),
        "connect_oci_shape": instance.get("shape", ""),
        "connect_oci_lifecycle_state": instance.get("lifecycleState", ""),
        "connect_oci_compartment_name": compartment_map.get(
            instance.get("compartmentId", ""), "Unknown"
        ),
        "connect_oci_availability_domain": instance.get("availabilityDomain", ""),
        "connect_oci_fault_domain": instance.get("faultDomain", ""),
        "connect_oci_ocpus": int(shape_config.get("ocpus", 0)),
        "connect_oci_memory_gb": int(shape_config.get("memoryInGBs", 0)),
        "connect_oci_image_os": image_os,
        "connect_oci_creation_time": iso_to_epoch(instance.get("timeCreated", "")),
        "connect_oci_freeform_tags": tags_str,
        "connect_oci_boot_volume_size_gb": boot_volume_size,
        "connect_oci_block_volumes": block_volumes,
    }

    # Network properties from VNIC and subnet/VCN lookups
    net = network_info or {}
    props["connect_oci_private_ip"] = net.get("private_ip", "") or ""
    props["connect_oci_public_ip"] = net.get("public_ip", "") or ""
    props["connect_oci_hostname"] = net.get("hostname", "")
    props["connect_oci_vnic_name"] = net.get("vnic_name", "")
    props["connect_oci_subnet"] = net.get("subnet_name", "")
    props["connect_oci_vcn"] = net.get("vcn_name", "")

    return props


def get_instance_network_info(region, compartment_id, instance_id,
                              tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                              verify=True, proxies=None):
    """Get the primary VNIC network details for an instance.

    Returns:
        dict with keys: mac, private_ip, public_ip, hostname, subnet_id
        mac and private_ip may be None on failure.
    """
    empty = {"mac": None, "private_ip": None, "public_ip": "", "hostname": "", "subnet_id": ""}

    try:
        vnic_attachments = list_vnic_attachments(
            region, compartment_id, instance_id,
            tenancy_ocid, user_ocid, fingerprint, private_key_pem,
            verify=verify, proxies=proxies
        )
    except Exception:
        return empty

    if not vnic_attachments:
        return empty

    # Find the primary VNIC (isPrimary == True) or use the first one
    primary_att = None
    for att in vnic_attachments:
        if att.get("lifecycleState") != "ATTACHED":
            continue
        if att.get("isPrimary", False):
            primary_att = att
            break
    if primary_att is None and vnic_attachments:
        # Fall back to first attached VNIC
        for att in vnic_attachments:
            if att.get("lifecycleState") == "ATTACHED":
                primary_att = att
                break

    if not primary_att or not primary_att.get("vnicId"):
        return empty

    try:
        vnic = get_vnic(
            region, primary_att["vnicId"],
            tenancy_ocid, user_ocid, fingerprint, private_key_pem,
            verify=verify, proxies=proxies
        )
    except Exception:
        return empty

    mac_hex = format_mac(vnic.get("macAddress", ""))
    private_ip = vnic.get("privateIp", "")
    public_ip = vnic.get("publicIp", "")
    hostname = vnic.get("hostnameLabel", "")
    vnic_name = vnic.get("displayName", "")
    subnet_id = vnic.get("subnetId", "")

    return {
        "mac": mac_hex,
        "private_ip": private_ip or None,
        "public_ip": public_ip or "",
        "hostname": hostname or "",
        "vnic_name": vnic_name or "",
        "subnet_id": subnet_id or "",
    }


def get_instance_volumes(region, availability_domain, compartment_id, instance_id,
                         tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                         verify=True, proxies=None):
    """Get boot volume size and block volumes for an instance.

    Returns:
        tuple (boot_volume_size_gb, block_volumes_list)
        boot_volume_size_gb: int
        block_volumes_list: list of dicts [{"name": ..., "size_gb": ...}, ...]
    """
    boot_volume_size = 0
    block_volumes = []

    # Get boot volume
    try:
        boot_attachments = list_boot_volume_attachments(
            region, availability_domain, compartment_id, instance_id,
            tenancy_ocid, user_ocid, fingerprint, private_key_pem,
            verify=verify, proxies=proxies
        )
        for att in boot_attachments:
            if att.get("lifecycleState") == "ATTACHED" and att.get("bootVolumeId"):
                try:
                    bv = get_boot_volume(
                        region, att["bootVolumeId"],
                        tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                        verify=verify, proxies=proxies
                    )
                    boot_volume_size = int(bv.get("sizeInGBs", 0))
                except Exception:
                    pass
                break
    except Exception:
        pass

    # Get block volumes
    try:
        vol_attachments = list_volume_attachments(
            region, compartment_id, instance_id,
            tenancy_ocid, user_ocid, fingerprint, private_key_pem,
            verify=verify, proxies=proxies
        )
        for att in vol_attachments:
            if att.get("lifecycleState") == "ATTACHED" and att.get("volumeId"):
                try:
                    vol = get_volume(
                        region, att["volumeId"],
                        tenancy_ocid, user_ocid, fingerprint, private_key_pem,
                        verify=verify, proxies=proxies
                    )
                    block_volumes.append({
                        "name": vol.get("displayName", ""),
                        "size_gb": int(vol.get("sizeInGBs", 0))
                    })
                except Exception:
                    pass
    except Exception:
        pass

    return boot_volume_size, block_volumes
