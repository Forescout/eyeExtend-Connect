"""Native, bounded LDAPv3/AD client for the eyeExtend Connect sandbox.

No external packages, filesystem access, subprocesses, or background threads.
The caller supplies Forescout's SSLContext. See docs/design.md for boundaries.
"""

import ipaddress
import json
import random
import re
import socket
import ssl
import struct
import time
import uuid


PREFIX = "connect_activedirectory_"
MAX_PACKET = 4 * 1024 * 1024
MAX_VALUES = 20000
START_TLS = "1.3.6.1.4.1.1466.20037"
DOMAIN_SCOPE = "1.2.840.113556.1.4.1339"
ATTRS = ["objectGUID", "objectClass", "sAMAccountName", "dNSHostName",
         "userPrincipalName", "userAccountControl", "accountExpires", "memberOf",
         "objectSid", "primaryGroupID"]


class DirectoryError(Exception):
    pass


class ProtocolError(DirectoryError):
    pass


class TransportError(DirectoryError):
    pass


class MatchError(DirectoryError):
    pass


class NoUserIdentity(MatchError):
    """A logout/local session must replace retained AD identity values."""
    pass


class IndeterminateWrite(DirectoryError):
    pass


class LDAPError(DirectoryError):
    def __init__(self, code, operation):
        self.code = code
        labels = {3: "time limit exceeded", 4: "size limit exceeded",
                  8: "stronger authentication required", 10: "referral refused",
                  12: "required control unavailable", 16: "attribute not present",
                  19: "constraint violation", 20: "value already exists",
                  32: "object not found", 34: "invalid DN", 49: "invalid credentials",
                  50: "insufficient access", 51: "server busy", 52: "server unavailable",
                  53: "server unwilling to perform", 65: "object class violation",
                  122: "assertion failed (object changed)"}
        # Never expose server diagnostics: they may echo credentials or query data.
        # Connect rejects explicit .__init__ calls; Exception renders its args.
        self.args = ("LDAP %s: %s (code %s)" %
                     (operation, labels.get(code, "operation failed"), code),)


def tlv(tag, payload):
    length = len(payload)
    if length > MAX_PACKET:
        raise ProtocolError("LDAP message exceeds size limit")
    if length < 128:
        prefix = bytes([length])
    else:
        encoded = length.to_bytes((length.bit_length() + 7) // 8, "big")
        prefix = bytes([128 | len(encoded)]) + encoded
    return bytes([tag]) + prefix + payload


def integer(number, tag=2):
    if number < 0:
        raise ProtocolError("Negative protocol integer")
    return tlv(tag, number.to_bytes(max(1, (number.bit_length() + 8) // 8), "big"))


def octet(value, tag=4):
    return tlv(tag, value if isinstance(value, bytes) else value.encode("utf-8"))


def sequence(*items):
    return tlv(0x30, b"".join(items))


def elements(data):
    result = []
    offset = 0
    while offset < len(data):
        if offset + 2 > len(data):
            raise ProtocolError("Truncated BER header")
        tag, length = data[offset], data[offset + 1]
        offset += 2
        if tag & 31 == 31:
            raise ProtocolError("Unsupported BER tag")
        if length & 128:
            count = length & 127
            if not 1 <= count <= 4 or offset + count > len(data):
                raise ProtocolError("Invalid BER length")
            length = int.from_bytes(data[offset:offset + count], "big")
            offset += count
        if length > MAX_PACKET or offset + length > len(data):
            raise ProtocolError("Truncated or oversized BER value")
        result.append((tag, data[offset:offset + length]))
        offset += length
        if len(result) > MAX_VALUES:
            raise ProtocolError("Too many BER elements")
    return result


def require(item, tag):
    if item[0] != tag:
        raise ProtocolError("Unexpected LDAP response type")
    return item[1]


def number(item, tag=2):
    value = require(item, tag)
    if not value or len(value) > 8 or value[0] & 128:
        raise ProtocolError("Invalid LDAP integer")
    return int.from_bytes(value, "big")


def text_value(value):
    try:
        return value.decode("utf-8")
    except UnicodeError:
        raise ProtocolError("Invalid UTF-8 from directory") from None


def equal(attribute, value):
    # Encode the assertion value as bytes, never interpolate an LDAP filter string.
    return tlv(0xa3, octet(attribute) + octet(value))


def present(attribute):
    return octet(attribute, 0x87)


def all_of(*filters):
    return tlv(0xa0, b"".join(filters))


def any_of(*filters):
    if not filters:
        raise DirectoryError("No identity supplied")
    return filters[0] if len(filters) == 1 else tlv(0xa1, b"".join(filters))


def remaining(deadline, timeout):
    value = min(timeout, deadline - time.monotonic())
    if value <= 0:
        raise TransportError("Directory operation deadline exceeded")
    return value


def receive_exact(sock, count, deadline, timeout):
    chunks = []
    while count:
        sock.settimeout(remaining(deadline, timeout))
        part = sock.recv(count)
        if not part:
            raise TransportError("Directory connection closed")
        chunks.append(part)
        count -= len(part)
    return b"".join(chunks)


def receive_message(sock, deadline, timeout):
    head = receive_exact(sock, 2, deadline, timeout)
    if head[0] != 0x30:
        raise ProtocolError("Expected LDAP message sequence")
    length = head[1]
    if length & 128:
        count = length & 127
        if not 1 <= count <= 4:
            raise ProtocolError("Invalid LDAP frame length")
        length = int.from_bytes(receive_exact(sock, count, deadline, timeout), "big")
    if not 1 <= length <= MAX_PACKET:
        raise ProtocolError("LDAP frame exceeds size limit")
    return elements(receive_exact(sock, length, deadline, timeout))


def parse_endpoint(value, default_port):
    value = value.strip()
    if not value or re.search(r"[\s/@?#]", value):
        raise DirectoryError("Use a hostname or IP, optionally with a port; no URL")
    host, port = value, default_port
    if value.startswith("["):
        match = re.fullmatch(r"\[([^\]]+)\](?::([0-9]+))?", value)
        if not match:
            raise DirectoryError("Invalid bracketed IPv6 server")
        host = str(ipaddress.IPv6Address(match.group(1)))
        if match.group(2):
            port = int(match.group(2))
    elif value.count(":") == 1:
        host, port_text = value.rsplit(":", 1)
        if not port_text.isdigit():
            raise DirectoryError("Invalid server port")
        port = int(port_text)
    elif ":" in value:
        host = str(ipaddress.IPv6Address(value))
    if not host or not 1 <= port <= 65535:
        raise DirectoryError("Invalid server or port")
    return host.rstrip("."), port


def list_setting(value):
    return [part for part in re.split(r"[,;\s]+", str(value or "")) if part]


def dns_name(name):
    labels = name.rstrip(".").encode("idna").split(b".")
    if any(not label or len(label) > 63 for label in labels):
        raise DirectoryError("Invalid DNS name")
    encoded = b"".join(bytes([len(label)]) + label for label in labels) + b"\x00"
    if len(encoded) > 255:
        raise DirectoryError("DNS name is too long")
    return encoded


def read_dns_name(packet, offset):
    labels, seen, end = [], set(), None
    while True:
        if offset >= len(packet) or offset in seen or len(seen) > 128:
            raise ProtocolError("Invalid DNS name compression")
        seen.add(offset)
        length = packet[offset]
        if length & 0xc0 == 0xc0:
            if offset + 1 >= len(packet):
                raise ProtocolError("Truncated DNS pointer")
            if end is None:
                end = offset + 2
            offset = ((length & 63) << 8) | packet[offset + 1]
            continue
        if length & 0xc0 or offset + length + 1 > len(packet):
            raise ProtocolError("Invalid DNS label")
        offset += 1
        if length == 0:
            return ".".join(labels).lower(), end if end is not None else offset
        try:
            labels.append(packet[offset:offset + length].decode("ascii"))
        except UnicodeError:
            raise ProtocolError("Non-ASCII DNS response") from None
        if sum(len(label) + 1 for label in labels) > 254:
            raise ProtocolError("Oversized DNS name")
        offset += length


def parse_srv(packet, query_id, query_name):
    if len(packet) < 12:
        raise ProtocolError("Truncated DNS reply")
    ident, flags, qcount, answers, authorities, extras = struct.unpack("!6H", packet[:12])
    if ident != query_id or not flags & 0x8000 or flags & 0x7800 or qcount != 1:
        raise ProtocolError("Mismatched DNS reply")
    if flags & 15:
        raise DirectoryError("DNS lookup failed (rcode %s)" % (flags & 15))
    name, offset = read_dns_name(packet, 12)
    if name != query_name.lower().rstrip(".") or packet[offset:offset + 4] != b"\x00!\x00\x01":
        raise ProtocolError("Mismatched DNS question")
    if flags & 0x0200:
        return None
    offset += 4
    records = []
    if answers + authorities + extras > 1024:
        raise ProtocolError("Too many DNS records")
    for index in range(answers + authorities + extras):
        owner, offset = read_dns_name(packet, offset)
        if offset + 10 > len(packet):
            raise ProtocolError("Truncated DNS record")
        kind, record_class, ttl, size = struct.unpack("!HHIH", packet[offset:offset + 10])
        offset += 10
        end = offset + size
        if end > len(packet):
            raise ProtocolError("Truncated DNS data")
        if index < answers and kind == 33 and record_class == 1 and owner == name:
            if size < 7:
                raise ProtocolError("Truncated SRV record")
            priority, weight, port = struct.unpack("!HHH", packet[offset:offset + 6])
            target, target_end = read_dns_name(packet, offset + 6)
            if target_end != end:
                raise ProtocolError("Invalid SRV target length")
            if not target:
                raise DirectoryError("DNS reports AD service unavailable")
            if not port:
                raise ProtocolError("Invalid SRV port")
            records.append((priority, weight, target, port))
        offset = end
    if not records:
        raise DirectoryError("No AD domain controller SRV records found")
    return records


def srv_lookup(domain, resolvers, timeout, deadline):
    query_name = "_ldap._tcp.dc._msdcs." + domain.rstrip(".")
    ident = random.SystemRandom().randrange(65536)
    query = struct.pack("!6H", ident, 0x0100, 1, 0, 0, 0) + dns_name(query_name) + b"\x00!\x00\x01"
    for resolver in resolvers:
        host, port = parse_endpoint(resolver, 53)
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            raise DirectoryError("DNS resolvers must be IP addresses") from None
        sock = None
        try:
            sock = socket.socket(socket.AF_INET6 if address.version == 6 else socket.AF_INET,
                                 socket.SOCK_DGRAM)
            sock.settimeout(remaining(deadline, timeout))
            sock.connect((host, port))
            sock.send(query)
            packet = sock.recv(65535)
            records = parse_srv(packet, ident, query_name)
            if records is None:
                sock.close()
                sock = socket.create_connection((host, port), remaining(deadline, timeout))
                sock.sendall(struct.pack("!H", len(query)) + query)
                size = struct.unpack("!H", receive_exact(sock, 2, deadline, timeout))[0]
                records = parse_srv(receive_exact(sock, size, deadline, timeout), ident, query_name)
                if records is None:
                    raise ProtocolError("Truncated DNS TCP reply")
            return order_srv(records)
        except (OSError, DirectoryError):
            # A second configured resolver can recover from timeouts/SERVFAIL/NXDOMAIN.
            continue
        finally:
            if sock is not None:
                sock.close()
    raise DirectoryError("AD SRV discovery failed on all configured DNS resolvers")


def order_srv(records):
    ordered = []
    rng = random.SystemRandom()
    for priority in sorted(set(row[0] for row in records)):
        pool = [row for row in records if row[0] == priority]
        while pool:
            rng.shuffle(pool)
            pool.sort(key=lambda row: row[1] != 0)
            choice = rng.randint(0, sum(row[1] for row in pool))
            running = 0
            for index, row in enumerate(pool):
                running += row[1]
                if running >= choice:
                    ordered.append((row[2], row[3]))
                    pool.pop(index)
                    break
    return ordered


def verify_peer_name(certificate, hostname):
    """Strict SAN identity matching when the supplied context checks only trust.

    Require SANs, match IP SANs as addresses, and permit only a whole leftmost
    DNS wildcard. Works on Python 3.8 as well as versions without match_hostname.
    """
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    host = hostname.rstrip(".").encode("idna").decode("ascii").lower()
    for kind, value in certificate.get("subjectAltName", ()):
        if address is not None and kind == "IP Address":
            try:
                if ipaddress.ip_address(value) == address:
                    return
            except ValueError:
                continue
        elif address is None and kind == "DNS":
            pattern = value.rstrip(".").lower()
            if "*" not in pattern and pattern == host:
                return
            labels = pattern.split(".")
            host_labels = host.split(".")
            if (len(labels) >= 3 and labels[0] == "*" and pattern.count("*") == 1
                    and len(host_labels) == len(labels) and labels[1:] == host_labels[1:]):
                return
    raise ssl.CertificateError("Certificate SAN does not match the AD server identity")


class Client:
    def __init__(self, server, config, tls_context, deadline):
        self.server = server
        self.timeout = config["timeout"]
        self.deadline = deadline
        self.sock = None
        self.message_id = 0
        self.write_attempted = False
        self.write_confirmed = False
        try:
            self.sock = socket.create_connection(server, remaining(deadline, self.timeout))
            if config["transport"] == "ldaps":
                self.start_tls(tls_context)
            elif config["transport"] == "starttls":
                self.send(tlv(0x77, octet(START_TLS, 0x80)))
                self.result(self.read(0x78), "StartTLS")
                self.start_tls(tls_context)
            self.send(tlv(0x60, integer(3) + octet(config["bind_user"]) +
                          octet(config["password"], 0x80)))
            self.result(self.read(0x61), "bind")
        except Exception:
            self.close()
            raise

    def start_tls(self, context):
        if context is None:
            raise DirectoryError("TLS requires the ssl_context supplied by Forescout")
        self.sock.settimeout(remaining(self.deadline, self.timeout))
        self.sock = context.wrap_socket(self.sock, server_hostname=self.server[0])
        # Certificate validation remains controlled by the supplied context.
        # Only validating contexts need the fallback SAN identity check.
        if context.verify_mode != ssl.CERT_NONE and not context.check_hostname:
            verify_peer_name(self.sock.getpeercert(), self.server[0])

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def send(self, operation, controls=b""):
        self.message_id += 1
        self.sock.settimeout(remaining(self.deadline, self.timeout))
        self.sock.sendall(sequence(integer(self.message_id), operation, controls))

    def read(self, expected=None):
        message = receive_message(self.sock, self.deadline, self.timeout)
        if len(message) < 2 or number(message[0]) != self.message_id:
            raise ProtocolError("Unexpected LDAP message ID (including unsolicited disconnect)")
        if expected is not None:
            return require(message[1], expected)
        return message[1]

    def result(self, payload, operation, accepted=(0,)):
        fields = elements(payload)
        if len(fields) < 3:
            raise ProtocolError("Truncated LDAP result")
        code = number(fields[0], 0x0a)
        require(fields[1], 4)
        require(fields[2], 4)
        if code not in accepted:
            raise LDAPError(code, operation)
        return code

    def search(self, base, search_filter, attributes, scope=2, limit=2):
        operation = (octet(base) + integer(scope, 0x0a) + integer(0, 0x0a) +
                     integer(limit) + integer(max(1, int(remaining(self.deadline, self.timeout)))) +
                     tlv(1, b"\x00") + search_filter + sequence(*(octet(a) for a in attributes)))
        # Domain-root subtree searches otherwise return continuation references
        # for DNS/configuration partitions or child domains, even with a match.
        # MS-ADTS domain scope confines the search to this naming context. The
        # control is critical and has no controlValue; never retry without it.
        controls = tlv(0xa0, sequence(octet(DOMAIN_SCOPE), tlv(1, b"\xff"))) if scope == 2 else b""
        self.send(tlv(0x63, operation), controls)
        rows = []
        while True:
            kind, payload = self.read()
            if kind == 0x65:
                self.result(payload, "search")
                return rows
            if kind == 0x73:
                raise LDAPError(10, "search")
            if kind != 0x64:
                raise ProtocolError("Unexpected LDAP search response")
            fields = elements(payload)
            if len(fields) != 2:
                raise ProtocolError("Malformed LDAP entry")
            dn = text_value(require(fields[0], 4))
            attrs = {}
            for item in elements(require(fields[1], 0x30)):
                parts = elements(require(item, 0x30))
                if len(parts) != 2:
                    raise ProtocolError("Malformed LDAP attribute")
                name = text_value(require(parts[0], 4)).lower()
                if name in attrs:
                    raise ProtocolError("Duplicate LDAP attribute")
                attrs[name] = [require(v, 4) for v in elements(require(parts[1], 0x31))]
            rows.append({"dn": dn, "attrs": attrs})
            if len(rows) > limit:
                raise MatchError("Directory returned too many matching objects")

    def compare(self, dn, attribute, value):
        self.send(tlv(0x6e, octet(dn) + sequence(octet(attribute), octet(value))))
        # LDAP can return noSuchAttribute for a group with no member values.
        return self.result(self.read(0x6f), "compare", (5, 6, 16)) == 6

    def modify_member(self, group, member, add):
        change = sequence(integer(0 if add else 1, 0x0a),
                          sequence(octet("member"), tlv(0x31, octet(member))))
        operation = tlv(0x66, octet(group) + sequence(change))
        self.write_attempted = True  # Before sendall: a partial send may reach the DC.
        self.send(operation)
        code = self.result(self.read(0x67), "modify", (0, 16, 20))
        self.write_confirmed = True
        return code


def setting(params, name, default=""):
    return params.get(PREFIX + name, default)


def configuration(params):
    config = {key: str(setting(params, key)).strip() for key in
              ("domain", "netbios_domain", "servers", "dns_servers", "bind_user",
               "computer_base", "user_base")}
    config["password"] = str(setting(params, "password"))
    config["transport"] = str(setting(params, "transport", "ldaps"))
    config["discovery"] = str(setting(params, "discovery", "servers"))
    for name, default, low, high in [("timeout", 5, 1, 30), ("total_timeout", 25, 2, 120),
                                    ("port", 0, 0, 65535)]:
        try:
            config[name] = int(setting(params, name, default))
        except (TypeError, ValueError):
            raise DirectoryError("Invalid numeric setting: " + name) from None
        if not low <= config[name] <= high:
            raise DirectoryError("Setting out of range: " + name)
    if config["transport"] not in ("ldaps", "starttls", "ldap"):
        raise DirectoryError("Select LDAPS, StartTLS, or plaintext LDAP")
    if config["discovery"] not in ("servers", "dns"):
        raise DirectoryError("Select explicit servers or DNS discovery")
    if not config["bind_user"] or not config["password"]:
        raise DirectoryError("Non-empty bind identity and password are required")
    if not config["domain"] or not re.fullmatch(r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", config["domain"]):
        raise DirectoryError("An AD DNS domain is required, for example example.test")
    config["domain"] = config["domain"].lower()
    if config["discovery"] == "servers" and not list_setting(config["servers"]):
        raise DirectoryError("Configure at least one AD server")
    if config["discovery"] == "dns" and not list_setting(config["dns_servers"]):
        raise DirectoryError("Configure at least one DNS resolver IP for SRV discovery")
    if len(list_setting(config["servers"])) > 16 or len(list_setting(config["dns_servers"])) > 8:
        raise DirectoryError("Limit server lists to 16 AD servers and 8 DNS resolvers")
    return config


def candidates(config, deadline):
    default_port = config["port"] or (636 if config["transport"] == "ldaps" else 389)
    if config["discovery"] == "servers":
        servers = [parse_endpoint(value, default_port) for value in list_setting(config["servers"])]
    else:
        records = srv_lookup(config["domain"], list_setting(config["dns_servers"]),
                             config["timeout"], deadline)
        # AD advertises LDAP/389, not a standard LDAPS SRV service.
        servers = [(host, default_port if config["port"] or config["transport"] == "ldaps" else port)
                   for host, port in records]
    result = []
    for server in servers:
        if server not in result:
            result.append(server)
    return result[:16]


def scalar(entry, attribute, required=True):
    values = entry["attrs"].get(attribute.lower(), [])
    if not values and not required:
        return None
    if len(values) != 1:
        raise DirectoryError("Missing or multi-valued required attribute: " + attribute)
    return values[0]


def split_dn(dn):
    # Preserve escapes; the server performs authoritative DN parsing/equality.
    if not isinstance(dn, str) or not dn or "\x00" in dn or len(dn) > 8192:
        raise DirectoryError("A full distinguished name is required")
    parts = []
    start, escaped = 0, False
    for index, char in enumerate(dn):
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == ",":
            parts.append(dn[start:index].strip())
            start = index + 1
    parts.append(dn[start:].strip())
    if escaped or any(not re.match(r"(?:[A-Za-z][A-Za-z0-9-]*|[0-9]+(?:\.[0-9]+)+)=.+", part)
                      for part in parts):
        raise DirectoryError("A full distinguished name is required")
    return parts


def in_domain(dn, base):
    parts, suffix = split_dn(dn), split_dn(base)
    return len(parts) >= len(suffix) and [p.casefold() for p in parts[-len(suffix):]] == [p.casefold() for p in suffix]


def domain_base(client, config):
    roots = client.search("", present("objectClass"), ["defaultNamingContext"], scope=0, limit=1)
    if len(roots) != 1:
        raise DirectoryError("AD RootDSE did not return a naming context")
    base = text_value(scalar(roots[0], "defaultNamingContext"))
    expected = ",".join("DC=" + label for label in config["domain"].split("."))
    if not in_domain(base, expected) or len(split_dn(base)) != len(split_dn(expected)):
        raise DirectoryError("Server belongs to a different AD DNS domain")
    return base


def input_values(params, tag):
    values = params.get(tag, [])
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, (list, tuple)):
        raise MatchError("Unexpected Forescout property format: " + tag)
    values = [value.strip() for value in values if isinstance(value, str) and value.strip()]
    if len(values) > 32 or any(len(value) > 1024 for value in values):
        raise MatchError("Too many or oversized identity values")
    return list(dict.fromkeys(values))


def check_domain(value, config, subject="Identity"):
    allowed = [config["domain"].casefold()]
    if config["netbios_domain"]:
        allowed.append(config["netbios_domain"].casefold())
    if value and value.casefold() not in allowed:
        netbios = "; AD NetBIOS domain %r" % config["netbios_domain"] if config["netbios_domain"] else "; AD NetBIOS domain is not configured"
        raise MatchError("%s domain %r does not match connection AD domain %r%s" %
                         (subject, value, config["domain"], netbios))


def windows_users(value):
    """Accept Connect JSON and the native composite's Map.toString form."""
    if value is None or value == "" or value == []:
        return []
    if isinstance(value, str):
        if len(value) > 32768:
            raise MatchError("Oversized Windows Active Users property")
        try:
            value = json.loads(value)
        except (ValueError, RecursionError):
            # Native dependencies are not necessarily registered in Connect's
            # type map. Their getString() values can be comma-joined Java maps.
            text = value.strip()
            if text.startswith("[") and text.endswith("]"):
                text = text[1:-1].strip()
            rows = re.findall(r"\{[^{}]*\}", text)
            if not rows or re.sub(r"\s+", "", text) != re.sub(r"\s+", "", ",".join(rows)):
                raise MatchError("Invalid Windows Active Users composite") from None
            value = []
            for row in rows:
                fields = {}
                for pair in row[1:-1].split(","):
                    key, separator, item = pair.strip().partition("=")
                    if not separator or key in fields or key not in ("domain_name", "user_name"):
                        raise MatchError("Invalid Windows Active Users composite")
                    fields[key] = item.strip()
                value.append(fields)
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, (list, tuple)) or len(value) > 32:
        raise MatchError("Invalid Windows Active Users composite list")
    users = []
    for row in value:
        if not isinstance(row, dict):
            raise MatchError("Invalid Windows Active Users composite row")
        domain, user = row.get("domain_name"), row.get("user_name")
        if (not isinstance(domain, str) or not isinstance(user, str)
                or not domain.strip() or not user.strip()
                or len(domain) > 1024 or len(user) > 1024
                or any(c in domain + user for c in ("\\", "\x00", ",", "{", "}"))):
            raise MatchError("Invalid Windows Active Users domain or username")
        if domain.strip().casefold() == "local":
            raise NoUserIdentity("Windows Active Users identifies a local user; not attempting the AD lookup")
        users.append(domain.strip() + "\\" + user.strip())
    return users


def user_identities(params):
    """All current observations; never pick the first of conflicting users."""
    users = []
    for tag in ("user", "linux_logged_users", "mac_logged_users"):
        raw = params.get(tag)
        if raw is None or raw == "" or raw == []:
            continue
        if not isinstance(raw, (str, list, tuple)) or (
                isinstance(raw, (list, tuple)) and any(not isinstance(item, str) for item in raw)):
            raise MatchError("Unexpected Forescout property format: " + tag)
        # Connect joins multiple native scalar values with commas.
        values = input_values({tag: raw}, tag)
        for value in values:
            for user in value.split(","):
                user = user.strip()
                if not user or (tag != "user" and user.casefold() == "unknown"):
                    continue
                if re.search(r"(?:^|\s)\(local\)$", user, re.IGNORECASE):
                    label = "Forescout user property" if tag == "user" else tag
                    raise NoUserIdentity(label + " identifies a local user; not attempting the AD lookup")
                users.append(user)
    users.extend(windows_users(params.get("va_comp_users_logged_in")))
    if len(users) > 32:
        raise MatchError("Too many logged-in user identities")
    return list({user.casefold(): user for user in users}.values())


def username_identity(params, config):
    """Coalesce a bare SAM name with its matching, domain-qualified form."""
    candidates = {}
    for value in user_identities(params):
        if "\\" in value:
            domain, name = value.split("\\", 1)
            if not domain or not name or "\\" in name or "@" in name:
                raise MatchError("Invalid domain-qualified user")
            check_domain(domain, config, "User")
            key = ("sam", name.casefold())
        elif "@" in value:
            name = value
            if value.count("@") != 1 or not all(value.split("@")):
                raise MatchError("Invalid user principal name")
            key = ("upn", value.casefold())
        else:
            name = value
            key = ("sam", name.casefold())
        if name.endswith("$"):
            raise MatchError("A machine/service account is not a logged-in user")
        if key not in candidates or "\\" in value:
            candidates[key] = value
    if not candidates:
        raise NoUserIdentity("No logged-in AD user identity is available")
    if len(candidates) != 1:
        raise MatchError("One logged-in user identity is required; multiple sessions or conflicting username sources are ambiguous")
    return next(iter(candidates.values()))


def check_user_observation(params, record):
    """Reject an old GUID when any available username no longer agrees."""
    users = user_identities(params)
    aliases = {record.get(key).casefold() for key in ("identity", "upn", "sam")
               if isinstance(record.get(key), str) and record.get(key)}
    domain, sam = record.get("domain"), record.get("sam")
    if isinstance(domain, str) and domain and isinstance(sam, str) and sam:
        aliases.add((domain + "\\" + sam).casefold())
    # An explicitly empty Windows list is a logout observation, unlike an
    # absent/unresolved property. Do not reuse the previous session's GUID.
    windows = params.get("va_comp_users_logged_in")
    if windows is not None and not windows_users(windows):
        raise NoUserIdentity("Windows Active Users is empty; refresh the GUID script result")
    if any(user.casefold() not in aliases for user in users):
        raise MatchError("Logged-in user differs from the GUID observation; refresh the script result")


def collector_result(params, property_tag):
    """Read the confirmed collector result without contacting the directory."""
    if not property_tag:
        return None
    raw = params.get(property_tag)
    if raw is None or raw == "" or raw == []:
        return None
    if isinstance(raw, (list, tuple)):
        if len(raw) != 1:
            raise MatchError("Multiple GUID collector results are ambiguous")
        raw = raw[0]
    if not isinstance(raw, str) or not raw.strip() or len(raw) > 8192:
        raise MatchError("Invalid GUID collector property format")
    try:
        result = json.loads(raw)
    except (ValueError, RecursionError):
        raise MatchError("GUID collector did not return valid JSON") from None
    validate_collector_metadata(result)
    return result


def validate_collector_metadata(result):
    # Accept cached observations from the previous collector during rollout.
    if not isinstance(result, dict) or result.get("schema") not in ("connectad-guid-v1", "nativead-guid-v1"):
        raise MatchError("Unsupported GUID collector schema")
    observed = result.get("collected_at")
    if type(observed) is not int or observed < 0 or observed > time.time() + 60:
        raise MatchError("GUID collector result has an invalid timestamp; refresh the script result")


def collector_account(result, kind):
    if result is None:
        return None
    record = result.get(kind)
    if not isinstance(record, dict) or record.get("status") not in (
            "ok", "error", "not_domain_joined", "no_active_user", "multiple_active_users",
            "not_ad_user", "session_changed"):
        raise MatchError("Invalid GUID collector account status")
    return record


def empty_composite(record, defaults):
    """Accept a clear or its typed default fields supplied by Forescout.

    The core stores {}, but dependency reads can expand all registered fields
    to empty strings, zero dates and false booleans. Any populated, unexpected
    or incorrectly typed field must still pass the normal evidence checks.
    """
    if not isinstance(record, dict) or (record and record.keys() != defaults.keys()):
        return False
    return all(name in defaults and type(value) is type(defaults[name])
               and value == defaults[name] for name, value in record.items())


def collector_record(params, kind, property_tag):
    if property_tag == PREFIX + "managed_" + kind + "_guid_script_details":
        # Connect serializes a scalar composite dependency as a JSON object.
        # Only the declared input is read; raw evidence and old Object/Groups
        # output must never bypass the requested dependency chain.
        record = params.get(property_tag)
        if record is None or record == "" or record == []:
            return None
        if isinstance(record, str):
            if len(record) > 8192:
                raise MatchError("Invalid managed GUID property format")
            try:
                record = json.loads(record)
            except (ValueError, RecursionError):
                raise MatchError("Managed GUID property did not return valid JSON") from None
        if kind == "user" and empty_composite(record, {
                "schema": "", "status": "", "collected_at": 0, "guid": "",
                "domain": "", "sam": "", "upn": "", "identity": ""}):
            # A successful empty composite replaces the previous user evidence.
            return None
        validate_collector_metadata(record)
        collector_account({kind: record}, kind)
        for field in ("guid", "domain", "sam", "upn", "identity"):
            if field in record and not isinstance(record[field], str):
                raise MatchError("Invalid GUID collector field: " + field)
        return record
    return collector_account(collector_result(params, property_tag), kind)


def record_guid(record):
    value = record.get("guid")
    if not isinstance(value, str) or not re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", value):
        raise MatchError("GUID collector returned an invalid objectGUID")
    guid = uuid.UUID(value)
    if not guid.int:
        raise MatchError("GUID collector returned an empty objectGUID")
    return guid


def run_collector(params, kind, guid_property):
    """Expose parsed GUID evidence even when AD is unreachable or unconfigured."""
    try:
        result = collector_result(params, guid_property)
        record = collector_account(result, kind)
        if record is None or (kind == "computer" and record["status"] == "no_active_user"):
            if kind == "user":
                # Omission marks resolution unknown and retains the last user.
                # Replace the composite with no fields: no GUID, status or null.
                return {"properties": {PREFIX + "managed_user_guid_script_details": {}}}
            return {"properties": {}}
        value = {"status": record["status"], "schema": result["schema"],
                 "collected_at": result["collected_at"]}
        fields = ("guid", "domain", "sam")
        if kind == "user":
            fields += ("upn", "identity")
        if kind == "user" and record["status"] == "no_active_user":
            if any(record.get(name) not in (None, "") for name in fields):
                raise MatchError("GUID collector reports no active user but contains user identity data")
            # A completed logout observation has useful status/time/schema.
            # Replace every old identity field and retain the original time so
            # subsequent observations can generate dependency change events.
            return {"properties": {PREFIX + "managed_user_guid_script_details": value}}
        for name in fields:
            item = record.get(name)
            if item is not None and not isinstance(item, str):
                raise MatchError("Invalid GUID collector field: " + name)
            if name == "guid" and (item or record["status"] == "ok"):
                item = str(record_guid(record))
            # One observation describes one object. The composite replaces its
            # whole row; omit unavailable scalar fields without null values.
            if item:
                value[name] = item
        return {"properties": {PREFIX + "managed_" + kind + "_guid_script_details": value}}
    except MatchError as error:
        return {"error": str(error)}


def collected_guid(params, kind, config, property_tag, allow_computer_fallback=True, fallback_notes=None):
    """Use the declared raw or managed collector evidence as identity.

    There is no age cutoff. Computer reads may use names when the collected GUID
    is missing or invalid. A no-active-user observation without a GUID may use one
    native user identity. Local-user markers and other negative evidence block.
    """
    users = user_identities(params) if kind == "user" else []
    record = collector_record(params, kind, property_tag)
    if record is None:
        return None
    if kind == "computer" and record["status"] == "not_domain_joined":
        raise MatchError("Computer is not AD joined; not attempting the lookup")
    if kind == "user" and record["status"] == "not_ad_user":
        raise NoUserIdentity("GUID collector identifies a non-AD user; not attempting the AD lookup")
    if record["status"] != "ok":
        if (kind == "user" and record["status"] == "no_active_user"
                and record.get("guid") in (None, "")):
            # WTS may see no active session while Forescout has a user value.
            # Use that value through the normal scoped username search.
            if users:
                return None
            raise NoUserIdentity("No logged-in AD user identity is available")
        if not (kind == "computer" and allow_computer_fallback and record["status"] == "error"):
            raise MatchError("GUID collector did not identify a unique AD %s; refresh and inspect its status" % kind)
    try:
        guid = record_guid(record)
    except MatchError as error:
        # Only an unusable scalar GUID permits read-only computer fallback.
        # Malformed containers, user evidence, and forward writes remain strict.
        if not (kind == "computer" and allow_computer_fallback
                and (record.get("guid") is None or isinstance(record["guid"], str))):
            raise
        domain = record.get("domain")
        if domain is not None and not isinstance(domain, str):
            raise MatchError("Invalid GUID collector field: domain")
        if domain:
            check_domain(domain, config, "Collected computer")
        if fallback_notes is not None:
            fallback_notes.append(str(error) + "; tried computer name matching")
        return None
    if record["status"] != "ok":
        raise MatchError("GUID collector did not identify a unique AD %s; refresh and inspect its status" % kind)
    domain = record.get("domain")
    if not isinstance(domain, str) or domain.casefold() != config["domain"].casefold():
        raise MatchError("Collected GUID belongs to a different AD domain")
    if kind == "user":
        # UUID remains the LDAP lookup key. This is a freshness guard against a
        # cached previous user's GUID when Forescout has already seen a logon change.
        check_user_observation(params, record)
    # AD's objectGUID is a 16-byte value in Windows little-endian GUID layout.
    return guid.bytes_le


def computer_name_identity(params, config):
    """Check Windows domain evidence, then search all exact observed names."""
    for domain in input_values(params, "nbtdomain"):
        check_domain(domain, config, "Computer")
    candidates, descriptions, described_dns = [], [], set()
    for tag, label, confidence, method in (
            ("nbthost", "NetBIOS hostname", "High", "NetBIOS hostname"),
            ("dhcp_hostname_v2", "DHCP hostname", "Medium", "DHCP hostname"),
            ("hostname", "DNS name", "Low", "DNS name"),
            ("hostnames_list", "DNS names", "Low", "DNS name")):
        names = input_values(params, tag)
        display_names = names
        if method == "DNS name":
            display_names = []
            for name in names:
                key = name.rstrip(".").casefold()
                if key not in described_dns:
                    display_names.append(name)
                    described_dns.add(key)
        if display_names:
            display = ", ".join(repr(name)[:160] for name in display_names[:4])
            descriptions.append(label + "=" + display + (", ..." if len(display_names) > 4 else ""))
        for name in names:
            if "\\" in name:
                domain, name = name.split("\\", 1)
                if not domain or not name or "\\" in name:
                    raise MatchError("Invalid domain-qualified computer " + label.lower())
                check_domain(domain, config, "Computer")
            name = name.rstrip(".")
            if not name or not name.rstrip("$"):
                raise MatchError("Invalid computer " + label.lower())
            # Search observed names first. DNS-derived short names are a separate
            # second pass, only after this search returns no objects.
            attribute, value = (("dNSHostName", name) if "." in name
                                else ("sAMAccountName", name.rstrip("$") + "$"))
            candidates.append((attribute, value, confidence, method))
    if not candidates:
        raise MatchError("Computer lookup requires a NetBIOS hostname, DHCP hostname, or DNS name")
    return computer_name_filter(candidates), "; ".join(descriptions), candidates


def computer_name_filter(candidates):
    filters = dict.fromkeys(equal(attribute, value) for attribute, value, unused, unused_method in candidates)
    return all_of(equal("objectCategory", "computer"), any_of(*filters))


def computer_dns_fallback(candidates, config):
    """Derive computer accounts only in this connection's DNS namespace.

    Connect supplies one domain connection to each invocation. An exact suffix
    uses that domain; a child suffix may use this configured parent. A sibling
    domain or a mere substring match never authorizes an account-name search.
    """
    fallback, notes, seen_dns = [], [], set()
    domain = config["domain"].casefold()
    for attribute, value, unused, method in candidates:
        if attribute != "dNSHostName" or method != "DNS name":
            continue
        key = value.casefold()
        if key in seen_dns:
            continue
        seen_dns.add(key)
        if len(value) > 253 or not re.fullmatch(r"[A-Za-z0-9_-]{1,63}(?:\.[A-Za-z0-9_-]{1,63})+", value):
            notes.append("invalid DNS name %r" % value[:160])
            continue
        hostname, suffix = value.split(".", 1)
        if suffix.casefold() == domain or suffix.casefold().endswith("." + domain):
            account = hostname + "$"
            fallback.append(("sAMAccountName", account, "Low", "DNS-derived account name"))
            reason = "exact domain match" if suffix.casefold() == domain else "parent-domain fallback"
            notes.append("searched sAMAccountName=%r in AD domain %r (%s for DNS suffix %r)" %
                         (account, domain, reason, suffix))
        else:
            notes.append("DNS suffix %r does not match connection AD domain %r or a child of it" % (suffix, domain))
    # Keep errors bounded even if Forescout supplies many aliases.
    detail = "; ".join(notes[:4]) + ("; ..." if len(notes) > 4 else "")
    return fallback, detail


def computer_match_details(entry, candidates):
    # Candidates are ordered by strength. Check the returned attributes rather
    # than assigning High just because a nonmatching NetBIOS name was supplied.
    for attribute, value, confidence, method in candidates:
        values = entry["attrs"].get(attribute.lower(), [])
        if any(text_value(actual).casefold() == value.casefold() for actual in values):
            return confidence, method
    raise ProtocolError("Directory object does not match the requested computer names")


def identity_filter(params, kind, config, guid_property="", allow_computer_fallback=True):
    guid = collected_guid(params, kind, config, guid_property, allow_computer_fallback)
    if guid is not None:
        match = equal("objectGUID", guid)
        if kind == "computer":
            return all_of(equal("objectCategory", "computer"), match)
        return all_of(equal("objectCategory", "person"), equal("objectClass", "user"), match)
    if kind == "computer":
        return computer_name_identity(params, config)[0]
    user = username_identity(params, config)
    if "\\" in user:
        domain, user = user.split("\\", 1)
        if not domain or not user or "\\" in user:
            raise MatchError("Invalid domain-qualified user")
        check_domain(domain, config)
        match = equal("sAMAccountName", user)
    elif "@" in user:
        match = equal("userPrincipalName", user)
    else:
        # The configured domain scopes an unqualified account name; workstation
        # nbtdomain is not evidence of the logged-in user's domain.
        match = equal("sAMAccountName", user)
    if user.endswith("$"):
        raise MatchError("A machine/service account is not a logged-in user")
    return all_of(equal("objectCategory", "person"), equal("objectClass", "user"), match)


def resolve_entry(client, params, kind, config, base, guid_property="", recorded_guid=None, allow_computer_fallback=True):
    search_base = config[kind + "_base"] or base
    if not in_domain(search_base, base):
        raise DirectoryError("Search base must be inside the configured domain")
    fallback_notes = []
    requested_guid = recorded_guid if recorded_guid is not None else collected_guid(
        params, kind, config, guid_property, allow_computer_fallback, fallback_notes)
    if kind == "computer" and requested_guid is None:
        search_filter, description, candidates = computer_name_identity(params, config)
    elif recorded_guid is None:
        search_filter = identity_filter(params, kind, config, guid_property, allow_computer_fallback)
    else:
        account_class = equal("objectCategory", "computer") if kind == "computer" else all_of(
            equal("objectCategory", "person"), equal("objectClass", "user"))
        search_filter = all_of(account_class, equal("objectGUID", recorded_guid))
    rows = client.search(search_base, search_filter, ATTRS, limit=2)
    if (not rows and kind == "computer" and requested_guid is not None
            and recorded_guid is None and allow_computer_fallback):
        fallback_notes.append("objectGUID=%s returned no matching AD computer; tried computer name matching" %
                              str(uuid.UUID(bytes_le=requested_guid)))
        try:
            search_filter, description, candidates = computer_name_identity(params, config)
        except MatchError as error:
            raise MatchError("; ".join(fallback_notes + [str(error)])) from None
        requested_guid = None
        rows = client.search(search_base, search_filter, ATTRS, limit=2)
    if not rows and kind == "computer" and requested_guid is None:
        fallback, detail = computer_dns_fallback(candidates, config)
        if detail:
            description += "; DNS account fallback: " + detail
        if fallback:
            rows = client.search(search_base, computer_name_filter(fallback), ATTRS, limit=2)
            candidates = fallback
    if len(rows) != 1:
        message = "No matching AD %s" % kind if not rows else "Multiple matching AD %s objects" % kind
        if kind == "computer":
            if requested_guid is not None:
                description = "objectGUID=" + str(uuid.UUID(bytes_le=requested_guid))
            if fallback_notes:
                description = "; ".join(fallback_notes + [description])
            message += " in domain %r (search base %r) using %s" % (config["domain"], search_base, description)
        raise MatchError(message)
    entry = rows[0]
    if not in_domain(entry["dn"], search_base):
        raise ProtocolError("Directory returned an object outside the search base")
    guid = scalar(entry, "objectGUID")
    if len(guid) != 16:
        raise ProtocolError("Invalid AD objectGUID")
    if requested_guid is not None and guid != requested_guid:
        raise ProtocolError("Directory returned a different objectGUID")
    if requested_guid is not None:
        confidence, method = "Exact", "GUID"
    elif kind == "computer":
        confidence, method = computer_match_details(entry, candidates)
    else:
        user = username_identity(params, config)
        if "\\" in user:
            confidence, method = "High", "Domain-qualified username"
        elif "@" in user:
            confidence, method = "High", "User principal name"
        else:
            confidence, method = "Medium", "Unqualified username"
    entry["match_confidence"], entry["match_method"] = confidence, method
    return entry


def direct_groups(client, entry):
    attrs = entry["attrs"]
    has_range = any(name.startswith("memberof;range=") for name in attrs)
    if attrs.get("memberof") and has_range:
        raise ProtocolError("Conflicting membership attribute encodings")
    if "memberof" in attrs and not has_range:
        return sorted(set(text_value(value) for value in attrs["memberof"]), key=str.casefold)
    # AD returns memberOf;range=0-1499 on objects with many memberships.
    values, expected, current = [], 0, entry
    for unused in range(100):
        ranged = [(name, val) for name, val in current["attrs"].items() if name.startswith("memberof;range=")]
        if not ranged and expected == 0:
            return []
        if len(ranged) != 1:
            raise ProtocolError("Missing or ambiguous membership range")
        match = re.fullmatch(r"memberof;range=([0-9]+)-([0-9]+|\*)", ranged[0][0])
        if not match or int(match.group(1)) != expected:
            raise ProtocolError("Unexpected membership range")
        values.extend(text_value(value) for value in ranged[0][1])
        if len(values) > MAX_VALUES:
            raise DirectoryError("Membership list exceeds configured client limit")
        if match.group(2) == "*":
            return sorted(set(values), key=str.casefold)
        end = int(match.group(2))
        if end < expected or len(ranged[0][1]) != end - expected + 1:
            raise ProtocolError("Incomplete membership range")
        expected = end + 1
        rows = client.search(entry["dn"], equal("objectGUID", scalar(entry, "objectGUID")),
                             ["memberOf;range=%s-*" % expected], scope=0, limit=1)
        if len(rows) != 1:
            raise DirectoryError("Account changed while reading memberships")
        current = rows[0]
    raise DirectoryError("Too many membership ranges")


def primary_group_sid(entry):
    # MS-ADTS: replace only the account SID's final RID, preserving its domain.
    # LDAP carries objectSid as binary; subauthorities are little-endian DWORDs.
    sid = scalar(entry, "objectSid")
    if (len(sid) < 12 or sid[0] != 1 or not 1 <= sid[1] <= 15 or
            len(sid) != 8 + 4 * sid[1]):
        raise DirectoryError("Invalid AD objectSid; cannot resolve the primary group")
    try:
        rid = int(scalar(entry, "primaryGroupID"))
    except ValueError:
        raise DirectoryError("Invalid AD primaryGroupID") from None
    if not 0 < rid <= 4294967295:
        raise DirectoryError("AD primaryGroupID is out of range")
    return sid[:-4] + rid.to_bytes(4, "little")


def primary_group_dn(client, entry, base):
    sid = primary_group_sid(entry)
    # The group can live outside an account's configured OU search base.
    # Search the verified domain on the same DC, without following referrals.
    rows = client.search(base, all_of(equal("objectClass", "group"), equal("objectSid", sid)),
                         ["objectSid"], limit=2)
    if len(rows) != 1:
        raise MatchError("AD primary group did not resolve to one group; membership result is incomplete")
    group = rows[0]
    if not in_domain(group["dn"], base) or scalar(group, "objectSid") != sid:
        raise ProtocolError("Directory returned a different AD primary group")
    return group["dn"]


def all_direct_groups(client, entry, base):
    groups = direct_groups(client, entry)
    primary = primary_group_dn(client, entry, base)
    groups = sorted([dn for dn in groups if dn.casefold() != primary.casefold()] + [primary],
                    key=str.casefold)
    if len(groups) > MAX_VALUES:
        raise DirectoryError("Membership list exceeds configured client limit")
    return groups


def group_rows(entry, groups, kind, server, checked_at):
    group_identity = {"user_dn": entry["dn"]} if kind == "user" else {}
    # Connect stringifies nested lists. Emit one composite row per DN and
    # overwrite the complete list, never patch a cached membership snapshot.
    return [{"group_dns": group, "checked_at": checked_at, "server": "%s:%s" % server,
             **group_identity} for group in groups]


def account_properties(client, entry, kind, server, base, property_suffix=""):
    prefix = PREFIX + kind + "_"
    groups = all_direct_groups(client, entry, base) if property_suffix != "object" else None
    checked_at = int(time.time())
    if property_suffix == "group_details":
        return {prefix + "group_details": group_rows(entry, groups, kind, server, checked_at)}
    try:
        uac = int(scalar(entry, "userAccountControl"))
        expires = int(scalar(entry, "accountExpires"))
    except ValueError:
        raise ProtocolError("Invalid AD account state") from None
    if uac < 0 or not 0 <= expires <= 9223372036854775807:
        raise ProtocolError("AD account state is out of range")
    never = expires in (0, 9223372036854775807)
    epoch = (expires // 10000000) - 11644473600
    responding_server = "%s:%s" % server
    account = {"matched": True, "dn": entry["dn"],
              "match_confidence": entry["match_confidence"], "match_method": entry["match_method"],
              "guid": str(uuid.UUID(bytes_le=scalar(entry, "objectGUID"))),
              "disabled": bool(uac & 2),
              "expired": not never and expires <= 116444736000000000 + time.time_ns() // 100,
              "expiration_set": not never,
              "checked_at": checked_at, "server": responding_server}
    # Connect 2.0.7 parses composite dates as scalar epoch numbers. It rejects
    # both [] and [epoch]. The whole composite row is replaced on success;
    # omit an unset date instead of returning null or an invented timestamp.
    if not never:
        account["expiration"] = epoch
    properties = {prefix + "object": account}
    if property_suffix != "object":
        properties[prefix + "group_details"] = group_rows(entry, groups, kind, server, checked_at)
    return properties


def change_membership(client, entry, group_dn, add, base, expected_group_guid=None):
    if not in_domain(group_dn, base) or len(split_dn(group_dn)) <= len(split_dn(base)):
        raise DirectoryError("Group must be a full DN within the configured AD domain")
    try:
        groups = client.search(group_dn, equal("objectClass", "group"), ["objectGUID", "objectSid"], scope=0, limit=1)
    except LDAPError as error:
        if error.code == 32:
            raise MatchError("Specified group DN does not exist or is not visible to the bind account (LDAP code 32)") from None
        if error.code == 34:
            raise MatchError("Specified group DN is invalid (LDAP code 34)") from None
        raise
    if len(groups) != 1:
        raise MatchError("The specified group DN does not identify a visible AD group; it may be missing, unreadable, or not a group")
    group = groups[0]
    guid = scalar(group, "objectGUID")
    if len(guid) != 16:
        raise ProtocolError("Invalid group GUID")
    if expected_group_guid is not None and guid != expected_group_guid:
        raise MatchError("Recorded group was replaced; membership was not changed")
    change = {"group_dn": group["dn"], "group_guid": str(uuid.UUID(bytes_le=guid)), "changed": False}
    if scalar(group, "objectSid", required=False) == primary_group_sid(entry):
        if not add:
            raise DirectoryError("Cannot remove the account's AD primary group; changing primaryGroupID is not supported")
        change.update({"was_member": True, "status": "Already present (AD primary group)"})
        return change
    # Compare uses AD's own DN matching rules and doesn't enumerate a huge group.
    before = client.compare(group["dn"], "member", entry["dn"])
    change["was_member"] = before
    if before == add:
        change["status"] = "Already present" if add else "Already absent"
        return change
    # AD does not advertise RFC 4528's assertion control. Recheck both identities
    # immediately before a normal, single-value LDAP Modify on the full group DN.
    if not client.compare(group["dn"], "objectGUID", guid) or not client.compare(
            entry["dn"], "objectGUID", scalar(entry, "objectGUID")):
        raise DirectoryError("Account or group changed before the membership write")
    code = client.modify_member(group["dn"], entry["dn"], add)
    if client.compare(group["dn"], "member", entry["dn"]) != add:
        raise IndeterminateWrite("Membership modification was not verified on the same DC")
    # A duplicate-add / absent-delete race belongs to another writer, not us.
    change["changed"] = code == 0
    change["status"] = ("Added" if add else "Removed") if code == 0 else (
        "Already present" if add else "Already absent")
    return change


def undo_option(params):
    value = setting(params, "undo_on_cancel", True)
    if type(value) is bool:
        return value
    if isinstance(value, str) and value.strip().lower() in ("true", "false", "1", "0"):
        return value.strip().lower() in ("true", "1")
    if type(value) is int and value in (0, 1):
        return bool(value)
    raise DirectoryError("Undo when action cancelled must be true or false")


def authorized_group_dn(params, kind, requested_dn, domain):
    """Fail closed; changes use an explicitly configured DN, never a pattern."""
    if kind not in ("computer", "user"):
        raise DirectoryError("Invalid group action object type")
    base = ",".join("DC=" + label for label in domain.split("."))

    def key(dn):
        if not in_domain(dn, base) or len(split_dn(dn)) <= len(split_dn(base)):
            raise DirectoryError("Group must be a full DN within the configured AD domain")
        return tuple(part.casefold() for part in split_dn(dn))

    requested_key = key(requested_dn)
    allow_any = setting(params, kind + "_allow_any_group", False)
    if isinstance(allow_any, str) and allow_any.strip().lower() in ("true", "false", "1", "0"):
        allow_any = allow_any.strip().lower() in ("true", "1")
    elif type(allow_any) is int and allow_any in (0, 1):
        allow_any = bool(allow_any)
    if type(allow_any) is not bool:
        raise DirectoryError(kind.title() + " Allow any group must be explicitly true or false")
    if allow_any:
        return requested_dn
    raw = setting(params, kind + "_group_whitelist", "")
    if not isinstance(raw, str) or len(raw) > 65536:
        raise DirectoryError(kind.title() + " Group Whitelist must be text of at most 65536 characters")
    names = [line.strip() for line in raw.splitlines() if line.strip()]
    if not names:
        raise DirectoryError("%s Group Whitelist is empty and Allow any group is disabled; all group add/remove changes are blocked" % kind.title())
    if len(names) > 256:
        raise DirectoryError(kind.title() + " Group Whitelist exceeds 256 group DNs")
    allowed = {}
    for dn in names:
        allowed[key(dn)] = dn
    if requested_key not in allowed:
        raise DirectoryError("Group DN is not permitted by the %s Group Whitelist: %s" %
                             (kind.title(), requested_dn))
    # Resolve the administrator's configured DN, not a differently encoded
    # action-supplied string. AD remains authoritative about DN identity.
    return allowed[requested_key]


def saved_action(params, kind, action):
    raw = params.get("cookie")
    if raw is None or raw == "":
        return None
    if not isinstance(raw, str) or len(raw) > 32768:
        raise DirectoryError("Invalid group action cookie")
    try:
        saved = json.loads(raw)
        if not isinstance(saved, dict) or saved.get("schema") != "connectad-group-undo-v1":
            raise ValueError()
        if saved.get("kind") != kind or saved.get("operation") != action:
            raise ValueError()
        if any(type(saved.get(key)) is not bool for key in ("undo", "changed", "was_member")):
            raise ValueError()
        if saved["changed"] and saved["was_member"] != (action == "remove"):
            raise ValueError()
        if not isinstance(saved.get("domain"), str) or not re.fullmatch(
                r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", saved["domain"]):
            raise ValueError()
        for key in ("account_dn", "group_dn"):
            split_dn(saved.get(key))
        for key in ("account_guid", "group_guid"):
            saved[key] = str(record_guid({"guid": saved.get(key)}))
        server = saved.get("server")
        if (not isinstance(server, list) or len(server) != 2 or
                not isinstance(server[0], str) or not server[0] or len(server[0]) > 253 or
                type(server[1]) is not int or not 1 <= server[1] <= 65535):
            raise ValueError()
        return saved
    except (ValueError, RecursionError, DirectoryError):
        raise DirectoryError("Invalid or mismatched group action cookie; no membership changed") from None


def action_response(status, entry_dn="", group_dn="", server=""):
    return {"succeeded": True, "result_msg": status + (": " + group_dn if group_dn else ""),
            "properties": {PREFIX + "action_status": {
                "result": status, "reason": "", "time": int(time.time()), "object_dn": entry_dn,
                "group_dn": group_dn, "server": server}}}


def membership_cookie(config, server, entry, change, kind, action, undo):
    return json.dumps({"schema": "connectad-group-undo-v1", "domain": config["domain"],
                      "kind": kind, "operation": action, "undo": undo,
                      "changed": change["changed"], "was_member": change["was_member"],
                      "account_dn": entry["dn"],
                      "account_guid": str(uuid.UUID(bytes_le=scalar(entry, "objectGUID"))),
                      "group_dn": change["group_dn"], "group_guid": change["group_guid"],
                      "server": list(server)}, separators=(",", ":"))


def refresh_action_groups(response, client, params, entry, kind, config, base, server):
    """Read back after confirmed membership, without replaying a write on error."""
    try:
        # The initial account snapshot predates the action. Re-read the same
        # GUID on this connection, including renames and other writers' changes.
        fresh = resolve_entry(client, params, kind, config, base,
                              recorded_guid=scalar(entry, "objectGUID"))
        groups = all_direct_groups(client, fresh, base)
        response["properties"][PREFIX + kind + "_group_details"] = group_rows(
            fresh, groups, kind, server, int(time.time()))
    except Exception as error:
        # Membership is already verified and the undo cookie already exists.
        # Do not lose it, classify the write as unknown, or fail over/replay.
        message = str(error) if isinstance(error, DirectoryError) else "AD read failed or returned an unexpected response"
        warning = "Membership confirmed, but live Groups refresh failed: " + message
        response["result_msg"] += "; " + warning
        response["properties"][PREFIX + "action_status"]["reason"] = warning


def connection_failure(server, transport, error):
    """Keep TLS diagnostics without including bind parameters or LDAP payloads."""
    prefix = "%s:%s %s" % (server[0], server[1], {"ldaps": "LDAPS", "starttls": "StartTLS", "ldap": "LDAP"}[transport])
    if isinstance(error, ssl.SSLCertVerificationError):
        detail = " ".join(str(getattr(error, "verify_message", "") or error).split())[:400]
        message = prefix + " certificate validation failed: " + detail
        if getattr(error, "verify_code", None) == 3:
            message += "; Forescout requires the issuing CA's current CRL in its certificate/CRL store"
        return message
    if isinstance(error, ssl.SSLError):
        detail = " ".join(str(getattr(error, "reason", "") or error).split())[:400]
        return prefix + " TLS handshake failed: " + detail
    if isinstance(error, (socket.timeout, TimeoutError)):
        return prefix + " connection/protocol failure: timed out"
    return prefix + " connection/protocol failure"


def matched_object_guid(params, kind, config, property_tag):
    """Use the sole Groups dependency; never fall back to native identities."""
    label = kind.title() + " Object"
    if property_tag != PREFIX + kind + "_object":
        raise MatchError("Unexpected Groups dependency")
    record = params.get(property_tag)
    if record is None or record == "" or record == []:
        if kind == "user":
            raise NoUserIdentity("User Object is unavailable; no current AD user groups")
        raise MatchError(label + " is unavailable; resolve it before requesting Groups")
    if isinstance(record, str):
        if len(record) > 16384:
            raise MatchError(label + " composite is oversized")
        try:
            record = json.loads(record)
        except (ValueError, RecursionError):
            raise MatchError(label + " did not return a valid composite") from None
    if kind == "user" and empty_composite(record, {
            "matched": False, "match_confidence": "", "match_method": "", "dn": "", "guid": "",
            "disabled": False, "expired": False, "expiration_set": False, "expiration": 0,
            "checked_at": 0, "server": ""}):
        raise NoUserIdentity("User Object is empty; no current AD user groups")
    if not isinstance(record, dict) or record.get("matched") is not True:
        raise MatchError(label + " does not contain a successful match; resolve it before requesting Groups")
    try:
        guid = record_guid(record).bytes_le
    except MatchError:
        raise MatchError(label + " does not contain a valid objectGUID") from None
    expected_base = ",".join("DC=" + part for part in config["domain"].split("."))
    if not in_domain(record.get("dn"), expected_base):
        raise MatchError(label + " belongs to a different AD domain; resolve it for this connection")
    # Fresh GUID lookup below enforces object class and the current search base.
    # Do not use the old DN as the lookup key: the account may have been renamed.
    return guid


def configure_crl_check(params, context, transport):
    """Adjust only revocation flags on Connect's per-invocation TLS context."""
    if transport == "ldap" or context.verify_mode == ssl.CERT_NONE:
        return None
    value = setting(params, "check_crl", True)
    if isinstance(value, str) and value.strip().lower() in ("true", "false", "1", "0"):
        value = value.strip().lower() in ("true", "1")
    if type(value) is not bool:
        raise DirectoryError("Check certificate revocation (CRL) must be true or false")
    flags = int(context.verify_flags)
    if value:
        # Keep an existing full-chain check; at least the leaf must be checked.
        flags |= int(ssl.VERIFY_CRL_CHECK_LEAF)
    else:
        # CHECK_CHAIN includes CHECK_LEAF. Preserve every unrelated verify bit.
        flags &= ~int(ssl.VERIFY_CRL_CHECK_CHAIN)
    if context.verify_flags != flags:
        context.verify_flags = flags
    return value


def execute(params, tls_context, kind=None, action=None, guid_property="", cancel=False, action_context=None, property_suffix="", object_property=""):
    """One independent bounded operation. Never replay an uncertain write."""
    if action_context is None:
        action_context = {}
    saved = saved_action(params, kind, action) if action is not None else None
    if cancel and saved is not None:
        action_context["group_dn"] = saved["group_dn"]
    if cancel:
        if saved is None:
            # Failed starts have no cookie. Acknowledge their cancellation
            # without replacing the failed/unknown attempt and its reason.
            return {"succeeded": True, "result_msg": "Cancelled: no successful action cookie; no change made"}
        if not saved["undo"] or not saved["changed"]:
            status = "Cancelled: undo disabled; change retained" if not saved["undo"] else "Cancelled: original action made no change"
            return action_response(status, saved["account_dn"], saved["group_dn"])
    undo = undo_option(params) if action is not None and not cancel else False
    config = configuration(params)
    if saved is not None and saved["undo"] and saved["changed"] and saved["domain"].casefold() != config["domain"]:
        raise DirectoryError("Recorded action belongs to a different AD domain")
    if config["transport"] != "ldap" and tls_context is None:
        raise DirectoryError("TLS requires the ssl_context supplied by Forescout")
    if action is not None:
        requested_dn = saved["group_dn"] if cancel else setting(params, "group_dn")
        group_dn = authorized_group_dn(params, kind, requested_dn, config["domain"])
        action_context["group_dn"] = group_dn
    parent_guid = None
    if object_property:
        if action is not None or cancel or property_suffix != "group_details" or kind not in ("computer", "user"):
            raise MatchError("Object dependency is only supported for read-only Groups resolution")
        parent_guid = matched_object_guid(params, kind, config, object_property)
    elif kind is not None and not cancel:
        # Read-only computer discovery may recover from a failed collector.
        # Preserve the stricter computer evidence guard before membership writes.
        identity_filter(params, kind, config, guid_property, allow_computer_fallback=action is None)
    crl_enabled = configure_crl_check(params, tls_context, config["transport"])
    deadline = time.monotonic() + config["total_timeout"]
    servers = candidates(config, deadline)
    if cancel:
        # Read and undo on the DC that confirmed the original write. A different
        # replica may not yet contain it. Never connect to cookie-only targets.
        servers = [server for server in servers if server[0].casefold() == saved["server"][0].casefold()
                   and server[1] == saved["server"][1]]
        if not servers:
            raise DirectoryError("Original AD server is not in the current server configuration; undo not attempted")
    failures = []
    for server in servers:
        client = None
        # Keep only the current attempt's context. Account DN is recorded only
        # after a fresh resolution, never copied from an old undo cookie.
        action_context.update({"server": "%s:%s" % server, "object_dn": ""})
        try:
            client = Client(server, config, tls_context, deadline)
            base = domain_base(client, config)
            if kind is None:
                validation = ""
                if config["transport"] != "ldap":
                    validation = "; certificate validation " + ("disabled" if tls_context.verify_mode == ssl.CERT_NONE else "enabled")
                    if crl_enabled is not None:
                        validation += "; CRL checking " + ("enabled" if crl_enabled else "disabled")
                return {"succeeded": True, "result_msg": "Bound to %s:%s; AD domain verified; %s%s" %
                        (server[0], server[1], config["transport"], validation)}
            recorded_guid = uuid.UUID(saved["account_guid"]).bytes_le if cancel else parent_guid
            entry = resolve_entry(client, params, kind, config, base, guid_property, recorded_guid,
                                  allow_computer_fallback=action is None)
            if action is not None:
                action_context["object_dn"] = entry["dn"]
                owns_change = saved is not None and saved["undo"] and saved["changed"]
                if owns_change and scalar(entry, "objectGUID") != uuid.UUID(saved["account_guid"]).bytes_le:
                    raise MatchError("Cancel the existing group action before changing its account")
                expected_group = uuid.UUID(saved["group_guid"]).bytes_le if owns_change else None
                desired = saved["was_member"] if cancel else action == "add"
                change = change_membership(client, entry, group_dn, desired, base, expected_group)
                status = "Undone: " + change["status"] if cancel else change["status"]
                response = action_response(status, entry["dn"], change["group_dn"], "%s:%s" % server)
                if not cancel:
                    if owns_change:
                        # Preserve original ownership if Connect repeats a successful
                        # action and supplies its cookie; an idempotent retry must
                        # not replace an undoable change with a no-op record.
                        change.update({"changed": True, "was_member": saved["was_member"]})
                    response["cookie"] = membership_cookie(config, server, entry, change, kind, action, undo)
                refresh_action_groups(response, client, params, entry, kind, config, base, server)
                return response
            return {"properties": account_properties(client, entry, kind, server, base, property_suffix)}
        except LDAPError as error:
            if client is not None and client.write_confirmed:
                raise IndeterminateWrite("Membership write returned, but verification failed; re-read membership before retrying") from None
            if error.code not in (51, 52) or (client is not None and client.write_attempted):
                raise
            failures.append("%s:%s LDAP %s" % (server[0], server[1], error.code))
        except (OSError, TransportError, ssl.CertificateError, ProtocolError) as error:
            if client is not None and client.write_attempted:
                raise IndeterminateWrite("Write outcome unknown; verify membership before retrying. No failover write was sent") from None
            failures.append(connection_failure(server, config["transport"], error))
        finally:
            if client is not None:
                client.close()
    raise DirectoryError("No AD server completed the request: " + "; ".join(failures))


def run(params, tls_context, kind=None, action=None, guid_property="", cancel=False, property_suffix="", object_property=""):
    """Connect entrypoint: property failures never masquerade as healthy accounts."""
    action_context = {"object_dn": "", "group_dn": str(setting(params, "group_dn")), "server": ""}
    original_flags = None
    try:
        if tls_context is not None:
            original_flags = tls_context.verify_flags
        return execute(params, tls_context, kind, action, guid_property, cancel, action_context, property_suffix, object_property)
    except Exception as error:
        message = str(error) if isinstance(error, DirectoryError) else "Invalid configuration or unexpected directory response"
        # Do not return partial group/state values after failed or ambiguous reads.
        if kind is not None and action is None:
            if kind == "user" and isinstance(error, NoUserIdentity):
                # Resolve successfully to empty values. An error/omitted value
                # leaves old successful identities and Inventory memberships.
                # Clear Groups with Object: the core may not request a Groups
                # resolution when its Object dependency has become empty.
                properties = {PREFIX + "user_group_details": []}
                if property_suffix != "group_details":
                    properties[PREFIX + "user_object"] = {}
                return {"properties": properties}
            return {"error": message}
        result = {"succeeded": False, "result_msg": message}
        if action is not None:
            # Connect 2.0.7's normal ActionCallback logs succeeded but sends a
            # successful ActionReply even when false. An error key selects its
            # failure callback, which also publishes the supplied properties.
            result["error"] = message
            result["properties"] = {PREFIX + "action_status": {
                "result": "Unknown" if isinstance(error, IndeterminateWrite) else "Failed",
                "reason": message, "time": int(time.time()), **action_context}}
        return result
    finally:
        # Connect 2.0.7 creates this context for each invocation. Do not retain
        # altered flags if a caller reuses it, including after failed operations.
        # Chain trust, hostname checks, certificates, and TLS options are untouched.
        if original_flags is not None and tls_context.verify_flags != original_flags:
            tls_context.verify_flags = original_flags
