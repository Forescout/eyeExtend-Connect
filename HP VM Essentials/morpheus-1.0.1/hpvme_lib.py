"""
HP VME Connect App - Shared Library
Helpers for talking to the HPE VM Essentials (Morpheus) API.

Library files cannot access params directly, so every value is passed in as an
argument. Library files also do no logging; the calling scripts do that.

Behaviour below was checked against a VM Essentials 9.1.0.2 manager:
  - The server's powerState is the true power state. The instance status
    flipped between "stopped" and "running" while the VM was powered off.
  - computeServerType.format separates hosts ("vmHypervisor") from VMs ("guestVm").
  - Discovered VMs have no instance record, so instance actions cannot apply.
  - The manager's own VM carries "appliance": true.
  - Host records list vnet* NICs that mirror their VMs' NICs. These are ignored.
"""

import json
import re
from datetime import datetime, timezone
from urllib.parse import quote, urlparse

import requests

REQUEST_TIMEOUT = 30  # seconds per API call; scripts have a 2-minute limit overall
PAGE_SIZE = 100

FORMAT_HOST = "vmHypervisor"
FORMAT_VM = "guestVm"


class HpvmeError(Exception):
    """An API failure with a message that is safe to show to the operator."""


# --- Connection settings ----------------------------------------------------


def build_proxies(proxy_enable, proxy_ip, proxy_port, proxy_user="", proxy_pass=""):
    """Build a proxies dict for the requests library from Connect proxy settings."""
    if proxy_enable != "true":
        return None
    if proxy_user:
        proxy_url = f"http://{quote(proxy_user, safe='')}:{quote(proxy_pass, safe='')}@{proxy_ip}:{proxy_port}"
    else:
        proxy_url = f"http://{proxy_ip}:{proxy_port}"
    return {"http": proxy_url, "https": proxy_url}


def get_proxies_from_params(params):
    """Extract proxy settings from params and build a proxies dict."""
    return build_proxies(
        params.get("connect_proxy_enable", ""),
        params.get("connect_proxy_ip", ""),
        params.get("connect_proxy_port", ""),
        params.get("connect_proxy_username", ""),
        params.get("connect_proxy_password", ""),
    )


def _as_list(value):
    """Return a field value as a list.

    Each manager is a separate entry in the Connect GUI. A value can arrive as a
    list (one item per manager) or as a single string (one manager). Strings are
    never split on commas, because passwords can contain commas.
    """
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None or value == "":
        return []
    return [str(value)]


def normalize_url(url):
    """Return a request-ready base URL. A bare IP or hostname is assumed to be https."""
    url = str(url or "").strip().rstrip("/")
    if url and not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    return url


def get_managers(params):
    """Return (url, username, password) for every configured manager.

    The URL is returned as configured, because that value is stored on each
    endpoint and later compared for routing.
    """
    urls = _as_list(params.get("connect_hpvme_url"))
    usernames = _as_list(params.get("connect_hpvme_username"))
    passwords = _as_list(params.get("connect_hpvme_password"))

    managers = []
    for index, url in enumerate(urls):
        username = usernames[index] if index < len(usernames) else (usernames[0] if usernames else "")
        password = passwords[index] if index < len(passwords) else (passwords[0] if passwords else "")
        managers.append((url.strip(), username, password))
    return managers


def get_routed_manager(params):
    """Return (url, username, password) for the manager that owns this endpoint."""
    managers = get_managers(params)
    routed = params.get("connect_controller_ip_tag") or params.get("connect_hpvme_controller_ip") or ""
    routed = normalize_url(routed[0] if isinstance(routed, list) and routed else routed)
    for manager in managers:
        if normalize_url(manager[0]) == routed:
            return manager
    if routed:
        # Never send an action to a different manager: its VM IDs mean something else.
        raise HpvmeError(f"No configured manager matches {routed}.")
    if len(managers) > 1:
        raise HpvmeError("This endpoint has no manager routing information. Wait for the next discovery.")
    if managers:
        return managers[0]
    raise HpvmeError("No HP VME manager is configured.")


# --- HTTP -------------------------------------------------------------------


def _error_message(resp):
    """Pull the API's own error message out of a failed response, if it has one."""
    try:
        body = resp.json()
    except ValueError:
        return ""
    if isinstance(body, dict):
        return str(body.get("msg") or body.get("error_description") or "")
    return ""


def _describe_http_failure(resp):
    code = resp.status_code
    detail = _error_message(resp)
    suffix = f" {detail}" if detail else ""
    if code == 401:
        return "HP VME rejected the login or token (HTTP 401)." + suffix
    if code == 403:
        return "The HP VME user lacks permission for this operation (HTTP 403)." + suffix
    if code == 404:
        return "HP VME could not find this object (HTTP 404). It may have been deleted." + suffix
    return f"HP VME API returned HTTP {code}." + suffix


def _send(method, url, verify, proxies, **kwargs):
    """Send a request, turning connection problems into operator-readable errors."""
    try:
        return requests.request(method, url, verify=verify, proxies=proxies,
                                timeout=REQUEST_TIMEOUT, **kwargs)
    except requests.exceptions.SSLError:
        raise HpvmeError(
            "TLS certificate validation failed. Install a trusted certificate on the "
            "manager, or turn off certificate validation for this entry."
        )
    except requests.exceptions.Timeout:
        raise HpvmeError(f"Timed out after {REQUEST_TIMEOUT} seconds connecting to the HP VME manager.")
    except requests.exceptions.ConnectionError:
        raise HpvmeError("Could not connect to the HP VME manager. Check the URL, network, and proxy settings.")


def get_token(manager_url, username, password, verify=True, proxies=None):
    """Log in and return an access token.

    Tokens from this call last about 30 days. The app logs in whenever a script
    runs rather than storing a token, so a token can never expire unnoticed.
    """
    resp = _send(
        "POST",
        normalize_url(manager_url) + "/oauth/token",
        verify,
        proxies,
        params={"client_id": "morph-api", "grant_type": "password", "scope": "write"},
        data={"username": username, "password": password},
    )
    if resp.status_code in (400, 401):
        raise HpvmeError("HP VME login failed. Check the username and password.")
    if resp.status_code != 200:
        raise HpvmeError(_describe_http_failure(resp))
    try:
        token = resp.json().get("access_token")
    except ValueError:
        token = None
    if not token:
        raise HpvmeError("HP VME login did not return an access token.")
    return token


class Client:
    """A logged-in connection to one HP VME manager."""

    def __init__(self, manager_url, username, password, verify=True, proxies=None):
        self.base_url = normalize_url(manager_url)
        self.verify = verify
        self.proxies = proxies
        token = get_token(manager_url, username, password, verify, proxies)
        self.headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def request(self, method, path, query=None, body=None):
        """Call the API and return its JSON body, or raise HpvmeError."""
        resp = _send(method, self.base_url + path, self.verify, self.proxies,
                     headers=self.headers, params=query, json=body)
        if resp.status_code != 200:
            raise HpvmeError(_describe_http_failure(resp))
        try:
            data = resp.json()
        except ValueError:
            raise HpvmeError("HP VME API returned a response that is not JSON.")
        _raise_if_unsuccessful(data)
        return data

    def get_server(self, server_id):
        """Read one server. The record may or may not be wrapped in a "server" key."""
        data = self.request("GET", f"/api/servers/{server_id}")
        return data.get("server") or data

    def get_instance(self, instance_id):
        """Read one instance. The record may or may not be wrapped in an "instance" key."""
        data = self.request("GET", f"/api/instances/{instance_id}")
        return data.get("instance") or data

    def get_all(self, path, key, query=None):
        """Read every page of a list endpoint."""
        items = []
        offset = 0
        while True:
            page_query = dict(query or {})
            page_query.update({"max": PAGE_SIZE, "offset": offset})
            data = self.request("GET", path, query=page_query)
            page = data.get(key) or []
            items.extend(page)
            total = (data.get("meta") or {}).get("total")
            offset += len(page)
            if not page or len(page) < PAGE_SIZE or (total is not None and offset >= total):
                return items


def _raise_if_unsuccessful(data):
    """HP VME can return HTTP 200 and still report failure in the body.

    Power actions answer like {"success": true, "results": {"1": {"success": true}}},
    so per-item results are checked as well.
    """
    if not isinstance(data, dict):
        return
    if data.get("success") is False:
        raise HpvmeError(str(data.get("msg") or "HP VME reported that the request failed."))
    results = data.get("results")
    if isinstance(results, dict):
        for result in results.values():
            if isinstance(result, dict) and result.get("success") is False:
                raise HpvmeError(str(result.get("msg") or "HP VME reported that the request failed."))


# --- Reading the inventory --------------------------------------------------


def server_format(server):
    return (server.get("computeServerType") or {}).get("format") or ""


def map_instances_by_server_id(instances):
    """Index instance associations, allowing string IDs in endpoint parameters."""
    return {str(server_id): instance
            for instance in instances
            for server_id in instance.get("servers") or []}


def get_instance_for_server(client, server):
    """Resolve the live instance association without relying on endpoint properties."""
    instance_id = (server.get("instance") or {}).get("id")
    if instance_id is None:
        instances = client.get_all("/api/instances", "instances")
        instance = map_instances_by_server_id(instances).get(str(server.get("id")))
        instance_id = instance.get("id") if instance else None
    return client.get_instance(instance_id) if instance_id is not None else None


def fetch_inventory(client):
    """Return (hosts, vms, instance_by_server_id) from one manager."""
    servers = client.get_all("/api/servers", "servers")
    instances = client.get_all("/api/instances", "instances")

    instance_by_server_id = map_instances_by_server_id(instances)

    hosts = []
    vms = []
    for server in servers:
        if server.get("removedFromInventory"):
            continue
        kind = server_format(server)
        if kind == FORMAT_HOST:
            hosts.append(server)
        elif kind == FORMAT_VM:
            vms.append(server)
    return hosts, vms, instance_by_server_id


def format_mac(mac):
    """Convert a MAC address to Forescout's 12-character form, or "" if invalid."""
    cleaned = re.sub(r"[^0-9A-Fa-f]", "", str(mac or "")).upper()
    return cleaned if len(cleaned) == 12 else ""


def vm_identities(server):
    """Return one {"mac", "ip"} per NIC of a VM. A stopped VM may have only a MAC."""
    identities = []
    for nic in server.get("interfaces") or []:
        mac = format_mac(nic.get("macAddress"))
        ip = nic.get("ipAddress") or None
        if mac or ip:
            identities.append({"mac": mac or None, "ip": ip})
    if not identities and server.get("internalIp"):
        identities.append({"mac": None, "ip": server["internalIp"]})
    return identities


def host_identities(server):
    """Return the host's management identity as a single endpoint.

    Hosts also list a physical NIC with no IP, and vnet* NICs mirroring their VMs.
    Those would create phantom endpoints, so only the NIC holding the management
    IP is used. In the lab that is the bridge (hvmbr0), not the physical NIC.
    """
    management_ip = server.get("internalIp") or server.get("externalIp")
    nics = [nic for nic in (server.get("interfaces") or [])
            if not str(nic.get("name") or "").startswith("vnet") and nic.get("ipAddress")]
    chosen = next((nic for nic in nics if nic.get("ipAddress") == management_ip), None)
    if chosen is None and not management_ip and nics:
        chosen = nics[0]
    if chosen is not None:
        return [{"mac": format_mac(chosen.get("macAddress")) or None, "ip": chosen.get("ipAddress")}]
    return [{"mac": None, "ip": management_ip}] if management_ip else []


def make_endpoints(identities, properties):
    """Create one Forescout endpoint per identity, sharing the same properties."""
    endpoints = []
    for identity in identities:
        endpoint = {"properties": properties}
        if identity.get("mac"):
            endpoint["mac"] = identity["mac"]
        if identity.get("ip"):
            endpoint["ip"] = identity["ip"]
        endpoints.append(endpoint)
    return endpoints


# --- Mapping API records to Forescout properties ----------------------------


def _name_of(record, key="name"):
    return (record or {}).get(key) or ""


def bytes_to_gb(value):
    return int(round((value or 0) / (1024 ** 3)))


def bytes_to_mb(value):
    return int(round((value or 0) / (1024 ** 2)))


def to_epoch(timestamp):
    """Convert an API timestamp like 2026-11-05T05:19:10.432Z to epoch seconds."""
    if not timestamp:
        return None
    for pattern in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            parsed = datetime.strptime(timestamp, pattern)
            return int(parsed.replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            continue
    return None


def format_tags(tags):
    """Turn [{"name": "a", "value": "b"}] into "a=b; c=d"."""
    parts = []
    for tag in tags or []:
        if isinstance(tag, dict) and tag.get("name"):
            value = tag.get("value")
            parts.append(f"{tag['name']}={value}" if value not in (None, "") else str(tag["name"]))
    return "; ".join(parts)


def _operating_system(server):
    name = _name_of(server.get("serverOs"))
    if name:
        return name
    return " ".join(part for part in (server.get("platform"), server.get("platformVersion")) if part)


def vm_properties(server, instance):
    """Build VM properties. instance is None for a discovered VM."""
    instance = instance or {}
    networks = []
    for nic in server.get("interfaces") or []:
        name = _name_of(nic.get("network"))
        if name and name not in networks:
            networks.append(name)
    agent = bool(server.get("agentInstalled"))

    properties = {
        "connect_hpvme_endpoint_type": "VM",
        "connect_hpvme_name": server.get("name") or "",
        "connect_hpvme_power_state": server.get("powerState") or "unknown",
        "connect_hpvme_managed": bool((server.get("computeServerType") or {}).get("managed")),
        "connect_hpvme_is_manager": bool(server.get("appliance")),
        "connect_hpvme_os": _operating_system(server),
        "connect_hpvme_os_type": server.get("osType") or "",
        "connect_hpvme_cloud": _name_of(server.get("zone")),
        "connect_hpvme_group": _name_of(instance.get("group")),
        "connect_hpvme_cluster": _name_of(instance.get("cluster")),
        "connect_hpvme_host": _name_of(server.get("parentServer")),
        "connect_hpvme_plan": _name_of(server.get("plan")),
        "connect_hpvme_cpu_cores": server.get("maxCores") or 0,
        "connect_hpvme_memory_mb": bytes_to_mb(server.get("maxMemory")),
        "connect_hpvme_storage_gb": bytes_to_gb(server.get("maxStorage")),
        "connect_hpvme_networks": ", ".join(networks),
        "connect_hpvme_tags": format_tags(instance.get("tags") or server.get("tags")),
        "connect_hpvme_labels": ", ".join(str(l) for l in (instance.get("labels") or server.get("labels") or [])),
        "connect_hpvme_agent_installed": agent,
        "connect_hpvme_agent_version": (server.get("agentVersion") or "") if agent else "",
        "connect_hpvme_guest_agent_status": server.get("guestAgentStatus") or "",
        "connect_hpvme_locked": bool(instance.get("locked")),
        "connect_hpvme_owner": _name_of(instance.get("owner") or server.get("owner"), "username"),
        "connect_hpvme_environment": instance.get("environment") or "",
        "connect_hpvme_instance_status": instance.get("status") or "",
    }
    if instance.get("id") is not None:
        properties["connect_hpvme_instance_id"] = instance["id"]
    created = to_epoch(server.get("dateCreated"))
    if created is not None:
        properties["connect_hpvme_date_created"] = created
    return properties


def host_properties(server, vm_count):
    """Build hypervisor host properties."""
    stats = server.get("stats") or {}
    vendor = str(server.get("hardwareProductVendor") or "").strip()
    product = str(server.get("hardwareProductName") or "").strip()
    agent = bool(server.get("agentInstalled"))

    return {
        "connect_hpvme_endpoint_type": "Host",
        "connect_hpvme_host_name": server.get("name") or "",
        "connect_hpvme_host_power_state": server.get("powerState") or "unknown",
        "connect_hpvme_host_status": server.get("status") or "",
        "connect_hpvme_host_type": _name_of(server.get("computeServerType")),
        "connect_hpvme_host_os": _operating_system(server),
        "connect_hpvme_host_cluster": _name_of(server.get("serverGroup")),
        "connect_hpvme_host_cloud": _name_of(server.get("zone")),
        "connect_hpvme_host_hardware": " ".join(part for part in (vendor, product) if part),
        "connect_hpvme_host_cpu_model": server.get("hardwareCpuModel") or "",
        "connect_hpvme_host_cpu_cores": server.get("maxCores") or 0,
        "connect_hpvme_host_cpu_sockets": server.get("maxSockets") or 0,
        "connect_hpvme_host_cpu_usage": int(round(stats.get("cpuUsage") or 0)),
        "connect_hpvme_host_memory_gb": bytes_to_gb(server.get("maxMemory")),
        "connect_hpvme_host_memory_used_gb": bytes_to_gb(stats.get("usedMemory")),
        "connect_hpvme_host_storage_gb": bytes_to_gb(server.get("maxStorage")),
        "connect_hpvme_host_storage_used_gb": bytes_to_gb(stats.get("usedStorage")),
        "connect_hpvme_host_vm_count": vm_count,
        "connect_hpvme_host_agent_installed": agent,
        "connect_hpvme_host_agent_version": (server.get("agentVersion") or "") if agent else "",
        "connect_hpvme_host_maintenance_mode": bool(server.get("maintenanceMode")),
    }


# --- Actions ----------------------------------------------------------------


def is_manager_vm(server, manager_url):
    """True if this VM is the HP VME manager itself."""
    if server.get("appliance") or server.get("systemServer"):
        return True
    manager_host = urlparse(normalize_url(manager_url)).hostname
    addresses = {server.get("internalIp"), server.get("externalIp")}
    addresses.update(nic.get("ipAddress") for nic in server.get("interfaces") or [])
    return bool(manager_host) and manager_host in addresses


def connect_for_action(params, verify):
    """Log in to the manager that owns this endpoint."""
    url, username, password = get_routed_manager(params)
    proxies = get_proxies_from_params(params)
    return Client(url, username, password, verify, proxies), url


def resolve_target(client, manager_url, params, disruptive):
    """Check that this endpoint can take an action, using live data.

    Returns (server, instance_id). Raises HpvmeError if the endpoint is a
    hypervisor host, a discovered VM, or (for disruptive actions) the manager.
    """
    server_id = params.get("connect_hpvme_server_id")
    if server_id in (None, ""):
        raise HpvmeError("This endpoint has no HP VME server ID. Wait for the next discovery and try again.")

    server = client.get_server(server_id)
    kind = server_format(server)
    if kind == FORMAT_HOST:
        raise HpvmeError("Refused: this endpoint is a hypervisor host. The app only acts on VMs.")
    if kind != FORMAT_VM:
        raise HpvmeError(f"Refused: unexpected server type '{kind}'. The app only acts on VMs.")
    if disruptive and is_manager_vm(server, manager_url):
        raise HpvmeError("Refused: this VM is the HP VME manager. Powering it off would stop the manager.")

    instance = get_instance_for_server(client, server)
    if instance is None or instance.get("id") is None:
        raise HpvmeError("Refused: this is a discovered VM with no instance record. "
                         "This app version only acts on VMs managed as instances.")
    return server, instance["id"]


POWER_STATES = {"start": "on", "stop": "off", "suspend": "suspended"}


def _instance_members(client, server, instance_id, manager_url, disruptive):
    """Verify instance membership and reject unsafe instance-wide action targets."""
    instance = client.get_instance(instance_id)
    server_ids = sorted({str(server_id) for server_id in instance.get("servers") or []})
    if str(server.get("id")) not in server_ids:
        raise HpvmeError("Refused: the VM's live instance membership could not be verified.")
    members = []
    for server_id in server_ids:
        member = server if server_id == str(server.get("id")) else client.get_server(server_id)
        if server_format(member) != FORMAT_VM:
            raise HpvmeError("Refused: the instance contains a server that is not a VM.")
        if disruptive and is_manager_vm(member, manager_url):
            raise HpvmeError("Refused: the instance contains the HP VME manager.")
        members.append(member)
    return members, server_ids


def _instance_power_state(client, server, instance_id, manager_url, disruptive):
    """Require a restorable, uniform state across the instance-wide action target."""
    members, server_ids = _instance_members(
        client, server, instance_id, manager_url, disruptive)
    states = {member.get("powerState") for member in members}
    if len(states) != 1 or not states.issubset(POWER_STATES.values()):
        raise HpvmeError("Refused: the instance has mixed or unknown power states; safe undo is not possible.")
    return states.pop(), server_ids


def run_instance_action(params, verify, verb, query=None, disruptive=True):
    """Run a simple PUT /api/instances/{id}/{verb} action and return a response dict."""
    try:
        client, manager_url = connect_for_action(params, verify)
        server, instance_id = resolve_target(client, manager_url, params, disruptive)
        cookie = None
        if verb in POWER_STATES:
            before, server_ids = _instance_power_state(
                client, server, instance_id, manager_url, disruptive)
            if verb == "stop" and before == "suspended":
                raise HpvmeError("Refused: powering off a suspended VM loses its saved memory state. "
                                 "Start the VM before stopping it.")
            if verb == "suspend" and before == "off":
                raise HpvmeError("Refused: a powered-off VM cannot be suspended. Start it first.")
            cookie = json.dumps({
                "version": 1, "verb": verb, "before": before, "after": POWER_STATES[verb],
                "manager_url": normalize_url(manager_url), "server_id": str(server["id"]),
                "instance_id": str(instance_id), "server_ids": server_ids,
            })
            if before == POWER_STATES[verb]:
                return {"succeeded": True, "cookie": cookie}
        elif verb == "restart":
            _instance_members(client, server, instance_id, manager_url, disruptive)
        client.request("PUT", f"/api/instances/{instance_id}/{verb}", query=query)
        response = {"succeeded": True}
        if cookie is not None:
            response["cookie"] = cookie
        return response
    except HpvmeError as error:
        return {"succeeded": False, "troubleshooting": str(error)}


def restore_power_state(params, verify, verb):
    """Restore the recorded state only for the same target and expected transition."""
    raw_cookie = params.get("cookie")
    if not isinstance(raw_cookie, str):
        return {"succeeded": False, "troubleshooting": "The stored power undo information is missing."}
    try:
        cookie = json.loads(raw_cookie)
    except ValueError:
        return {"succeeded": False, "troubleshooting": "The stored power undo information could not be read."}
    if (not isinstance(cookie, dict) or cookie.get("version") != 1
            or verb not in POWER_STATES or cookie.get("verb") != verb
            or cookie.get("before") not in ("on", "off", "suspended")
            or cookie.get("after") != POWER_STATES[verb]
            or (verb == "stop" and cookie.get("before") == "suspended")
            or (verb == "suspend" and cookie.get("before") == "off")):
        return {"succeeded": False, "troubleshooting": "The stored power undo information is invalid."}
    try:
        client, manager_url = connect_for_action(params, verify)
        before = cookie["before"]
        server, instance_id = resolve_target(client, manager_url, params, before != "on")
        current, server_ids = _instance_power_state(
            client, server, instance_id, manager_url, before != "on")
        if (cookie.get("manager_url") != normalize_url(manager_url)
                or cookie.get("server_id") != str(server["id"])
                or cookie.get("instance_id") != str(instance_id)
                or cookie.get("server_ids") != server_ids):
            raise HpvmeError("Refused: the stored power undo information belongs to a different target.")
        if before == cookie["after"] or current == before:
            return {"succeeded": True}
        if current != cookie["after"]:
            raise HpvmeError("Refused: the power state changed or the action is still pending. "
                             "Check the VM before retrying undo.")
        restore_verb = next(action for action, state in POWER_STATES.items() if state == before)
        query = {"server": "true"} if restore_verb in ("start", "stop") else None
        client.request("PUT", f"/api/instances/{instance_id}/{restore_verb}", query=query)
        return {"succeeded": True}
    except HpvmeError as error:
        return {"succeeded": False, "troubleshooting": str(error)}


def lock_instance(params, verify):
    """Lock the VM without claiming ownership of the API's ownerless lock."""
    try:
        client, manager_url = connect_for_action(params, verify)
        _, instance_id = resolve_target(client, manager_url, params, False)
        if client.get_instance(instance_id).get("locked"):
            return {"succeeded": True, "cookie": "already_locked"}
        client.request("PUT", f"/api/instances/{instance_id}/lock")
        return {"succeeded": True, "cookie": "manual_unlock_required"}
    except HpvmeError as error:
        return {"succeeded": False, "troubleshooting": str(error)}


def unlock_instance(params, verify):
    """Refuse automatic unlock: the API provides no proof of lock ownership."""
    if params.get("cookie") == "already_locked":
        return {"succeeded": True}
    return {"succeeded": False, "troubleshooting":
            "Automatic unlock is disabled because HP VME does not expose lock ownership. "
            "An operator must unlock the instance in HP VME."}


def create_snapshot(params, verify):
    """Request a snapshot. It runs in the background on the manager."""
    snapshot = {}
    name = str(params.get("connect_hpvme_snapshot_name") or "").strip()
    description = str(params.get("connect_hpvme_snapshot_description") or "").strip()
    if name:  # with no name, the manager generates one
        snapshot["name"] = name
    if description:
        snapshot["description"] = description
    try:
        client, manager_url = connect_for_action(params, verify)
        _, instance_id = resolve_target(client, manager_url, params, False)
        client.request("PUT", f"/api/instances/{instance_id}/snapshot", body={"snapshot": snapshot})
        return {"succeeded": True}
    except HpvmeError as error:
        return {"succeeded": False, "troubleshooting": str(error)}


def _update_tags(client, instance_id, add=None, remove=None):
    instance = {}
    if add:
        instance["addTags"] = add
    if remove:
        instance["removeTags"] = remove
    client.request("PUT", f"/api/instances/{instance_id}", body={"instance": instance})


def change_tag(params, verify):
    """Add or remove one tag. The cookie stores what is needed to reverse the change."""
    operation = str(params.get("connect_hpvme_tag_operation") or "add").strip().lower()
    name = str(params.get("connect_hpvme_tag_name") or "").strip()
    value = str(params.get("connect_hpvme_tag_value") or "").strip() or "true"
    if operation not in ("add", "remove"):
        return {"succeeded": False, "troubleshooting": "Operation must be 'add' or 'remove'."}
    if not name:
        return {"succeeded": False, "troubleshooting": "A tag name is required."}
    try:
        client, manager_url = connect_for_action(params, verify)
        _, instance_id = resolve_target(client, manager_url, params, False)
        current = client.get_instance(instance_id).get("tags") or []
        existing = next((tag for tag in current if tag.get("name") == name), None)
        if operation == "add":
            _update_tags(client, instance_id, add=[{"name": name, "value": value}])
        elif existing is not None:
            _update_tags(client, instance_id, remove=[{"name": name}])
        cookie = {"name": name, "had_tag": existing is not None,
                  "value": existing.get("value") if existing else None}
        return {"succeeded": True, "cookie": json.dumps(cookie)}
    except HpvmeError as error:
        return {"succeeded": False, "troubleshooting": str(error)}


def restore_tag(params, verify):
    """Put a tag back to how it was before the Add or Remove Tag action."""
    try:
        cookie = json.loads(params.get("cookie") or "{}")
    except ValueError:
        return {"succeeded": False, "troubleshooting": "The stored undo information could not be read."}
    name = cookie.get("name")
    if not name:
        return {"succeeded": False, "troubleshooting": "The stored undo information has no tag name."}
    try:
        client, manager_url = connect_for_action(params, verify)
        _, instance_id = resolve_target(client, manager_url, params, False)
        if cookie.get("had_tag"):
            _update_tags(client, instance_id, add=[{"name": name, "value": cookie.get("value")}])
        else:
            _update_tags(client, instance_id, remove=[{"name": name}])
        return {"succeeded": True}
    except HpvmeError as error:
        return {"succeeded": False, "troubleshooting": str(error)}
