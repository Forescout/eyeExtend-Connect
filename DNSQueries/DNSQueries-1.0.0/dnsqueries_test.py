"""DNS Queries app library; injected into Connect scripts (do not import it)."""
import ipaddress
import json
import logging
import re
import time
import uuid

DNS_PROPERTY = "connect_dnsqueries_domains"
DNS_SCOPE_ALL = "all"
DNS_SCOPE_UNKNOWN_FUNCTION = "unknown_function"
DNSMASQ = re.compile(r"\bquery\[(?P<qtype>[A-Za-z0-9-]+)\]\s+(?P<domain>\S+)\s+from\s+(?P<client_ip>\S+)\s*$")
BIND = re.compile(r"\bclient\s+(?:@\S+\s+)?(?P<client_ip>[0-9A-Fa-f:.]+)#\d+\s+(?:\([^\r\n]*?\)\s*)?:\s+query:\s+(?P<domain>\S+)\s+IN\s+(?P<qtype>[A-Za-z0-9-]+)\b")


def dns_client(value):
    value = str(value).strip()
    if value.startswith("["):
        match = re.fullmatch(r"\[([^\]]+)\](?::\d+)?", value)
        if not match:
            raise ValueError("Invalid bracketed client IP")
        value = match.group(1)
    elif "#" in value:
        value = value.rsplit("#", 1)[0]
    if "%" in value:
        raise ValueError("Scoped IP cannot identify a unique endpoint")
    address = ipaddress.ip_address(value)
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        address = address.ipv4_mapped
    if address.is_loopback or address.is_unspecified or address.is_multicast or address.is_link_local:
        raise ValueError("Client IP is not an identifiable network endpoint")
    if str(address) == "255.255.255.255":
        raise ValueError("Broadcast client address")
    return str(address)


def dns_domain(value):
    value = str(value).lower()
    if value.endswith("."):
        value = value[:-1]
    if not value or len(value) > 253:
        raise ValueError("Invalid DNS name length")
    # Underscores are intentional: SRV queries in the supplied capture use them.
    labels = value.split(".")
    if any(not re.fullmatch(r"[a-z0-9_*\-]{1,63}", label) for label in labels):
        raise ValueError("Invalid DNS label; use ASCII/punycode names")
    return value


def dns_scope(params):
    # Default defensively for missing/legacy configuration: broad DNS
    # enrichment is expensive on large deployments.
    scope = params.get("connect_dnsqueries_scope", DNS_SCOPE_UNKNOWN_FUNCTION) or DNS_SCOPE_UNKNOWN_FUNCTION
    if scope not in (DNS_SCOPE_ALL, DNS_SCOPE_UNKNOWN_FUNCTION):
        raise ValueError("Unknown DNS query target scope")
    return scope


def dns_should_publish(params):
    """Return whether the DNS property may be returned for this endpoint."""
    if dns_scope(params) == DNS_SCOPE_ALL:
        return True
    return str(params.get("function", "")).strip().lower() == "unknown"


def dns_parse(message, params):
    if not isinstance(message, str) or len(message) > 16384:
        return None
    # One event per call. Reject multiline input rather than attribute multiple events.
    message = message.strip()
    if "\n" in message or "\r" in message:
        return None
    mode = params.get("connect_dnsqueries_format", "auto") or "auto"
    fields = None
    if mode == "custom":
        fields = dnsqueries_common.dns_custom_fields(dnsqueries_common.dns_pattern(params), message)
    elif mode in ("auto", "dnsmasq", "bind"):
        patterns = [DNSMASQ, BIND] if mode == "auto" else [DNSMASQ if mode == "dnsmasq" else BIND]
        for pattern in patterns:
            match = pattern.search(message)
            if match:
                fields = match.groupdict()
                break
    elif mode == "json":
        start = message.find("{")
        if start >= 0:
            try:
                payload = json.loads(message[start:])
                if isinstance(payload, dict) and payload.get("event") == "query":
                    fields = {"client_ip": payload.get("client_ip"), "domain": payload.get("qname")}
            except (ValueError, TypeError):
                return None
    else:
        raise ValueError("Unknown DNS log format")
    if not fields or not fields.get("client_ip") or not fields.get("domain"):
        return None
    try:
        return dns_client(fields["client_ip"]), dns_domain(fields["domain"])
    except ValueError:
        return None


def dns_database(app_name):
    from persistent_util import PersistUtil
    return PersistUtil(app_name)


def dns_receive(params, db, now=None):
    parsed = dns_parse(params.get("connect_syslog_message"), params)
    if parsed is None:
        return {}
    ip, domain = parsed
    domains = dnsqueries_common.dns_snapshot(db, ip, time.time() if now is None else now, domain)
    # In Unknown Function mode the event is retained, but the property is
    # returned only by the resolver after it receives the host's function
    # dependency. This prevents DNS data from being published to classified
    # endpoints while preserving events if an endpoint later becomes Unknown.
    if dns_scope(params) == DNS_SCOPE_UNKNOWN_FUNCTION:
        return {"ip": ip}
    # Deliberately omit online: syslog only updates existing endpoints.
    return {"ip": ip, "properties": {DNS_PROPERTY: domains}}


def dns_resolve(params, db, now=None):
    ip = dns_client(params.get("ip", ""))
    if not dns_should_publish(params):
        return {"properties": {DNS_PROPERTY: []}}
    domains = dnsqueries_common.dns_snapshot(db, ip, time.time() if now is None else now)
    return {"properties": {DNS_PROPERTY: domains}}


# Standalone Connect entry point
try:
    mode = params.get("connect_dnsqueries_format", "auto") or "auto"
    if mode == "custom":
        dnsqueries_common.dns_pattern(params)
    elif mode not in ("auto", "dnsmasq", "bind", "json"):
        raise ValueError("Unknown DNS log format")
    db = dns_database(connect_app_name)
    probe = "test-" + uuid.uuid4().hex
    if not db.save("dns_health", probe, "ok") or db.get("dns_health", probe) != "ok":
        raise RuntimeError("Connect persistent storage is unavailable")
    db.delete("dns_health", probe)
    response = {"succeeded": True, "result_msg": "Parser configuration and persistent storage OK. This does not test syslog delivery. Configure a policy recheck to expire idle-host queries."}
except Exception as error:
    response = {"succeeded": False, "result_msg": str(error)}
