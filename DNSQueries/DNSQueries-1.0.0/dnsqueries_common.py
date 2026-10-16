"""Custom matcher and persistence helpers embedded into Connect handlers at build time."""

DNS_WINDOW = 7 * 86400
DNS_LIMIT = 20
DNS_BUCKET_SECONDS = 86400
DNS_BUCKET_COUNT = 8
DNS_CUSTOM_MAX_CANDIDATES = 64
DNS_CUSTOM_TOKENS = ("\\S+", "\\d+", "\\w+")
DNS_REGEX_META = set("\\.^$*+?{}[]()|")
DNS_CLEANUP_BUCKET = None


def dns_pattern(params):
    expression = params.get("connect_dnsqueries_regex", "") or ""
    if not expression:
        raise ValueError("Custom mode requires a query-only regular expression")
    if len(expression) > 2048:
        raise ValueError("Custom expression exceeds 2048 characters")
    if not expression.endswith("$"):
        raise ValueError("Custom expression must end with $")
    expression = expression[:-1]
    first_start = expression.find("(?P<")
    if first_start <= 0:
        raise ValueError("Custom expression needs a fixed query prefix")
    first_end = expression.find(")", first_start)
    second_start = expression.find("(?P<", first_end + 1)
    if first_end < 0 or second_start <= first_end:
        raise ValueError("Custom expression needs client_ip and domain named groups")
    second_end = expression.find(")", second_start)
    if second_end != len(expression) - 1:
        raise ValueError("Custom expression only permits two terminal named groups")
    prefix = expression[:first_start]
    middle = expression[first_end + 1:second_start]
    if not middle or any(char in DNS_REGEX_META for char in prefix + middle):
        raise ValueError("Custom expression only permits fixed text outside named groups")
    groups = []
    for start, end in ((first_start, first_end), (second_start, second_end)):
        group = expression[start + 4:end]
        if ">" not in group:
            raise ValueError("Invalid custom named group")
        name, token = group.split(">", 1)
        if name not in ("client_ip", "domain") or token not in DNS_CUSTOM_TOKENS:
            raise ValueError("Custom groups must use client_ip/domain with \\S+, \\d+, or \\w+")
        groups.append((name, token))
    if {groups[0][0], groups[1][0]} != {"client_ip", "domain"}:
        raise ValueError("Custom expression needs client_ip and domain named groups")
    return prefix, groups[0], middle, groups[1]


def dns_custom_character(token, character):
    if token == "\\S+":
        return not character.isspace()
    if token == "\\d+":
        return "0" <= character <= "9"
    return character.isalnum() or character == "_"


def dns_custom_value(message, start, end, token):
    if end <= start:
        return None
    value = message[start:end]
    return value if all(dns_custom_character(token, character) for character in value) else None


def dns_custom_fields(pattern, message):
    prefix, first_group, middle, second_group = pattern
    start = 0
    for unused in range(DNS_CUSTOM_MAX_CANDIDATES):
        found = message.find(prefix, start)
        if found < 0:
            return None
        middle_start = message.find(middle, found + len(prefix))
        if middle_start >= 0:
            first_value = dns_custom_value(message, found + len(prefix), middle_start, first_group[1])
            second_value = dns_custom_value(message, middle_start + len(middle), len(message), second_group[1])
            if first_value is not None and second_value is not None:
                return {first_group[0]: first_value, second_group[0]: second_value}
        start = found + 1
    return None


def dns_table(now):
    return "dns_events_{}".format(int(now // DNS_BUCKET_SECONDS) % DNS_BUCKET_COUNT)


def dns_bucket(now):
    return int(now // DNS_BUCKET_SECONDS)


def dns_key(bucket, ip, domain):
    return "{}|{}|{}".format(bucket, ip, domain)


def dns_tables(now, ip):
    bucket = dns_bucket(now)
    return [("dns_events_{}".format((bucket - offset) % DNS_BUCKET_COUNT), "{}|{}|".format(bucket - offset, ip)) for offset in range(DNS_BUCKET_COUNT)]


def dns_cleanup(db, now):
    bucket = dns_bucket(now)
    table = dns_table(now)
    for key in db.get_all_keys(table) or []:
        generation, separator, unused = key.partition("|")
        if not separator:
            continue
        try:
            if int(generation) >= bucket:
                continue
        except ValueError:
            continue
        try:
            db.delete(table, key)
        except KeyError:
            pass


def dns_maintain_bucket(db, now):
    global DNS_CLEANUP_BUCKET
    bucket = dns_bucket(now)
    if DNS_CLEANUP_BUCKET == bucket:
        return
    dns_cleanup(db, now)
    DNS_CLEANUP_BUCKET = bucket


def dns_snapshot(db, ip, now, add_domain=None):
    if add_domain is not None:
        dns_maintain_bucket(db, now)
        table = dns_table(now)
        key = dns_key(dns_bucket(now), ip, add_domain)
        if not db.save(table, key, str(now)):
            raise RuntimeError("DNS persistence write failed; no property update returned")
    newest = {}
    for table, prefix in dns_tables(now, ip):
        for key in db.get_all_keys(table) or []:
            if not key.startswith(prefix):
                continue
            raw = db.get(table, key)
            try:
                seen = float(raw)
            except (TypeError, ValueError):
                continue
            domain = key[len(prefix):]
            if now - DNS_WINDOW < seen:
                previous = newest.get(domain)
                if previous is None or seen > previous:
                    newest[domain] = seen
    selected = sorted(newest, key=lambda name: (-newest[name], name))[:DNS_LIMIT]
    return sorted(selected)