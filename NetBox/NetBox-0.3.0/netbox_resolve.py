"""NetBox lookups shared by the NetBox Connect App scripts (prepended to each script at build time)."""
import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request

NB_MAC_TEXT = re.compile(
    r"(?<![0-9a-f])((?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}|(?:[0-9a-f]{4}\.){2}[0-9a-f]{4})(?![0-9a-f])", re.I)
NB_INTERFACE_PATHS = {
    "dcim.interface": "dcim/interfaces/",
    "virtualization.vminterface": "virtualization/interfaces/",
}


def nb_config(params, context):
    url = (params.get("connect_netbox_url") or "").strip().rstrip("/")
    token = (params.get("connect_netbox_token") or "").strip()
    if not url.lower().startswith(("http://", "https://")):
        raise ValueError("NetBox URL must start with http:// or https://")
    if url.lower().endswith("/api"):
        url = url[:-4]
    if not token:
        raise ValueError("NetBox API token is empty")
    # NetBox 4.5+ tokens (nbt_<key>.<secret>) use the Bearer scheme, older ones the Token scheme.
    scheme = "Bearer" if token.startswith("nbt_") else "Token"
    return {
        "url": url,
        "auth": "{} {}".format(scheme, token),
        "context": context,
        "mac_in_text": str(params.get("connect_netbox_mac_in_text", "true")).lower() == "true",
    }


def nb_get(cfg, path, query=None):
    url = "{}/api/{}".format(cfg["url"], path)
    if query:
        url += "?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(url, headers={"Authorization": cfg["auth"], "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, context=cfg["context"], timeout=20) as reply:
            return json.loads(reply.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code in (401, 403):
            raise RuntimeError("NetBox rejected the API token (HTTP {})".format(error.code))
        raise RuntimeError("NetBox answered HTTP {} for {}".format(error.code, path))


def nb_post(cfg, path, body):
    request = urllib.request.Request(
        "{}/api/{}".format(cfg["url"], path), data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"Authorization": cfg["auth"], "Accept": "application/json", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, context=cfg["context"], timeout=20) as reply:
            return json.loads(reply.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:300]
        if error.code in (401, 403):
            raise RuntimeError("NetBox refused the change (HTTP {}). The token must be write-enabled and its "
                               "user needs permission to add IP addresses. {}".format(error.code, detail))
        raise RuntimeError("NetBox answered HTTP {}: {}".format(error.code, detail))


def nb_add_ip(cfg, ip, mac, status, description):
    """Create the IP address record of one endpoint. Returns the link to the new record."""
    existing = nb_find_ip(cfg, ip)
    if existing:
        raise RuntimeError("{} is already recorded in NetBox: {}/ipam/ip-addresses/{}/".format(
            ip, cfg["url"], existing.get("id")))
    status = (status or "active").strip().lower()
    if status not in ("active", "reserved", "dhcp", "slaac"):
        raise ValueError("Status must be active, reserved, dhcp or slaac")
    # Same mask as the prefix the address belongs to; a host address when NetBox has no such prefix.
    prefix = nb_prefix(cfg, ip).get("connect_netbox_prefix") or ""
    length = prefix.split("/")[-1] if "/" in prefix else "32"
    text = (description or "").strip() or "Added from Forescout"
    mac = nb_mac(mac)
    if mac and mac not in {nb_mac(found) for found in NB_MAC_TEXT.findall(text)}:
        text = "{} ({})".format(text, nb_colon(mac))
    record = nb_post(cfg, "ipam/ip-addresses/", {
        "address": "{}/{}".format(ip, length), "status": status, "description": text[:200]})
    return "{}/ipam/ip-addresses/{}/".format(cfg["url"], record.get("id"))


def nb_results(cfg, path, query):
    # An endpoint or filter that this NetBox version lacks is the same as "nothing found".
    try:
        return nb_get(cfg, path, query).get("results") or []
    except RuntimeError as error:
        if "HTTP 404" in str(error) or "HTTP 400" in str(error):
            return []
        raise


def nb_mac(value):
    clean = re.sub(r"[^0-9a-f]", "", str(value or "").lower())
    return clean if len(clean) == 12 else ""


def nb_colon(mac):
    return ":".join(mac[i:i + 2] for i in range(0, 12, 2))


def nb_private_mac(mac):
    # Locally administered bit: the address was made up by the endpoint (private Wi-Fi address).
    return bool(mac) and bool(int(mac[1], 16) & 2)


def nb_name(value):
    if isinstance(value, dict):
        return str(value.get("display") or value.get("name") or value.get("label") or value.get("value") or "")
    return str(value or "")


def nb_interface_macs(interface):
    macs = {nb_mac(interface.get("mac_address"))}
    primary = interface.get("primary_mac_address")
    if isinstance(primary, dict):
        macs.add(nb_mac(primary.get("mac_address")))
    for row in interface.get("mac_addresses") or []:
        if isinstance(row, dict):
            macs.add(nb_mac(row.get("mac_address")))
    macs.discard("")
    return macs


def nb_record_macs(cfg, record):
    macs = set()
    path = NB_INTERFACE_PATHS.get(record.get("assigned_object_type") or "")
    if path and record.get("assigned_object_id"):
        macs |= nb_interface_macs(nb_get(cfg, "{}{}/".format(path, record["assigned_object_id"])))
    if cfg["mac_in_text"]:
        text = "{} {}".format(record.get("description") or "", record.get("comments") or "")
        macs |= {nb_mac(found) for found in NB_MAC_TEXT.findall(text)}
    macs.discard("")
    return macs


def nb_find_ip(cfg, ip):
    rows = nb_results(cfg, "ipam/ip-addresses/", {"address": ip, "limit": 10})
    live = [row for row in rows if nb_name(row.get("status", {}).get("value") if isinstance(row.get("status"), dict) else row.get("status")) != "deprecated"]
    return live[0] if live else None


def nb_find_mac(cfg, mac):
    """Return the IP address record (or None) of the interface that owns this MAC."""
    colon = nb_colon(mac)
    for row in nb_results(cfg, "dcim/mac-addresses/", {"mac_address": colon, "limit": 5}):
        path = NB_INTERFACE_PATHS.get(row.get("assigned_object_type") or "")
        if path and row.get("assigned_object_id"):
            return {"interface": (path, row["assigned_object_id"])}
    for path in ("dcim/interfaces/", "virtualization/interfaces/"):
        for row in nb_results(cfg, path, {"mac_address": colon, "limit": 5}):
            return {"interface": (path, row["id"])}
    if cfg["mac_in_text"]:
        for text in (colon, colon.replace(":", "-"), mac, ".".join(mac[i:i + 4] for i in (0, 4, 8))):
            for row in nb_results(cfg, "ipam/ip-addresses/", {"q": text, "limit": 5}):
                if mac in nb_record_macs(dict(cfg, mac_in_text=True), dict(row, assigned_object_id=None)):
                    return {"record": row}
    return None


def nb_value(field):
    return field.get("value") if isinstance(field, dict) else field


def nb_describe(cfg, record, ip, macs=None):
    """Properties taken from an IP address record and what it is attached to."""
    props = {
        "connect_netbox_ip_status": nb_value(record.get("status")),
        "connect_netbox_address": record.get("address"),
        "connect_netbox_ip_role": nb_value(record.get("role")),
        "connect_netbox_vrf": nb_name(record.get("vrf")),
        "connect_netbox_dns_name": record.get("dns_name"),
        "connect_netbox_description": record.get("description"),
        "connect_netbox_comments": (record.get("comments") or "").strip()[:500],
        "connect_netbox_tenant": nb_name(record.get("tenant")),
        "connect_netbox_tags": [nb_name(tag) for tag in record.get("tags") or []],
        "connect_netbox_url": "{}/ipam/ip-addresses/{}/".format(cfg["url"], record.get("id")),
        "connect_netbox_last_updated": (record.get("last_updated") or "")[:10],
    }
    if macs is None:
        macs = nb_record_macs(cfg, record)
    props["connect_netbox_mac"] = ", ".join(sorted(nb_colon(mac) for mac in macs))
    parent = record.get("assigned_object") or {}
    owner = parent.get("device") or parent.get("virtual_machine")
    if parent.get("name"):
        props["connect_netbox_interface"] = parent["name"]
    if isinstance(owner, dict) and owner.get("id"):
        kind = "dcim/devices/" if parent.get("device") else "virtualization/virtual-machines/"
        props["connect_netbox_device"] = nb_name(owner)
        try:
            props.update(nb_device(nb_get(cfg, "{}{}/".format(kind, owner["id"]))))
        except RuntimeError as error:
            logging.debug("NetBox: no detail for {}: {}".format(owner, error))
    return props


def nb_device(detail):
    """Inventory data of the device or virtual machine that owns the address."""
    kind = detail.get("device_type") or {}
    model = " ".join(part for part in (nb_name(kind.get("manufacturer")), kind.get("model") or "") if part)
    if not model and detail.get("cluster"):
        model = "Virtual machine on {}".format(nb_name(detail["cluster"]))
    place = " / ".join(part for part in (nb_name(detail.get("location")), nb_name(detail.get("rack"))) if part)
    if place and detail.get("position"):
        place += " U{}".format(detail["position"])
    return {
        "connect_netbox_device_role": nb_name(detail.get("role") or detail.get("device_role")),
        "connect_netbox_device_status": nb_value(detail.get("status")),
        "connect_netbox_device_type": model,
        "connect_netbox_platform": nb_name(detail.get("platform")),
        "connect_netbox_serial": detail.get("serial"),
        "connect_netbox_asset_tag": detail.get("asset_tag"),
        "connect_netbox_site": nb_name(detail.get("site")),
        "connect_netbox_location": place,
    }


def nb_prefix(cfg, ip):
    rows = nb_results(cfg, "ipam/prefixes/", {"contains": ip, "limit": 50})
    if not rows:
        return {}
    best = max(rows, key=lambda row: int(str(row.get("prefix", "0/0")).split("/")[-1]))
    props = {"connect_netbox_prefix": best.get("prefix"),
             "connect_netbox_prefix_description": best.get("description")}
    vlan = best.get("vlan")
    if isinstance(vlan, dict):
        props["connect_netbox_vlan"] = "{} ({})".format(vlan.get("name"), vlan.get("vid"))
    site = best.get("site") or (best.get("scope") if "site" in str(best.get("scope_type") or "") else None)
    if site:
        props["connect_netbox_site"] = nb_name(site)
    return props


def nb_ip_range(cfg, ip):
    """Name of the IP range (DHCP pool, reserved block...) that holds the address, if any."""
    for row in nb_results(cfg, "ipam/ip-ranges/", {"contains": ip, "limit": 5}):
        label = row.get("description") or row.get("display") or ""
        role = nb_name(row.get("role"))
        return "{} ({})".format(label, role) if role else label
    return ""


def nb_summary(props):
    """One line with the essentials, for the device profile and reports."""
    parts = [props.get("connect_netbox_address"), props.get("connect_netbox_ip_status"),
             props.get("connect_netbox_dns_name"), props.get("connect_netbox_device"),
             props.get("connect_netbox_description")]
    network = " ".join(part for part in (props.get("connect_netbox_prefix"),
                                         "VLAN " + props["connect_netbox_vlan"] if props.get("connect_netbox_vlan") else "")
                       if part)
    parts.append(network)
    return " | ".join(str(part) for part in parts if part)


def nb_lookup(cfg, ip, mac):
    """Decide the NetBox status of one endpoint and collect its NetBox properties."""
    mac = nb_mac(mac)
    props = {}
    record = nb_find_ip(cfg, ip) if ip else None
    if record:
        known = nb_record_macs(cfg, record)
        status = "mac_mismatch" if known and mac and mac not in known else "documented"
        props.update(nb_describe(cfg, record, ip, known))
    else:
        found = nb_find_mac(cfg, mac) if mac else None
        if found:
            status = "other_ip"
            if "record" in found:
                props.update(nb_describe(cfg, found["record"], ip))
            else:
                path, ident = found["interface"]
                key = "interface_id" if path.startswith("dcim") else "vminterface_id"
                rows = nb_results(cfg, "ipam/ip-addresses/", {key: ident, "limit": 1})
                if rows:
                    props.update(nb_describe(cfg, rows[0], ip))
        else:
            status = "not_found_private_mac" if nb_private_mac(mac) else "not_found"
    if ip:
        for key, value in nb_prefix(cfg, ip).items():
            if not props.get(key):  # the device's own site wins over the prefix's
                props[key] = value
        props["connect_netbox_ip_range"] = nb_ip_range(cfg, ip)
    if props.get("connect_netbox_url"):  # only when NetBox has a record for the endpoint
        props["connect_netbox_summary"] = nb_summary(props)
    props["connect_netbox_status"] = status
    return {key: value for key, value in props.items() if value not in (None, "", [])}


# Standalone Connect entry point
# Resolves the NetBox properties of one endpoint from its IP and MAC address.
response = {}
try:
    host_ip = params.get("ip")
    host_mac = params.get("mac")
    if not host_ip and not host_mac:
        response["error"] = "The endpoint has no IP or MAC address to look up in NetBox."
    else:
        response["properties"] = nb_lookup(nb_config(params, ssl_context), host_ip, host_mac)
except Exception as error:
    response["error"] = "NetBox lookup failed: {}".format(error)
logging.debug("NetBox resolve for ip=[{}] mac=[{}] returned [{}]".format(params.get("ip"), params.get("mac"), response))
